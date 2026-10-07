"""Independent review checks. Writes only results/codex_review/; cached models only.

python scripts/codex_review.py artifacts
python scripts/codex_review.py retrieval
python scripts/codex_review.py live
python scripts/codex_review.py metrics
python scripts/codex_review.py judge
python scripts/codex_review.py scoring
"""
import hashlib
import json
import os
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import mcqa
import eval as ev

OUT = ev.OUT / "codex_review"


def read(path):
    return [json.loads(s) for s in path.read_text(encoding="utf-8").splitlines() if s.strip()]


def save(name, obj):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def artifacts():
    pages = mcqa.load_pages()
    raw = read(mcqa.DATA / "pages.jsonl")
    qs = {n: read(ev.OUT / f"questions_{n}.jsonl") for n in ("retrieval", "answers", "tool", "tool_dev")}
    answers = read(ev.OUT / "answers.jsonl")
    summary = json.loads((ev.OUT / "answers_summary.json").read_text(encoding="utf-8"))
    # Recompute through the production functions into our separate output directory.
    old_out = ev.OUT
    try:
        ev.OUT = OUT
        ev.summarize_answers(answers)
    finally:
        ev.OUT = old_out
    new_summary = json.loads((OUT / "answers_summary.json").read_text(encoding="utf-8"))
    tool = json.loads((ev.OUT / "tool.json").read_text(encoding="utf-8"))
    tool_agree = all(x["correct"] == (ev.answer_number(x["answer"], x["question"]) == x["gold"]) for x in tool["rows"])
    mixed = [x for x in answers if ev.hedged(x["answer"]) and re.sub(
        r"(?i)\bi (?:do not|don't) know\b[.!]?", "", x["answer"]).strip()]
    out = {
        "scope": "Independent artifact checks; saved metrics are recomputed, not regenerated.",
        "corpus": {"stored_rows": len(raw), "missing_rows": sum(bool(p.get("missing")) for p in raw),
                   "distinct_pages": len(pages), "words": sum(len(p["text"].split()) for p in pages)},
        "question_counts": {n: len(q) for n, q in qs.items()},
        "retrieval_answers_question_overlap": len({x["question"] for x in qs["retrieval"]} &
                                                  {x["question"] for x in qs["answers"]}),
        "tool_dev_test_item_overlap": len({x["item"] for x in qs["tool"]} & {x["item"] for x in qs["tool_dev"]}),
        "answer_summary_matches": summary == new_summary,
        "tool_saved_scoring_matches": tool_agree,
        "answers_by_variant": dict(Counter(x["variant"] for x in answers)),
        "mixed_uncertainty_candidates": [{k: x[k] for k in ("question", "variant", "answer", "correct", "faithful")}
                                          for x in mixed],
        "recipe_version": mcqa.crafting_data()["version"],
        "recipe_counts": {n: len(mcqa.crafting_data()[n]) for n in ("recipes", "tags", "names")},
        "question_pool_sha256": hashlib.file_digest((mcqa.DATA / "qa_630k.parquet").open("rb"), "sha256").hexdigest(),
    }
    save("artifacts.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "mixed_uncertainty_candidates"}, indent=2), flush=True)
    print(f"Mixed uncertainty candidates: {len(mixed)}; inspect artifacts.json (candidate count is not a manual verdict).")


def metrics():
    from bert_score import score
    answers = read(ev.OUT / "answers.jsonl")
    picked = random.Random(7).sample(read(ev.OUT / "questions_answers.jsonl"), 12)
    wanted = {q["question"] for q in picked}
    rows = [x for x in answers if x["question"] in wanted]
    _, _, f1 = score([x["answer"] or "-" for x in rows], [x["reference"] for x in rows],
                     model_type="distilroberta-base", lang="en", rescale_with_baseline=True)
    scores = [{"question": x["question"], "variant": x["variant"], "saved": x["bertscore_f1"],
               "recomputed": round(v, 4)} for x, v in zip(rows, f1.tolist())]
    out = {"scope": "12 seed-7 saved questions x 3 variants; BERTScore recomputation using cached model on CPU.",
           "n": len(scores), "max_abs_difference": max(abs(x["saved"] - x["recomputed"]) for x in scores),
           "rows": scores}
    save("bertscore.json", out)
    print(f"Recomputed BERTScore for {len(scores)} answers; max difference {out['max_abs_difference']}", flush=True)


def judge():
    answers = read(ev.OUT / "answers.jsonl")
    wanted = {q["question"] for q in random.Random(7).sample(read(ev.OUT / "questions_answers.jsonl"), 4)}
    rows = []
    for x in (x for x in answers if x["question"] in wanted):
        verdict = ev.judge_correct(x)
        rows.append({"kind": "correctness_reproduction", "question": x["question"], "variant": x["variant"],
                     "reference": x["reference"], "answer": x["answer"], "saved": x["correct"], "recomputed": verdict})
        save("judge_rows.json", rows)
        print(f"Judge {len(rows)}/12: {x['variant']} {verdict.get('verdict')}", flush=True)
    # Deliberately bypass judge_faithful's abstention shortcut to inspect omitted factual claims.
    mixed = [x for x in answers if x["passages"] and ev.hedged(x["answer"]) and re.sub(
        r"(?i)\bi (?:do not|don't) know\b[.!]?", "", x["answer"]).strip()]
    for x in mixed:
        verdict = ev.ask_judge(ev.FAITHFUL_PROMPT.format(**x), ev.FAITHFUL_SCHEMA)
        rows.append({"kind": "omitted_claims_check", "question": x["question"], "variant": x["variant"],
                     "answer": x["answer"], "passages": x["passages"], "saved": x["faithful"], "recomputed": verdict})
        save("judge_rows.json", rows)
        print(f"Omitted faithfulness: {x['variant']} {verdict.get('verdict')}", flush=True)
    reproduced = [x for x in rows if x["kind"] == "correctness_reproduction"]
    summary = {"scope": "12 saved correctness verdicts regenerated; six mixed uncertainty answers checked for faithfulness. Automatic diagnostics, no human validation.",
               "n_correctness": len(reproduced), "same_verdict": sum(x["saved"]["verdict"] == x["recomputed"].get("verdict") for x in reproduced),
               "omitted_claims_verdicts": dict(Counter(x["recomputed"].get("verdict") for x in rows if x["kind"] == "omitted_claims_check"))}
    save("judge_summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)


def scoring():
    numeric = re.compile(r"\s*([0-9][0-9,]*)\s*(?:\[tool\])?\s*[.]?\s*$")
    summary, changed = {}, []
    for name in ("tool_run1_before_fix.json", "tool.json", "tool_dev.json"):
        obj = json.loads((ev.OUT / name).read_text(encoding="utf-8"))
        summary[name] = {}
        for use in (False, True):
            xs = [x for x in obj["rows"] if x["use_tool"] == use]
            strict = [bool((m := numeric.fullmatch(x["answer"])) and int(m[1].replace(",", "")) == x["gold"]) for x in xs]
            summary[name][str(use)] = {"n": len(xs), "saved_correct": sum(x["correct"] for x in xs), "strict_correct": sum(strict)}
            changed.extend({"file": name, "question": x["question"], "answer": x["answer"], "gold": x["gold"],
                            "saved_correct": x["correct"], "strict_correct": s} for x, s in zip(xs, strict) if s != x["correct"])
    out = {"method": "Strict numeric answer with optional [tool] citation; historical verbose true answers require separate semantic review.",
           "summary": summary, "changed_rows": changed}
    save("tool_scoring.json", out)
    print(json.dumps(summary, indent=2), flush=True)


def retrieval():
    t = time.perf_counter()
    model = mcqa.embedder()
    tokenizer = model.tokenizer
    count = lambda s: len(tokenizer.encode(s, add_special_tokens=False))
    checks = {}
    for size in ev.SIZES:
        saved = read(mcqa.DATA / f"chunks_{size}.jsonl")
        rebuilt = [c for p in mcqa.load_pages() for c in mcqa.chunk_page(p, size, count)]
        lengths = [len(x) for x in tokenizer([c["text"] for c in saved], truncation=False)["input_ids"]]
        emb = np.load(mcqa.DATA / f"emb_{size}.npy")
        checks[size] = {"chunks": len(saved), "rebuilt_equal": saved == rebuilt, "max_tokens": max(lengths),
                        "median_tokens": float(np.median(lengths)), "over_budget": sum(n > size for n in lengths),
                        "embedding_shape": list(emb.shape), "finite_embeddings": bool(np.isfinite(emb).all()),
                        "max_norm_error": float(np.max(np.abs(np.linalg.norm(emb, axis=1) - 1)))}
        print(f"Index check {size}: {checks[size]}", flush=True)
    r = mcqa.Retriever(256)
    # Re-encode a reproducible sample of passages to check saved index correspondence.
    sample_ids = random.Random(7).sample(range(len(r.chunks)), 24)
    rebuilt_emb = model.encode([r.chunks[i]["text"] for i in sample_ids], normalize_embeddings=True)
    embedding_error = float(np.max(np.abs(rebuilt_emb - r.emb[sample_ids])))
    qs = random.Random(7).sample(read(ev.OUT / "questions_retrieval.jsonl"), 100)
    save("questions_retrieval.json", qs)
    rows = []
    for i, q in enumerate(qs, 1):
        for variant in ev.VARIANTS:
            ids = r.search(q["question"], variant, 10)
            titles = [r.chunks[j]["title"] for j in ids]
            rank = titles.index(q["title"]) + 1 if q["title"] in titles else None
            rows.append({**q, "variant": variant, "rank": rank, "ids": ids, "titles": titles})
        if i % 10 == 0:
            save("retrieval_rows.json", rows)
            print(f"Independent retrieval: {i}/100", flush=True)
    res = {}
    for v in ev.VARIANTS:
        ranks = [x["rank"] for x in rows if x["variant"] == v]
        res[v] = {"n": len(ranks), "source_page_hit_at_1": sum(x == 1 for x in ranks),
                  "source_page_hit_at_5": sum(x is not None and x <= 5 for x in ranks),
                  "source_page_hit_at_10": sum(x is not None for x in ranks),
                  "mrr_at_10": sum(1 / x for x in ranks if x) / len(ranks)}
    out = {"scope": "100-question seed-7 subset of Claude's retrieval set, 256 tokens, all four variants; not a new held-out test.",
           "index_checks": checks, "sample_reencoded_passages": 24, "embedding_max_abs_error": embedding_error,
           "summary": res, "seconds": round(time.perf_counter() - t, 1)}
    save("retrieval.json", out)
    print(json.dumps(out, indent=2), flush=True)


def live():
    r = mcqa.Retriever(256)
    # Gold amounts written independently for simple, unambiguous main recipes; not computed using craft().
    cases = [("How many iron ingots do I need to craft 3 hoppers? Reply with the number only.", 15),
             ("How many sticks do I need to craft 10 torches? Reply with the number only.", 3),
             ("How many iron ingots do I need to craft 3 buckets? Reply with the number only.", 9),
             ("How many wooden planks do I need to craft 2 chests? Reply with the number only.", 16),
             ("How many milk buckets do I need to craft 2 cakes? Reply with the number only.", 6),
             ("How many iron ingots do I need to craft 2 iron pickaxes? Reply with the number only.", 6),
             ("How many iron blocks do I need to craft 2 anvils? Reply with the number only.", 6),
             ("How many wooden planks do I need to craft 3 crafting tables? Reply with the number only.", 12)]
    rows = []
    for q, gold in cases:
        for use_tool in (False, True):
            t = time.perf_counter()
            out = mcqa.answer(q, r, use_tool=use_tool)
            rows.append({"question": q, "gold": gold, "use_tool": use_tool, **out,
                         "first_number_correct": ev.answer_number(out["answer"], q) == gold,
                         "seconds": round(time.perf_counter() - t, 2)})
            save("live_rows.json", rows)
            print(f"Craft {len(rows)}/16 tool={use_tool} gold={gold}: {out['answer']}", flush=True)
    qualitative = ["How much iron does a hopper need?",
                   "How do I craft a cake in Java Edition 26.3?",
                   "What happens if I sleep in a bed in the Nether?",
                   "Does every mob drop experience when killed?",
                   "What happens to a Totem of Undying after it saves me?",
                   "Who won the 2022 FIFA World Cup?"]
    for q in qualitative:
        t = time.perf_counter()
        out = mcqa.answer(q, r)
        rows.append({"question": q, "kind": "qualitative_spot_check", **out,
                     "seconds": round(time.perf_counter() - t, 2)})
        save("live_rows.json", rows)
        print(f"QA: {q}\n{out['answer']}", flush=True)
    summary = {str(v): {"n": 8, "first_number_correct": sum(x["first_number_correct"] for x in rows
                                                             if x.get("use_tool") == v),
                       "tool_called": sum(bool(x["tool_calls"]) for x in rows if x.get("use_tool") == v)}
               for v in (False, True)}
    save("live_summary.json", {"scope": "Eight independent simple recipe questions, paired tool/no-tool; six qualitative demo questions. Small diagnostic set, no population accuracy claim.",
                               "summary": summary})
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    {"artifacts": artifacts, "retrieval": retrieval, "live": live, "metrics": metrics, "judge": judge, "scoring": scoring}[sys.argv[1]]()
