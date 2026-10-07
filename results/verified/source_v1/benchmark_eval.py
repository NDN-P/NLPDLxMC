"""Evaluate the source-grounded Java benchmark without replacing historical experiments.

python scripts/benchmark_eval.py validate
python scripts/benchmark_eval.py run --split dev
python scripts/benchmark_eval.py run --split test
python scripts/benchmark_eval.py report --split test
Uses cached Hugging Face models and local Ollama. Resumes completed question/variant rows.
"""
import argparse
import csv
import hashlib
import json
import os
import platform
import sys
import time
from collections import Counter
from pathlib import Path
import urllib.request

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import mcqa
import eval as ev

DATASET = ROOT / "data" / "java_benchmark.jsonl"


def read(path):
    return [json.loads(s) for s in path.read_text(encoding="utf-8").splitlines() if s.strip()] if path.exists() else []


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def digest(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def normal(text):
    return " ".join(text.casefold().split())


def evidence_rank(question, retrieved):
    gold = normal(question.get("evidence", ""))
    return next((j for j, c in enumerate(retrieved, 1) if gold and c["title"] == question["title"]
                 and gold in normal(c["text"])), None)


def validate():
    qs = read(DATASET)
    if not qs:
        raise ValueError("benchmark is missing or empty")
    pages = {p["title"]: p for p in mcqa.load_pages()}
    ids, questions = set(), set()
    for q in qs:
        if q["id"] in ids or q["question"] in questions:
            raise ValueError("duplicate benchmark ID/question")
        ids.add(q["id"])
        questions.add(q["question"])
        if q["split"] not in ("dev", "test") or q["kind"] not in ("answerable", "unanswerable", "out_of_scope"):
            raise ValueError("invalid benchmark split/kind")
        if q["edition"] != "Java" or q["version"] != mcqa.MC_VERSION or q["human_reviewed"]:
            raise ValueError("scope or provenance mismatch; human review must be recorded separately")
        if not q["reference_answer"]:
            raise ValueError("empty reference")
        if q["kind"] == "answerable":
            p = pages[q["title"]]
            if p["revid"] != q["revid"] or not q["evidence"] or q["evidence"] not in p["text"]:
                raise ValueError(f"source quote/revision mismatch: {q['id']}")
    sources = {s: {q["title"] for q in qs if q["split"] == s and q["kind"] == "answerable"} for s in ("dev", "test")}
    if sources["dev"] & sources["test"]:
        raise ValueError("answerable source pages overlap between dev and test")
    return qs


def config():
    from huggingface_hub import snapshot_download
    tags = json.load(urllib.request.urlopen("http://localhost:11434/api/tags", timeout=10))["models"]
    model = next(m for m in tags if m["name"] == mcqa.LLM)
    return {"dataset_sha256": digest(DATASET), "mcqa_sha256": digest(ROOT / "mcqa.py"),
            "eval_sha256": digest(ROOT / "eval.py"), "evaluator_sha256": digest(Path(__file__)),
            "chunks_sha256": digest(mcqa.DATA / f"chunks_{mcqa.DEFAULT_SIZE}.jsonl"),
            "generator": mcqa.LLM, "generator_digest": model["digest"], "judge": ev.JUDGE_MODEL,
            "embedding": mcqa.EMBED_MODEL, "reranker": mcqa.RERANK_MODEL, "chunk_size": mcqa.DEFAULT_SIZE,
            "hf_model_revisions": {m: Path(snapshot_download(m, local_files_only=True)).name
                                   for m in (mcqa.EMBED_MODEL, mcqa.RERANK_MODEL, "distilroberta-base")},
            "python": platform.python_version(), "variants": list(ev.VARIANTS_QA), "use_tool": False,
            "provenance": "AI-curated questions with exact pinned source quotes; not independent human validation"}


def run(split):
    qs = [q for q in validate() if q["split"] == split]
    out = ROOT / "results" / "verified" / split
    out.mkdir(parents=True, exist_ok=True)
    cfg = config()
    if (out / "config.json").exists() and json.loads((out / "config.json").read_text(encoding="utf-8")) != cfg:
        raise ValueError("Run configuration changed. Preserve this directory and start a separately named run.")
    write(out / "config.json", cfg)
    write(out / "questions.json", qs)
    rows = read(out / "answers.jsonl")
    done = {(x["id"], x["variant"]) for x in rows}
    r = mcqa.Retriever(mcqa.DEFAULT_SIZE)
    with (out / "answers.jsonl").open("a", encoding="utf-8") as f:
        for q in qs:
            for variant in ev.VARIANTS_QA:
                if (q["id"], variant) in done:
                    continue
                t = time.perf_counter()
                result = mcqa.answer(q["question"], None if variant == "none" else r, variant, use_tool=False)
                row = {**q, "reference": q["reference_answer"], "variant": variant, **result}
                row["refused"], row["hedged"] = ev.refused(row["answer"]), ev.hedged(row["answer"])
                row["correct"] = ev.judge_correct(row) if q["kind"] == "answerable" else None
                row["faithful"] = ev.judge_faithful(row)
                if variant != "none":
                    ids = r.search(q["question"], variant, 10)
                    row["retrieved"] = [{"id": i, **r.chunks[i]} for i in ids]
                    # Entire quoted supporting evidence must appear in a retrieved passage, not merely its source page.
                    row["evidence_rank"] = evidence_rank(q, [r.chunks[i] for i in ids])
                else:
                    row["retrieved"], row["evidence_rank"] = [], None
                row["seconds"] = round(time.perf_counter() - t, 2)
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                f.flush()
                rows.append(row)
                print(f"{split}: {len(rows)}/{len(qs) * 3} {q['id']} {variant}: {row['answer'][:130]}", flush=True)
    from bert_score import score
    _, _, f1 = score([x["answer"] or "-" for x in rows], [x["reference"] for x in rows],
                     model_type="distilroberta-base", lang="en", rescale_with_baseline=True)
    for x, value in zip(rows, f1.tolist()):
        x["bertscore_f1"] = round(value, 4)
    (out / "answers.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8")
    report(split)


def summarize(rows):
    res = {}
    for variant in ev.VARIANTS_QA:
        xs = [x for x in rows if x["variant"] == variant]
        positive = [x for x in xs if x["kind"] == "answerable"]
        negative = [x for x in xs if x["kind"] != "answerable"]
        labels = Counter(x["correct"].get("verdict") for x in positive)
        faithful = Counter(x["faithful"].get("verdict") for x in xs if x["faithful"] is not None)
        valid = sum(faithful[v] for v in ("supported", "partly", "unsupported"))
        res[variant] = {"answerable_n": len(positive), "correct": labels["correct"], "partial": labels["partial"],
                        "incorrect": labels["incorrect"], "judge_unparsed": labels[None],
                        "judge_correct_ci_percent": ev.wilson(labels["correct"], len(positive)),
                        "score": ev.mean(ev.points(x) for x in positive),
                        "bertscore_f1_answerable": ev.mean(x["bertscore_f1"] for x in positive),
                        "answerable_refused": sum(x["refused"] for x in positive), "hedged": sum(x["hedged"] for x in xs),
                        "negative_n": len(negative), "negative_correct_refusal": sum(x["refused"] for x in negative),
                        "faithful_attempted": sum(faithful.values()), "faithful_valid": valid,
                        "faithful_unparsed": faithful[None], "supported": faithful["supported"],
                        "evidence_hit_at_5": sum(x["evidence_rank"] is not None and x["evidence_rank"] <= 5 for x in positive)}
    positives = [x for x in rows if x["kind"] == "answerable"]
    common = {x["id"] for x in positives if x["variant"] == "dense" and not x["refused"]} & {
        x["id"] for x in positives if x["variant"] == "rerank" and not x["refused"]}
    return {"variants": res, "paired_answerable": ev.paired_differences(positives),
            "common_answered_n": len(common), "common_answered_bertscore": {
                v: ev.mean(x["bertscore_f1"] for x in positives if x["id"] in common and x["variant"] == v)
                for v in ev.VARIANTS_QA}}


def report(split):
    out = ROOT / "results" / "verified" / split
    rows = read(out / "answers.jsonl")
    expected = len([q for q in validate() if q["split"] == split]) * 3
    if len(rows) != expected or any("bertscore_f1" not in x for x in rows):
        raise ValueError("Incomplete run; resume `run` before reporting")
    summary = summarize(rows)
    write(out / "summary.json", summary)
    lines = [f"# Source-grounded Java benchmark — {split}", "",
             "AI-curated and source-checked, awaiting independent team review. This is not human-certified accuracy.", "",
             "Correctness and BERTScore below cover answerable questions only. Expected refusals are measured separately.", "",
             "| Variant | Correct | Partial | Refused answerable | BERTScore F1 | Evidence in top 5 | Correct negative refusal |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for v, s in summary["variants"].items():
        lines.append(f"| {v} | {s['correct']}/{s['answerable_n']} | {s['partial']} | {s['answerable_refused']} | "
                     f"{s['bertscore_f1_answerable']} | {s['evidence_hit_at_5']}/{s['answerable_n']} | "
                     f"{s['negative_correct_refusal']}/{s['negative_n']} |")
    lines += ["", "Paired differences on the same answerable questions (95% bootstrap intervals):", "",
              "| Comparison | Mean | 95% CI |", "|---|---:|---|"]
    for key, value in summary["paired_answerable"].items():
        lines.append(f"| {key} | {value['mean_difference']} | {value['ci95']} |")
    lines += ["", f"Common questions answered by dense and rerank: {summary['common_answered_n']}; BERTScore: "
              f"{summary['common_answered_bertscore']}.", "", "Faithfulness counts (supported / valid, unparsed):"]
    for v, s in summary["variants"].items():
        lines.append(f"- {v}: {s['supported']}/{s['faithful_valid']}, {s['faithful_unparsed']} unparsed.")
    lines += ["", "Evidence-hit counts require the entire curated quote in a top-five passage from the cited page. "
              "They are conservative for alternate valid passages and evidence spanning chunk boundaries.",
              "", "All judgments are automatic; generator and judge share a model. See config.json, answers.jsonl and human_check.csv."]
    (out / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with (out / "human_check.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "kind", "question", "reference", "evidence", "source_url", "variant", "answer", "human_verdict", "notes"])
        for x in rows:
            w.writerow([x.get(k, "") for k in ("id", "kind", "question", "reference", "evidence", "source_url", "variant", "answer")] + ["", ""])
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "run", "report"))
    parser.add_argument("--split", choices=("dev", "test"), default="test")
    args = parser.parse_args()
    if args.command == "validate":
        qs = validate()
        print(f"Validated {len(qs)} questions, exact source quotes and disjoint dev/test pages.")
    elif args.command == "run":
        run(args.split)
    else:
        report(args.split)
