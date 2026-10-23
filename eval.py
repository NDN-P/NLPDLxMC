"""Ablation study and evaluation. Every result is saved in results/.

    python eval.py retrieval   # Recall@k and MRR for each retrieval variant and chunk size (no LLM needed)
    python eval.py misses      # the retrieval questions the final system misses (for the failure analysis)
    python eval.py answers     # BERTScore + LLM-as-Judge: no retrieval vs dense vs hybrid+rerank (needs Ollama)
    python eval.py summary     # recompute saved summaries; newly included claims may need Ollama judging
    python eval.py judgecheck  # agreement of the LLM judges with hand labels (results/*_labels_*.jsonl)
    python eval.py tooldev     # crafting questions used to tune the tool prompts (needs Ollama)
    python eval.py tool        # held-out crafting questions with and without the craft tool (needs Ollama)
    python eval.py rescore     # score the saved tool runs again with the current answer parser (no LLM needed)
    python eval.py report      # results/RESULTS.md from the saved JSON files
"""
import csv
import json
import math
import random
import re
import sys
from collections import Counter
from pathlib import Path

import mcqa

OUT = Path(__file__).resolve().parent / "results"
SIZES = [128, 256, 512]
VARIANTS = ["dense", "bm25", "hybrid", "rerank"]
SEED = 0


def save(name, obj):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")


def load(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def save_questions(name, qs):
    """The exact evaluation questions, one JSON object per line, so the set can be inspected and reused."""
    OUT.mkdir(exist_ok=True)
    with (OUT / f"questions_{name}.jsonl").open("w", encoding="utf-8") as f:
        for q in qs:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")


def write_check_sheet(path, header, rows):
    """Create a grading sheet once; never erase the team's existing annotations."""
    try:
        f = path.open("x", encoding="utf-8-sig", newline="")
    except FileExistsError:
        return
    with f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def wilson(k, n, z=1.96):
    """95% Wilson interval for k successes out of n, in percent."""
    p, d = k / n, 1 + z * z / n
    c, h = p + z * z / (2 * n), z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round(max(0.0, 100 * (c - h) / d), 1), round(min(100.0, 100 * (c + h) / d), 1)]  # no "-0.0"


def questions(n, seed=SEED, exclude=()):
    """n distinct pool questions whose source page is in the corpus. The pool is synthetic (generated from the
    wiki), so its answers are only imperfect references; the source page is the retrieval label."""
    m = mcqa.source_to_title()
    qa = mcqa.qa_frame()
    qa = qa[qa["source"].isin(m) & ~qa["question"].isin(set(exclude))]
    qa = qa.drop_duplicates("question").sample(n=n, random_state=seed)
    return [{"question": r.question, "reference": r.answer, "title": m[r.source]} for r in qa.itertuples()]


# ---------- retrieval ablation ---------------------------------------------------------------------------------------

def retrieval(n=1000):
    qs, results = questions(n), {}
    save_questions("retrieval", qs)
    for size in SIZES:
        r = mcqa.Retriever(size)
        for v in VARIANTS:
            ranks = []
            for q in qs:
                titles = [r.chunks[i]["title"] for i in r.search(q["question"], v, 10)]
                ranks.append(titles.index(q["title"]) + 1 if q["title"] in titles else None)
            hits = {k: sum(1 for x in ranks if x and x <= k) for k in (1, 5, 10)}
            results[f"{v}@{size}"] = {
                "variant": v, "size": size, "n": n, "chunks": len(r.chunks),
                **{f"recall@{k}": round(100 * h / n, 1) for k, h in hits.items()},
                "recall@5_ci": wilson(hits[5], n),
                "mrr@10": round(sum(1 / x for x in ranks if x) / n, 3)}
            print(results[f"{v}@{size}"], flush=True)
    save("retrieval.json", {"seed": SEED, "label": "the chunk comes from the page the question was generated from",
                            "results": results})


def misses():
    """The retrieval questions the final system (rerank, DEFAULT_SIZE) misses in its top 5, with what it found instead."""
    r, rows = mcqa.Retriever(mcqa.DEFAULT_SIZE), []
    for q in questions(1000):
        ids = r.search(q["question"], "rerank", 5)
        found = [f"{r.chunks[i]['title']} > {r.chunks[i]['section']}" for i in ids]
        if q["title"] not in [r.chunks[i]["title"] for i in ids]:
            rows.append({**q, "retrieved": found})
    with (OUT / "retrieval_misses.jsonl").open("w", encoding="utf-8") as f:
        for x in rows:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"{len(rows)} of 1000 questions missed in the top 5")


