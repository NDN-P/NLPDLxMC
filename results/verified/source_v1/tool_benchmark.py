"""New recipe-item holdout; preserves earlier experiments. Local Ollama, cached models only.

python scripts/tool_benchmark.py
"""
import json
import math
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import mcqa
import eval as ev
from scripts.benchmark_eval import config, read, write, digest

OUT = ROOT / "results" / "verified" / "tool"


def questions():
    excluded = {"minecraft:" + x for x in ("hopper", "torch", "bucket", "chest", "cake", "iron_pickaxe", "anvil", "crafting_table", "piston", "book", "pumpkin_pie", "observer")}
    for path in (ROOT / "results").glob("questions_tool*.jsonl"):
        excluded.update(x["item"] for x in read(path) if "item" in x)
    data = mcqa.crafting_data()
    candidates = []
    for iid, recipes in sorted(data["recipes"].items()):
        concrete = sorted({i for i in recipes[0]["slots"] if not i.startswith("#") and i in data["names"]})
        if len(recipes) == 1 and concrete and iid in data["names"] and iid not in excluded:
            candidates.append((iid, recipes[0], concrete))
    rng = random.Random(17)
    rows = []
    for iid, recipe, ingredients in rng.sample(candidates, 40):
        ingredient, count = rng.choice(ingredients), rng.randint(2, 16)
        gold = Counter(recipe["slots"])[ingredient] * math.ceil(count / recipe["makes"])
        rows.append({"question": f"How many {mcqa.label(ingredient, data)} do I need to craft {count} {mcqa.label(iid, data)}? Reply with the number only.",
                     "item": iid, "ingredient": ingredient, "count": count, "gold": gold,
                     "recipe": recipe, "game_version": data["version"]})
    return rows, sorted(excluded)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    qs, excluded = questions()
    cfg = {**config(), "task": "recipe-item holdout", "seed": 17, "n": len(qs),
           "recipe_sha256": digest(mcqa.DATA / "crafting.json"), "evaluator_sha256": digest(Path(__file__)),
           "excluded_items": excluded, "questions": qs, "variants": ["without_tool", "with_tool"],
           "use_tool": "paired false/true", "provenance": "Exact quantities from official recipe slots; no judge"}
    if (OUT / "config.json").exists() and json.loads((OUT / "config.json").read_text(encoding="utf-8")) != cfg:
        raise ValueError("Configuration changed; preserve this run and use a separate output directory")
    write(OUT / "config.json", cfg)
    write(OUT / "questions.json", qs)
    r = mcqa.Retriever(mcqa.DEFAULT_SIZE)
    rows = read(OUT / "answers.jsonl")
    done = {(x["item"], x["use_tool"]) for x in rows}
    with (OUT / "answers.jsonl").open("a", encoding="utf-8") as f:
        for q in qs:
            for use_tool in (False, True):
                if (q["item"], use_tool) in done:
                    continue
                t = time.perf_counter()
                result = mcqa.answer(q["question"], r, use_tool=use_tool)
                amount = ev.answer_number(result["answer"], q["question"])
                rows.append({**q, **result, "use_tool": use_tool, "predicted_amount": amount,
                             "correct": amount == q["gold"], "seconds": round(time.perf_counter() - t, 2)})
                f.write(json.dumps(rows[-1], ensure_ascii=False) + "\n")
                f.flush()
                print(f"Tool {len(rows)}/80 {q['item']} enabled={use_tool} gold={q['gold']}: {result['answer'][:130]}", flush=True)
    # Fixed dev non-recipe cases for false calls; keep these distinct from fresh recipe-item testing.
    other = [q for q in read(mcqa.DATA / "java_benchmark.jsonl") if q["split"] == "dev"]
    if (OUT / "false_calls.json").exists():
        alarms = json.loads((OUT / "false_calls.json").read_text(encoding="utf-8"))
    else:
        alarms = []
        for q in other:
            calls = [] if mcqa.other_edition(q["question"]) else mcqa.plan_tools(q["question"])
            alarms.append({"id": q["id"], "question": q["question"], "calls": calls})
        write(OUT / "false_calls.json", alarms)
    summary = {"variants": ev.tool_summary(rows), "false_call_dev_n": len(alarms),
               "false_call_dev_count": sum(bool(x["calls"]) for x in alarms),
               "answer_modes": dict(Counter(x.get("answer_mode", "llm") for x in rows if x["use_tool"])),
               "item_overlap_with_previous_sets": len({x["item"] for x in qs} & set(excluded))}
    write(OUT / "summary.json", summary)
    lines = ["# New recipe-item holdout", "", "40 new product IDs excluded from all prior saved tool question sets and known recipe development probes.",
             "Gold quantities come from version-pinned recipe slots; this measures the complete routing/calculator/answer pipeline.", "",
             "| Variant | Correct | Accuracy | 95% Wilson CI (%) | Tool called |", "|---|---:|---:|---|---:|"]
    for v, s in summary["variants"].items():
        lines.append(f"| {v} | {s['correct']}/{s['n']} | {s['accuracy']}% | {s['ci']} | {s['called_tool']} |")
    lines += ["", f"False calls on {len(alarms)} fixed non-recipe dev cases: {summary['false_call_dev_count']}.",
              f"Tool-enabled response modes: {summary['answer_modes']}.", "",
              "A calculator-backed fallback is explicitly recorded; gains do not demonstrate learned arithmetic or model training."]
    (OUT / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    run()
