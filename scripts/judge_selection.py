"""How the correctness judge was chosen: several judge set-ups against the hand labels of the first answer run
(results/judge_labels_run1.jsonl), saved to results/judge_selection.json.

    python scripts/judge_selection.py            # four set-ups, about 7 minutes with a GPU
    python scripts/judge_selection.py --think    # also qwen3:4b with thinking (about 15 minutes more)
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import eval as ev  # noqa: E402
import mcqa  # noqa: E402

# the first rewrite: a reason, then the verdict
REASON_PROMPT = """You check whether a system's answer to a Minecraft question agrees with a reference answer.

Question: {question}
Reference answer: {reference}
System answer: {answer}

Judge only whether the system answer states the key facts of the reference answer; do not use your own knowledge.
- "correct": it states the key facts of the reference (extra details are fine if they do not contradict it).
- "partial": it states some key facts of the reference, but others are missing or contradicted.
- "incorrect": it states none of the key facts, contradicts them, denies the premise, or says it does not know.
Reply with JSON: {{"reason": "<one sentence>", "verdict": "correct" | "partial" | "incorrect"}}"""
REASON_SCHEMA = {"type": "object", "required": ["reason", "verdict"], "properties": {
    "reason": {"type": "string"}, "verdict": {"type": "string", "enum": ["correct", "partial", "incorrect"]}}}

SETUPS = [("reason-then-verdict", REASON_PROMPT, REASON_SCHEMA, "qwen3:4b-instruct", None),
          ("reason-then-verdict", REASON_PROMPT, REASON_SCHEMA, "llama3.2:3b", None),
          ("decomposed (final)", ev.CORRECT_PROMPT, ev.CORRECT_SCHEMA, "qwen3:4b-instruct", None),
          ("decomposed (final)", ev.CORRECT_PROMPT, ev.CORRECT_SCHEMA, "qwen3:4b", False)]
if "--think" in sys.argv:
    SETUPS.append(("reason-then-verdict", REASON_PROMPT, REASON_SCHEMA, "qwen3:4b", True))


def main():
    rows = [json.loads(line) for line in (ev.OUT / "judge_labels_run1.jsonl").open(encoding="utf-8")]
    gold = [x["label"] for x in rows]
    old = {5: "correct", 4: "partial", 3: "partial"}  # the first judge's 1-5 scores, as saved in answers_run1.jsonl
    saved = {(x["question"], x["variant"]): x["judge"]["correct"]
             for x in map(json.loads, (ev.OUT / "answers_run1.jsonl").open(encoding="utf-8"))}
    results = [summarize("one-step 1-5 score (first run, saved verdicts)", "qwen3:4b-instruct", None, rows, gold,
                         [old.get(saved[(x["question"], x["variant"])], "incorrect") for x in rows], 0)]
    for name, prompt, schema, model, think in SETUPS:
        t, pred = time.time(), []
        for x in rows:
            msg = mcqa.chat([{"role": "user", "content": prompt.format(**x)}], fmt=schema, model=model, think=think,
                            num_predict=2048 if think else 512)
            try:
                pred.append(json.loads(msg["content"])["verdict"])
            except (ValueError, KeyError):
                pred.append(None)
        results.append(summarize(name, model, think, rows, gold, pred, time.time() - t))
    ev.save("judge_selection.json", {"labels": "results/judge_labels_run1.jsonl", "results": results})


def summarize(name, model, think, rows, gold, pred, secs):
    r = {"prompt": name, "model": model, "think": think, "n": len(rows),
         "exact_agreement": sum(p == g for p, g in zip(pred, gold)),
         "correct_vs_not": sum((p == "correct") == (g == "correct") for p, g in zip(pred, gold)),
         "unparsed": sum(p is None for p in pred),
         "per_variant": {v: sum(p == g for p, g, x in zip(pred, gold, rows) if x["variant"] == v)
                         for v in ev.VARIANTS_QA},
         "seconds": round(secs)}
    print(r, flush=True)
    return r


if __name__ == "__main__":
    main()