# ---------- answer quality -------------------------------------------------------------------------------------------

JUDGE_MODEL = mcqa.LLM  # the only judge that agreed with hand labels on all three variants alike (results/judge_*)
VARIANTS_QA = ("none", "dense", "rerank")
# Decomposed prompts: the model first writes down the fact, then decides. A one-step 1-5 score from the same model
# called 87 of 100 closed-book answers correct, many of them plainly wrong (results/answers_run1_*).
CORRECT_PROMPT = """You check whether a system's answer to a Minecraft question agrees with a reference answer.

Question: {question}
Reference answer: {reference}
System answer: {answer}

Work in three steps and reply with JSON:
1. "reference_fact": the key fact the reference answer gives, in a few words.
2. "answer_claim": what the system answer claims about that fact, in a few words ("nothing" if it does not know or
   only says the thing does not exist).
3. "verdict":
   - "correct" if the answer claim matches the reference fact,
   - "partial" if it matches only part of it,
   - "incorrect" if it is different, contradicts it, or is "nothing".
Use only the reference answer as the truth, not your own knowledge of Minecraft."""
CORRECT_SCHEMA = {"type": "object", "required": ["reference_fact", "answer_claim", "verdict"], "properties": {
    "reference_fact": {"type": "string"}, "answer_claim": {"type": "string"},
    "verdict": {"type": "string", "enum": ["correct", "partial", "incorrect"]}}}
FAITHFUL_PROMPT = """You check whether an answer is supported by the passages it was written from.

Passages:
{passages}

Answer: {answer}

Work in three steps and reply with JSON:
1. "claims": the factual claims the answer makes, in a few words each (ignore the [n] citation marks).
2. "unsupported": the claims that the passages do not state or clearly imply ("none" if every claim is supported).
3. "verdict": "supported" if every claim is supported, "partly" if some are not, "unsupported" if the main claim
   is not supported.
Use only the passages, not your own knowledge of Minecraft."""
FAITHFUL_SCHEMA = {"type": "object", "required": ["claims", "unsupported", "verdict"], "properties": {
    "claims": {"type": "string"}, "unsupported": {"type": "string"},
    "verdict": {"type": "string", "enum": ["supported", "partly", "unsupported"]}}}
POINTS = {"correct": 1.0, "partial": 0.5, "incorrect": 0.0}


def refused(answer):
    """A pure refusal: the answer is only "I do not know." (an answer that makes claims and then hedges is not one;
    the first version counted those as abstentions and skipped their faithfulness check)."""
    text = re.sub(r"\[[^\]]*\]", "", answer or "").lower().replace("\u2019", "'")
    text = re.sub(r"[^a-z' ]", " ", text)
    return " ".join(text.split()) in ("i do not know", "i don't know")


def hedged(answer):
    """Makes claims but also says it does not know part of the answer."""
    return not refused(answer) and ("do not know" in answer.lower() or "don't know" in answer.lower())


def ask_judge(prompt, schema):
    for _ in range(2):
        msg = mcqa.chat([{"role": "user", "content": prompt}], fmt=schema, model=JUDGE_MODEL)
        try:
            obj = json.loads(msg["content"])
            if (isinstance(obj, dict) and all(isinstance(obj.get(k), str) for k in schema["required"])
                    and obj.get("verdict") in schema["properties"]["verdict"]["enum"]):
                return obj
        except (ValueError, KeyError, TypeError):
            pass
    return {"verdict": None, "error": "invalid judge response after two attempts"}


def judge_correct(row):
    return ask_judge(CORRECT_PROMPT.format(**row), CORRECT_SCHEMA)


def judge_faithful(row):
    """Every answer written from passages, except a pure refusal (it makes no claim to check)."""
    if not row["passages"] or refused(row["answer"]):
        return None
    return ask_judge(FAITHFUL_PROMPT.format(**row), FAITHFUL_SCHEMA)


