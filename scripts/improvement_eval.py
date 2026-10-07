"""Frozen before/after checks on new, AI-curated source pages and recipe products.

Prepare and validate before generation; never overwrite earlier evaluation runs.
python scripts/improvement_eval.py validate
python scripts/improvement_eval.py run --implementation before
python scripts/improvement_eval.py run --implementation after
python scripts/improvement_eval.py report
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import random
import re
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
from scripts.benchmark_eval import digest, evidence_rank, read, write

DATASET = ROOT / "data" / "improvement_benchmark.jsonl"
OUT = ROOT / "results" / "improvement_review"
PROVENANCE = "AI-curated before generation; exact pinned source/official recipe checked; not independently human or game verified"


def prepare():
    if DATASET.exists():
        raise ValueError("The preselected dataset already exists; keep it frozen.")
    pages = {p["title"]: p for p in mcqa.load_pages()}
    facts = [
        ("dev", "Chest", 'A large chest (or "double chest") is the combination of two adjacent chests, and can store twice as many items.',
         "How does a double chest's storage capacity compare with a single chest?", "A double chest stores twice as many items as a single chest."),
        ("dev", "Beacon", "It doesn't matter which of the items is fed into the beacon.",
         "Does choosing a diamond instead of an iron ingot to activate a beacon change its powers?", "No. The activation payment item does not change the beacon's powers."),
        ("dev", "Iron Golem", "Using an iron ingot on a damaged iron golem heals 25HP", "How much health does one iron ingot restore to a damaged iron golem?", "One iron ingot restores 25 health points."),
        ("dev", "Fortune", "Silk Touch and Fortune are mutually exclusive.", "Can Silk Touch and Fortune normally coexist on one tool?", "No. Silk Touch and Fortune are mutually exclusive."),
        ("test", "Pig", "Pigs can be bred using carrots, potatoes, or beetroots.", "Which three crops can breed pigs?", "Carrots, potatoes, and beetroots can breed pigs."),
        ("test", "Wolf", "A wolf can be tamed by feeding it bones.", "What item is used to tame a wild wolf?", "Bones are used to tame a wild wolf."),
        ("test", "Wither", "It is the only source of Nether stars, which are needed to craft beacons.", "Which mob is the source of the Nether star used for a beacon?", "The wither is the source of Nether stars."),
        ("test", "Smelting", "The furnace takes 10 seconds (200 in-game ticks) to smelt an item.", "How long does a normal furnace take to smelt one item, in seconds and game ticks?", "A normal furnace takes 10 seconds, or 200 game ticks, per item."),
        ("test", "Food", "Dried kelp takes half the time (16 game ticks (0.8 seconds))", "How long does eating dried kelp take?", "Eating dried kelp takes 16 game ticks, or 0.8 seconds."),
        ("test", "Slime", "Slimes spawn in different sizes, and larger ones split into smaller ones on death.", "What happens to a larger slime when it dies?", "A larger slime splits into smaller slimes when it dies."),
        ("test", "Blaze", "It is not fire damage, does not ignite the target, and is not prevented by Fire Resistance.", "Does Fire Resistance protect a player from a blaze's melee attack?", "No. A blaze's melee attack is not fire damage, so Fire Resistance does not prevent it."),
        ("test", "Armor", "Chainmail armor can be repaired in an anvil using iron ingots", "Which material repairs chainmail armor in an anvil?", "Iron ingots repair chainmail armor in an anvil."),
    ]
    rows = []
    for split, title, quote, question, reference in facts:
        p = pages[title]
        start = p["text"].index(quote)
        headings = list(re.finditer(r"^(={2,6})\s*(.*?)\s*\1\s*$", p["text"][:start], re.M))
        section = headings[-1][2] if headings else "Introduction"
        rows.append({"id": f"improve-{len(rows)+1:03d}", "split": split, "kind": "answerable", "edition": "Java", "version": mcqa.MC_VERSION,
                     "question": question, "reference_answer": reference, "title": title, "revid": p["revid"], "section": section,
                     "source_url": f"https://minecraft.wiki/w/{title.replace(' ', '_')}?oldid={p['revid']}", "source_timestamp": p["timestamp"],
                     "evidence": quote, "evidence_start_char": start, "evidence_end_char": start+len(quote),
                     "evidence_sha256": hashlib.sha256(quote.encode()).hexdigest(), "human_reviewed": False, "provenance": PROVENANCE})
    negatives = [
        ("dev", "unanswerable", "What is the exact health of the wolf standing in my private world right now?"),
        ("dev", "out_of_scope", "In Minecraft Education Edition, how do I use the material reducer?"),
        ("test", "unanswerable", "What exact items are currently inside my singleplayer world's chest at coordinates 12, 64, 30?"),
        ("test", "out_of_scope", "In Minecraft Bedrock Edition, how do I enable education chemistry features?"),
    ]
    for split, kind, question in negatives:
        rows.append({"id": f"improve-{len(rows)+1:03d}", "split": split, "kind": kind, "edition": "Java", "version": mcqa.MC_VERSION,
                     "question": question, "reference_answer": "I do not know.", "human_reviewed": False, "provenance": PROVENANCE})
    excluded = {"minecraft:"+x for x in ("hopper", "torch", "bucket", "chest", "cake", "iron_pickaxe", "anvil", "crafting_table", "piston", "book", "pumpkin_pie", "observer")}
    for path in (ROOT / "results").glob("questions_tool*.jsonl"):
        excluded.update(x["item"] for x in read(path) if "item" in x)
    for folder in ("tool", "tool_final"):
        path = ROOT / "results" / "verified" / folder / "questions.json"
        if path.exists():
            excluded.update(x["item"] for x in json.loads(path.read_text(encoding="utf-8")))
    data = mcqa.crafting_data()
    candidates = []
    for iid, recipes in sorted(data["recipes"].items()):
        ingredients = sorted({x for x in recipes[0]["slots"] if not x.startswith("#") and x in data["names"] and x != iid})
        if iid not in excluded and iid in data["names"] and len(recipes) == 1 and ingredients:
            candidates.append((iid, recipes[0], ingredients))
    rng = random.Random(41)
    for j, (iid, recipe, ingredients) in enumerate(rng.sample(candidates, 12)):
        ingredient, count = rng.choice(ingredients), rng.randint(2, 16)
        name, product = mcqa.label(ingredient, data), mcqa.label(iid, data)
        style = ("canonical", "varied", "compound")[j % 3]
        question = {"canonical": f"How many {name} do I need to craft {count} {product}? Reply with the number only.",
                    "varied": f"I want {count} {product}. How much {name} does the crafting recipe require? Reply with the number only.",
                    "compound": f"For {count} {product}, calculate the required {name} and explain whether the crafting table alone makes them."}[style]
        rows.append({"id": f"improve-{len(rows)+1:03d}", "split": "dev" if j < 6 else "test", "kind": "recipe", "style": style,
                     "edition": "Java", "version": data["version"], "question": question, "item": iid, "ingredient": ingredient, "count": count,
                     "gold": Counter(recipe["slots"])[ingredient] * math.ceil(count / recipe["makes"]), "recipe": recipe,
                     "ingredient_name": name, "human_reviewed": False, "provenance": PROVENANCE})
    DATASET.write_text("".join(json.dumps(q, ensure_ascii=False)+"\n" for q in rows), encoding="utf-8")
    write(OUT / "selection.json", {"seed": 41, "selected_before_generation": True, "dataset_sha256": digest(DATASET),
                                  "excluded_recipe_items": sorted(excluded), "provenance": PROVENANCE})
    validate()


def validate():
    qs = read(DATASET)
    if len(qs) != 28 or len({q["id"] for q in qs}) != len(qs) or len({q["question"] for q in qs}) != len(qs):
        raise ValueError("Expected 28 unique preselected cases.")
    selection = json.loads((OUT / "selection.json").read_text(encoding="utf-8"))
    if digest(DATASET) != selection["dataset_sha256"]:
        raise ValueError("Preselected dataset changed.")
    pages = {p["title"]: p for p in mcqa.load_pages()}
    old = {q.get("title") for q in read(mcqa.DATA / "java_benchmark.jsonl") if q["kind"] == "answerable"}
    groups = {s: set() for s in ("dev", "test")}
    data = mcqa.crafting_data()
    for q in qs:
        if q["split"] not in groups or q["version"] != mcqa.MC_VERSION or q["human_reviewed"]:
            raise ValueError("Invalid scope, split, or unverified provenance.")
        if q["kind"] == "answerable":
            p = pages[q["title"]]
            if q["title"] in old or p["revid"] != q["revid"] or p["text"][q["evidence_start_char"]:q["evidence_end_char"]] != q["evidence"]:
                raise ValueError("Prior page overlap or quote mismatch.")
            if hashlib.sha256(q["evidence"].encode()).hexdigest() != q["evidence_sha256"]:
                raise ValueError("Quote hash mismatch.")
            groups[q["split"]].add(q["title"])
        elif q["kind"] == "recipe":
            if q["item"] in selection["excluded_recipe_items"] or q["recipe"] != data["recipes"][q["item"]][0]:
                raise ValueError("Prior recipe overlap or recipe mismatch.")
            if q["gold"] != Counter(q["recipe"]["slots"])[q["ingredient"]] * math.ceil(q["count"]/q["recipe"]["makes"]):
                raise ValueError("Recipe gold mismatch.")
    if groups["dev"] & groups["test"]:
        raise ValueError("Dev/test factual pages overlap.")
    return qs


def implementation(name):
    folder = OUT / f"source_{name}"
    path = folder / "mcqa.py"
    if name == "after" and not path.exists():
        folder.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / "mcqa.py").read_bytes())
        write(folder / "manifest.json", {"sha256": {"mcqa.py": digest(path)}, "data": "shared, unchanged pinned corpus/index/recipes"})
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if manifest["sha256"]["mcqa.py"] != digest(path):
        raise ValueError("Frozen implementation differs from its source manifest.")
    spec = importlib.util.spec_from_file_location(f"mcqa_improvement_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.DATA = ROOT / "data"
    return module, path


def run(name, split):
    qs = [q for q in validate() if split == "all" or q["split"] == split]
    module, path = implementation(name)
    tags = json.load(urllib.request.urlopen("http://localhost:11434/api/tags", timeout=10))["models"]
    model = next(m for m in tags if m["name"] == module.LLM)
    cfg = {"dataset_sha256": digest(DATASET), "implementation_sha256": digest(path), "evaluator_sha256": digest(Path(__file__)),
           "judge_code_sha256": digest(ROOT / "eval.py"), "generator": module.LLM, "generator_digest": model["digest"], "judge": ev.JUDGE_MODEL,
           "shared_data_sha256": {f: digest(module.DATA / f) for f in ("pages.jsonl", "chunks_256.jsonl", "emb_256.npy", "crafting.json")},
           "factual_variants": ["dense", "rerank"], "recipe_use_tool": True, "provenance": PROVENANCE}
    cfgpath = OUT / f"{name}_config.json"
    if cfgpath.exists() and json.loads(cfgpath.read_text(encoding="utf-8")) != cfg:
        raise ValueError("Frozen run configuration changed; keep existing evidence intact.")
    write(cfgpath, cfg)
    answers = OUT / f"{name}_answers.jsonl"
    rows = read(answers)
    done = {(q["id"], q["variant"]) for q in rows}
    r = module.Retriever(256)
    with answers.open("a", encoding="utf-8") as f:
        for q in qs:
            for variant in (["rerank"] if q["kind"] == "recipe" else ["dense", "rerank"]):
                if (q["id"], variant) in done:
                    continue
                t = time.perf_counter()
                result = module.answer(q["question"], r, variant, use_tool=q["kind"] == "recipe")
                row = {**q, "variant": variant, "implementation": name, **result, "generation_seconds": round(time.perf_counter()-t, 3)}
                row["refused"] = ev.refused(row["answer"])
                if q["kind"] == "recipe":
                    # Use the explicit target ingredient for every wording; never take the first unrelated number.
                    scorer_question = f"How many {q['ingredient_name']} do I need to craft"
                    row["predicted_amount"] = ev.answer_number(row["answer"], scorer_question)
                    row["quantity_correct"] = row["predicted_amount"] == q["gold"]
                else:
                    row["reference"] = q["reference_answer"]
                    row["correct"] = ev.judge_correct(row) if q["kind"] == "answerable" else None
                    row["faithful"] = ev.judge_faithful(row)
                    ids = r.search(q["question"], variant, 10)
                    row["retrieved"] = [{"id": i, **r.chunks[i]} for i in ids]
                    row["evidence_rank"] = evidence_rank(q, row["retrieved"])
                f.write(json.dumps(row, ensure_ascii=False)+"\n")
                f.flush()
                rows.append(row)
                print(f"{name} {q['split']} {q['id']} {variant} {row['generation_seconds']}s: {row['answer'][:180]}", flush=True)
    if len(rows) == 44:
        from bert_score import score
        facts = [q for q in rows if q["kind"] == "answerable"]
        _, _, f1 = score([q["answer"] or "-" for q in facts], [q["reference"] for q in facts], model_type="distilroberta-base", lang="en", rescale_with_baseline=True)
        for q, value in zip(facts, f1.tolist()):
            q["bertscore_f1"] = round(value, 4)
        answers.write_text("".join(json.dumps(q, ensure_ascii=False)+"\n" for q in rows), encoding="utf-8")
        report()


def report():
    summary = {"provenance": PROVENANCE, "dataset_sha256": digest(DATASET), "runs": {}}
    human_rows = []
    lines = ["# Improvement comparison", "", PROVENANCE+".", "", "12 factual cases use 12 source pages absent from the earlier factual benchmark; dev/test pages are disjoint. 12 recipe products exclude previous saved tool sets. Cases were frozen before generation.",
             "", "| Implementation | Split | Variant | Facts correct | BERTScore F1 | Evidence @5 | Pure negative refusals | Recipe quantities correct |", "|---|---|---|---:|---:|---:|---:|---:|"]
    for name in ("before", "after"):
        rows = read(OUT / f"{name}_answers.jsonl")
        if not rows:
            continue
        expected = {(q["id"], v) for q in validate() for v in (["rerank"] if q["kind"] == "recipe" else ["dense", "rerank"])}
        if (len(rows) != len(expected) or {(q["id"], q["variant"]) for q in rows} != expected
                or any("bertscore_f1" not in q for q in rows if q["kind"] == "answerable")):
            raise ValueError(f"Incomplete {name} run; resume generation and scoring before reporting.")
        cfg = json.loads((OUT / f"{name}_config.json").read_text(encoding="utf-8"))
        _, path = implementation(name)
        if cfg["implementation_sha256"] != digest(path) or cfg["dataset_sha256"] != digest(DATASET) or cfg["evaluator_sha256"] != digest(Path(__file__)):
            raise ValueError("Frozen source, dataset, or evaluator changed since generation.")
        groups = {}
        for split in ("dev", "test"):
            for variant in ("dense", "rerank"):
                xs = [q for q in rows if q["split"] == split and q["variant"] == variant]
                facts = [q for q in xs if q["kind"] == "answerable"]
                negatives = [q for q in xs if q["kind"] in ("unanswerable", "out_of_scope")]
                recipes = [q for q in xs if q["kind"] == "recipe"]
                faith = Counter(q["faithful"].get("verdict") for q in xs if q.get("faithful") is not None)
                label = Counter(ev.factual_verdict(q) for q in facts)
                value = {"facts_n": len(facts), "correct": label["correct"], "partial": label["partial"], "incorrect": label["incorrect"], "judge_unparsed": label[None],
                         "bertscore_f1": ev.mean(q.get("bertscore_f1") for q in facts if "bertscore_f1" in q),
                         "evidence_at_5": sum(q["evidence_rank"] is not None and q["evidence_rank"] <= 5 for q in facts),
                         "negative_n": len(negatives), "pure_negative_refusals": sum(q["refused"] for q in negatives),
                         "faithfulness": {"supported": faith["supported"], "partly": faith["partly"], "unsupported": faith["unsupported"], "unparsed": faith[None]},
                         "recipe_n": len(recipes), "recipe_quantity_correct": sum(q["quantity_correct"] for q in recipes),
                         "recipe_tool_calls": sum(bool(q.get("tool_calls")) for q in recipes),
                         "recipe_by_style": {s: {"n": sum(q["style"] == s for q in recipes), "correct": sum(q["style"] == s and q["quantity_correct"] for q in recipes)} for s in ("canonical", "varied", "compound")},
                         "warm_generation_seconds_mean": ev.mean(q["generation_seconds"] for q in xs if q["id"] != "improve-001")}
                groups[f"{split}_{variant}"] = value
                lines.append(f"| {name} | {split} | {variant} | {value['correct']}/{len(facts)} | {value['bertscore_f1']} | {value['evidence_at_5']}/{len(facts)} | {value['pure_negative_refusals']}/{len(negatives)} | {value['recipe_quantity_correct']}/{len(recipes)} |")
        summary["runs"][name] = {"complete": len(rows) == 44, "rows": len(rows), "groups": groups}
        human_rows.extend([q["id"], q["kind"], name, q["variant"], q["question"], q.get("reference_answer", q.get("gold", "")), q.get("evidence", ""), q["answer"], "", ""] for q in rows)
    lines += ["", "Correctness and faithfulness are automatic judgments from the same local model as the generator; BERTScore measures textual similarity. Pure factual refusals score incorrect. The small sample has wide uncertainty and does not certify current-version game behavior.",
              "", "Recipe scoring checks only the requested direct ingredient amount, not the rest of a compound explanation, inventory reuse, or recursively gathered materials. Different wording is tested explicitly. Negative counts require a pure refusal and are not comprehensive semantic refusal accuracy.",
              "", "Raw answers preserve citations, tool calls, supporting quotes, rankings, and response time excluding judges. Source snapshots and configuration hashes distinguish implementations; old evaluations remain unchanged. First-call CPU model loading affects latency; these timings are illustrative, not a rigorous performance benchmark.",
              "", "Dev cases may guide changes; test outputs must not guide tuning. No training or independent human labeling was performed."]
    write(OUT / "summary.json", summary)
    (OUT / "RESULTS.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    # Only create the review sheet after both complete runs so partial generation cannot truncate its coverage.
    if len(human_rows) == 88:
        ev.write_check_sheet(OUT / "human_check.csv", ["id", "kind", "implementation", "variant", "question", "reference", "evidence", "answer", "human_verdict", "notes"], human_rows)
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "validate", "run", "report"))
    parser.add_argument("--implementation", choices=("before", "after"), default="after")
    parser.add_argument("--split", choices=("dev", "test", "all"), default="all")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    elif args.command == "validate":
        print(f"Validated {len(validate())} preselected source-grounded cases.")
    elif args.command == "run":
        run(args.implementation, args.split)
    else:
        report()