def answers(n=100):
    r = mcqa.Retriever(mcqa.DEFAULT_SIZE)
    # held out from the retrieval questions, which were used to choose the chunk size
    rows, qs = [], questions(n, seed=SEED + 1, exclude=[q["question"] for q in questions(1000)])
    save_questions("answers", qs)
    for i, q in enumerate(qs):
        for v in VARIANTS_QA:
            out = mcqa.answer(q["question"], None if v == "none" else r, v, k=5, use_tool=False)
            row = {**q, "variant": v, "answer": out["answer"], "passages": out["passages"], "sources": out["sources"]}
            row["refused"], row["hedged"] = refused(row["answer"]), hedged(row["answer"])
            row["correct"] = judge_correct(row)
            row["faithful"] = judge_faithful(row)
            rows.append(row)
        print(f"{i + 1}/{n}", flush=True)
    from bert_score import score
    _, _, f1 = score([x["answer"] or "-" for x in rows], [x["reference"] for x in rows],
                     model_type="distilroberta-base", lang="en", rescale_with_baseline=True)
    for x, f in zip(rows, f1.tolist()):
        x["bertscore_f1"] = round(f, 4)
    with (OUT / "answers.jsonl").open("w", encoding="utf-8") as f:
        for x in rows:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    summarize_answers(rows)
    # answers with the judge's verdicts for the team to grade by hand (how far can the LLM judge be trusted?)
    sample = random.Random(SEED).sample(rows, 45)
    write_check_sheet(OUT / "judge_check.csv",
                      ["question", "reference", "variant", "answer", "judge_verdict", "judge_reference_fact",
                       "judge_answer_claim", "human_verdict (correct / partial / incorrect)"],
                      ([x["question"], x["reference"], x["variant"], x["answer"], x["correct"].get("verdict"),
                        x["correct"].get("reference_fact"), x["correct"].get("answer_claim"), ""] for x in sample))


def mean(vals):
    vals = list(vals)
    return round(sum(vals) / len(vals), 3) if vals else None


def factual_verdict(x):
    """A bare refusal contains no factual answer, even when an automatic judge disagrees."""
    return "incorrect" if refused(x["answer"]) else x["correct"].get("verdict")


def points(x):
    return POINTS.get(factual_verdict(x), 0.0)


def summarize_answers(rows):
    summary = {}
    for v in VARIANTS_QA:
        xs = [x for x in rows if x["variant"] == v]
        answered = [x for x in xs if not x["refused"]]
        n = len(xs)
        verdicts = Counter(factual_verdict(x) for x in xs)
        faithful = Counter(x["faithful"].get("verdict") for x in xs if x["faithful"])
        attempted = sum(faithful.values())
        checked = attempted - faithful[None]  # only parsed verdicts count
        summary[v] = {
            "n": n, "refused": n - len(answered), "hedged": sum(x["hedged"] for x in xs),
            "correct": verdicts["correct"], "partial": verdicts["partial"], "incorrect": verdicts["incorrect"],
            "unparsed": n - verdicts["correct"] - verdicts["partial"] - verdicts["incorrect"],
            "correct_pct": round(100 * verdicts["correct"] / n, 1), "correct_ci": wilson(verdicts["correct"], n),
            "score": mean(points(x) for x in xs),
            "bertscore_f1": mean(x["bertscore_f1"] for x in xs),
            # among the questions the variant did answer (a refusal is never "correct" but is not a wrong claim)
            "answered": len(answered),
            "correct_of_answered_pct": round(100 * sum(x["correct"].get("verdict") == "correct" for x in answered)
                                             / len(answered), 1) if answered else None,
            "bertscore_f1_answered": mean(x["bertscore_f1"] for x in answered),
            "faithful_attempted": attempted, "faithful_unparsed": faithful[None], "faithful_checked": checked,
            "supported": faithful["supported"], "partly": faithful["partly"], "unsupported": faithful["unsupported"],
            "supported_pct": round(100 * faithful["supported"] / checked, 1) if checked else None}
    save("answers_summary.json", {
        "seed": SEED + 1, "chunk_size": mcqa.DEFAULT_SIZE, "generator": mcqa.LLM, "judge_model": JUDGE_MODEL,
        "bertscore_model": "distilroberta-base (rescaled with baseline)",
        "score": "correct = 1, partial = 0.5, incorrect = 0, averaged over all questions", "summary": summary,
        "paired": paired_differences(rows)})


def paired_differences(rows, pairs=(("rerank", "dense"), ("rerank", "none"), ("dense", "none")), b=2000):
    """Every variant answers the same questions, so differences are measured per question (paired) with a 95%
    bootstrap interval over questions: much tighter than comparing two separate intervals."""
    by_q = {}
    for x in rows:
        by_q.setdefault(x["question"], {})[x["variant"]] = x
    qs = sorted(by_q)
    out = {}
    for a, c in pairs:
        for metric, f in (("score", points), ("bertscore_f1", lambda x: x["bertscore_f1"])):
            d = [f(by_q[q][a]) - f(by_q[q][c]) for q in qs]
            rng = random.Random(SEED)
            boot = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(b))
            out[f"{a} - {c}: {metric}"] = {"mean_difference": round(sum(d) / len(d), 3),
                                          "ci95": [round(boot[int(0.025 * b)], 3), round(boot[int(0.975 * b) - 1], 3)]}
    return out


def summary_only():
    """Recompute results/answers_summary.json from the saved results/answers.jsonl without generating answers again.
    Refusals are re-classified from the answer text, and answers that were never checked for faithfulness (hedged
    answers, skipped by the first classifier) are judged now, which needs Ollama."""
    path = OUT / "answers.jsonl"
    rows = [json.loads(line) for line in path.open(encoding="utf-8")]
    for x in rows:
        x.pop("abstained", None)
        x["refused"], x["hedged"] = refused(x["answer"]), hedged(x["answer"])
        if x.get("faithful") is None and x["passages"] and not x["refused"]:
            x["faithful"] = judge_faithful(x)
    with path.open("w", encoding="utf-8") as f:
        for x in rows:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    summarize_answers(rows)


# ---------- how far can the judge be trusted? ------------------------------------------------------------------------

def judgecheck():
    """Agreement of the two judges with hand labels: correctness (results/judge_labels_*.jsonl) and faithfulness
    (results/faithful_labels_*.jsonl)."""
    out = {}
    for path in sorted(OUT.glob("judge_labels_*.jsonl")) + sorted(OUT.glob("faithful_labels_*.jsonl")):
        rows = [json.loads(line) for line in path.open(encoding="utf-8")]
        faithful = path.name.startswith("faithful")
        pred = [((judge_faithful(x) or {}) if faithful else judge_correct(x)).get("verdict") for x in rows]
        gold = [x["label"] for x in rows]
        top = "supported" if faithful else "correct"
        agree = sum(p == g for p, g in zip(pred, gold))
        per = {v: f"{sum(p == g for p, g, x in zip(pred, gold, rows) if x['variant'] == v)}"
                  f"/{sum(x['variant'] == v for x in rows)}" for v in VARIANTS_QA if any(x["variant"] == v for x in rows)}
        out[path.name] = {"judge": "faithfulness" if faithful else "correctness", "n": len(rows),
                          "labelled_by": rows[0].get("labelled_by"), "exact_agreement": agree,
                          "top_label": top, "top_vs_not_agreement": sum((p == top) == (g == top) for p, g in zip(pred, gold)),
                          "cohen_kappa": kappa(gold, pred), "per_variant": per,
                          "confusion (label -> judge)": dict(Counter(f"{g} -> {p}" for g, p in zip(gold, pred)))}
        print(path.name, out[path.name], flush=True)
    save("judge_validation.json", {"judge_model": JUDGE_MODEL, "results": out})


def kappa(a, b):
    """Cohen's kappa: agreement corrected for the agreement two raters would reach by chance."""
    n, labels = len(a), set(a) | set(b)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0


# ---------- crafting tool ablation -----------------------------------------------------------------------------------

def tool_questions(n=40, seed=SEED, dev=False):
    """Quantity questions for items with exactly one crafting recipe; the gold number is computed from Mojang's
    recipe file: ceil(count / items per craft) * that ingredient's slots per craft.
    dev=True gives questions about other items (for tuning the prompt) that never overlap the test items."""
    data = mcqa.crafting_data()
    names = data["names"]
    cands = []
    for iid, opts in sorted(data["recipes"].items()):
        concrete = sorted({x for x in opts[0]["slots"] if not x.startswith("#") and x in names})
        if len(opts) == 1 and iid in names and concrete:
            cands.append((iid, opts[0], concrete))
    rng = random.Random(seed)
    picked = test = rng.sample(cands, n)
    if dev:
        rng = random.Random(seed + 100)
        picked = rng.sample([c for c in cands if c not in test], n)
    qs = []
    for iid, r, concrete in picked:
        ing, want = rng.choice(concrete), rng.randint(2, 16)
        gold = Counter(r["slots"])[ing] * math.ceil(want / r["makes"])
        qs.append({"question": f"How many {names[ing]} do I need to craft {want} {names[iid]}? "
                               "Reply with the number only.", "gold": gold, "item": iid})
    return qs


def answer_number(answer, question):
    """The amount the answer gives for the ingredient asked about, or None. Accepts a bare number ("12", "12 [tool]")
    or a number written right before the ingredient's name ("you need 15 iron ingots"). The first version took the
    first number anywhere, which counted refusals that repeat the requested count ("I do not know how many ... to
    craft 2 ...") as correct (results/tool_run1_before_fix.json)."""
    text = re.sub(r"\[[^\]]*\]", " ", answer or "").strip().lower()
    if refused(text) or "do not know" in text or "don't know" in text:
        return None
    if re.fullmatch(r"\d[\d,]*\.?", text):
        return int(text.rstrip(".").replace(",", ""))
    m = re.match(r"how many (.+?) do i need to craft", question.lower())
    name = re.escape(m.group(1)) if m else r"\w+"
    amounts = set()
    for found in re.finditer(r"(?<![\d.\-])(\d[\d,]*)\s+(?:x\s+)?" + name + r"(?:e?s)?\b", text):
        before, after = text[max(0, found.start() - 45):found.start()], text[found.end():found.end() + 30]
        if re.search(r"\b(?:not|no|never|instead of|rather than)\s*$", before):
            continue
        if re.match(r"\s+(?:are|is)\s+not\b", after):
            continue
        amounts.add(int(found.group(1).replace(",", "")))
    return amounts.pop() if len(amounts) == 1 else None


def tool_summary(rows):
    summary = {}
    for use_tool in (False, True):
        xs = [x for x in rows if x["use_tool"] == use_tool]
        k = sum(x["correct"] for x in xs)
        summary["with_tool" if use_tool else "without_tool"] = {
            "n": len(xs), "correct": k, "accuracy": round(100 * k / len(xs), 1), "ci": wilson(k, len(xs)),
            "called_tool": sum(1 for x in xs if x["tool_calls"]),
            "called_by_fallback": sum(1 for x in xs if any(c.get("via") == "route" for c in x["tool_calls"]))}
    return summary


def rescore():
    """Score every saved tool run again with answer_number (raw answers untouched; the old verdict is kept in
    each row as correct_first_number)."""
    for path in sorted(OUT.glob("tool*.json")):
        t = load(path.name)
        if "rows" not in t:
            continue
        for x in t["rows"]:
            x.setdefault("correct_first_number", x["correct"])
            x["correct"] = answer_number(x["answer"], x["question"]) == x["gold"]
        t["summary"] = {**t["summary"], **tool_summary(t["rows"])}
        t["scorer"] = "the number only, or the number right before the ingredient's name; refusals never count"
        save(path.name, t)
        s = t["summary"]
        print(path.name, "with tool", s["with_tool"]["correct"], "without", s["without_tool"]["correct"],
              "(first-number scorer:", sum(x["correct_first_number"] for x in t["rows"] if x["use_tool"]),
              sum(x["correct_first_number"] for x in t["rows"] if not x["use_tool"]), ")")


def tool(n=40, dev=False):
    """With vs without the craft tool on quantity questions (dev=True: the separate questions used to tune the prompts),
    plus how often the planner calls the tool for ordinary questions where it should not."""
    name = "tool_dev" if dev else "tool"
    r = mcqa.Retriever(mcqa.DEFAULT_SIZE)
    rows, qs = [], tool_questions(n, dev=dev)
    save_questions(name, qs)
    for i, q in enumerate(qs):
        for use_tool in (False, True):
            out = mcqa.answer(q["question"], r, "rerank", k=5, use_tool=use_tool)
            rows.append({**q, "use_tool": use_tool, "answer": out["answer"], "tool_calls": out["tool_calls"],
                         "correct": answer_number(out["answer"], q["question"]) == q["gold"]})
        print(f"{i + 1}/{n}", flush=True)
    summary = tool_summary(rows)
    # false alarms: ordinary (non-crafting) questions from the answer-quality set
    others = [q["question"] for q in questions(n, seed=SEED + 2 if dev else SEED + 1,
                                               exclude=[q["question"] for q in questions(1000)])]
    false_calls = [{"question": q, "calls": c} for q in others if (c := mcqa.plan_tools(q))]
    summary["false_calls_on_other_questions"] = {"n": len(others), "called": len(false_calls)}
    save(f"{name}.json", {"seed": SEED, "dev": dev, "game_version": mcqa.crafting_data()["version"],
                          "scorer": "the number only, or the number right before the ingredient's name; refusals never count",
                          "summary": summary, "false_calls": false_calls, "rows": rows})


# ---------- report ---------------------------------------------------------------------------------------------------

def report():
    lines = ["# MCQA results (generated by `python eval.py report`)", ""]
    if (OUT / "retrieval.json").exists():
        res = load("retrieval.json")["results"]
        lines += ["## Retrieval ablation", "",
                  "Source-page hit rate: a hit means a retrieved chunk comes from the wiki page the question was "
                  "generated from. It is not answer recall: a question can be answered on another page, and a chunk "
                  "from the source page need not contain the answer.", "",
                  "| Variant | Chunk size | Chunks | Hit@1 | Hit@5 [95% CI] | Hit@10 | MRR@10 |",
                  "|---|---|---|---|---|---|---|"]
        for x in res.values():
            lo, hi = x["recall@5_ci"]
            lines.append(f"| {x['variant']} | {x['size']} | {x['chunks']} | {x['recall@1']}% | {x['recall@5']}% "
                         f"[{lo}, {hi}] | {x['recall@10']}% | {x['mrr@10']} |")
        lines.append("")
    if (OUT / "answers_summary.json").exists():
        a = load("answers_summary.json")
        lines += ["## Answer quality: no retrieval vs dense vs hybrid + reranker", "",
                  f"{a['summary']['none']['n']} held-out questions; chunk size {a['chunk_size']}; generator "
                  f"{a['generator']}; judge {a['judge_model']}; BERTScore {a['bertscore_model']}. "
                  "References come from the synthetic question pool and are not always right. "
                  f"Judge score: {a['score']}.", "",
                  "| Retrieval | Refused (only \"I do not know\") | Hedged | Judge: correct [95% CI] | partial | "
                  "incorrect | Judge score | BERTScore F1 | Correct, of answered | BERTScore F1, answered | "
                  "Faithful: supported / valid verdicts (attempted, unparsed) |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        for v, x in a["summary"].items():
            faithful = (f"{x['supported']}/{x['faithful_checked']} ({x['supported_pct']}%) "
                        f"({x['faithful_attempted']}, {x['faithful_unparsed']})" if x["faithful_attempted"] else "n/a")
            lines.append(f"| {v} | {x['refused']} | {x['hedged']} | {x['correct']} ({x['correct_pct']}%) [{x['correct_ci'][0]}, "
                         f"{x['correct_ci'][1]}] | {x['partial']} | {x['incorrect']} | {x['score']} | "
                         f"{x['bertscore_f1']} | {x['correct_of_answered_pct']}% of {x['answered']} | "
                         f"{x['bertscore_f1_answered']} | {faithful} |")
        lines += ["", "Paired differences (same questions, 95% bootstrap interval over questions):", "",
                  "| Comparison | Mean difference | 95% CI |", "|---|---|---|"]
        for k, x in a["paired"].items():
            lines.append(f"| {k} | {x['mean_difference']:+} | [{x['ci95'][0]}, {x['ci95'][1]}] |")
        lines.append("")
    if (OUT / "judge_selection.json").exists():
        lines += ["## Choosing the judge (`scripts/judge_selection.py`)", "",
                  "Correctness verdicts of several judge set-ups against the 36 hand labels of the first answer run.", "",
                  "| Prompt | Model | Exact agreement | Correct vs not | Per variant (none / dense / rerank, of 12) | "
                  "Unparsed | Seconds |", "|---|---|---|---|---|---|---|"]
        for x in load("judge_selection.json")["results"]:
            model = x["model"] + (" (thinking)" if x["think"] else "")
            per = " / ".join(str(x["per_variant"][v]) for v in VARIANTS_QA)
            lines.append(f"| {x['prompt']} | {model} | {x['exact_agreement']}/{x['n']} | {x['correct_vs_not']}/{x['n']} "
                         f"| {per} | {x['unparsed']} | {x['seconds']} |")
        lines.append("")
    if (OUT / "judge_validation.json").exists():
        j = load("judge_validation.json")
        lines += ["## How far can the LLM judges be trusted?", "",
                  f"Verdicts of the {j['judge_model']} judges against hand labels: correctness (correct / partial / "
                  "incorrect) and faithfulness (supported / partly / unsupported).", "",
                  "| Labelled set | Judge | n | Labelled by | Exact agreement | Top label vs rest | Cohen's kappa | "
                  "Per variant | Disagreements (label -> judge) |", "|---|---|---|---|---|---|---|---|---|"]
        for name, x in j["results"].items():
            per = ", ".join(f"{k} {v}" for k, v in x["per_variant"].items())
            dis = ", ".join(f"{k}: {v}" for k, v in x["confusion (label -> judge)"].items()
                            if k.split(" -> ")[0] != k.split(" -> ")[1])
            lines.append(f"| `{name}` | {x['judge']} | {x['n']} | {x['labelled_by']} | {x['exact_agreement']}/{x['n']} "
                         f"| {x['top_vs_not_agreement']}/{x['n']} ({x['top_label']}) | {x['cohen_kappa']} | {per} "
                         f"| {dis} |")
        lines.append("")
    for name, title in (("tool_dev.json", "Crafting tool, dev questions (used to tune the prompts)"),
                        ("tool.json", "Crafting tool, held-out test questions (earlier experiment; current: results/verified/tool_final)")):
        if (OUT / name).exists():
            t = load(name)
            s = t["summary"]
            lines += [f"## {title}", "",
                      f"Quantity questions with a number computed from Minecraft {t['game_version']} recipe files; "
                      "answers go through the full pipeline (hybrid + reranker retrieval, 5 passages).", "",
                      "| Variant | Correct | Accuracy [95% CI] | Called the tool | of which by the fallback |",
                      "|---|---|---|---|---|"]
            for v in ("without_tool", "with_tool"):
                x = s[v]
                lines.append(f"| {v.replace('_', ' ')} | {x['correct']}/{x['n']} | {x['accuracy']}% "
                             f"[{x['ci'][0]}, {x['ci'][1]}] | {x['called_tool']} | {x.get('called_by_fallback', '-')} |")
            f = s["false_calls_on_other_questions"]
            lines += ["", f"Tool called for {f['called']} of {f['n']} ordinary (non-crafting) questions.", ""]
    history = [("tool_run1_before_fix.json", "first design: the tool offered in one prompt together with the passages"),
               ("tool_dev_before_citation_fix.json", "two-step agent before the citation fix, dev questions"),
               ("tool_run2_before_citation_fix.json", "two-step agent before the citation fix, test questions"),
               ("tool_run3_before_name_fix.json", "final agent, test questions before two generic names "
                                                  "(\"Smithing Template\") were made specific")]
    rows = [(name, what, load(name)["summary"]) for name, what in history if (OUT / name).exists()]
    if rows:
        lines += ["## Crafting tool, earlier runs (kept for the record)", "",
                  "The citation fix (the final answer cites the tool as [tool] instead of a passage) came from the demo, "
                  "and the name fix from Codex's review (docs/codex_review.md), not from test errors; every test run "
                  "is kept. All runs are scored with the current parser (`eval.py rescore`); the first parser took "
                  "the first number anywhere and counted 4 refusals in the first run as correct. "
                  "See docs/failure_analysis.md.", "",
                  "| File | What | With tool | Without tool | Called the tool |", "|---|---|---|---|---|"]
        for name, what, s in rows:
            w, wo = s["with_tool"], s["without_tool"]
            lines.append(f"| `{name}` | {what} | {w['correct']}/{w['n']} | {wo['correct']}/{wo['n']} | "
                         f"{w['called_tool']}/{w['n']} |")
        lines.append("")
    (OUT / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    {"retrieval": retrieval, "misses": misses, "answers": answers, "summary": summary_only, "judgecheck": judgecheck,
     "tool": tool, "rescore": rescore,
     "tooldev": lambda: tool(dev=True), "report": report}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
