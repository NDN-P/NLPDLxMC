# Current source-grounded failure analysis — 2026-10-07

This section describes the new fixed Java 26.3 benchmark and final tool run. The historical analysis below is preserved for comparison; its older synthetic-pool scores are not the current benchmark scores. Evidence and outputs are saved in `results/verified/test/answers.jsonl`, `results/verified/test/summary.json`, `results/verified/tool_final/`, and `results/verified/demo_final.json`.

The gameplay test contains 34 answerable questions from 17 source pages and 6 negative cases. References were curated by Codex from exact pinned source excerpts. They remain AI-curated, source-checked, and **not independently human verified**. Generation and judging both use `qwen3:4b-instruct`; the correctness and faithfulness labels below are automated judgments with the limitations demonstrated here.

## Current gameplay results and what they measure

| Variant | Correct by LLM judge, with pure-refusal correction | Partial | Incorrect | BERTScore F1, answerable cases | Exact annotated evidence in top 5 | Pure refusals on answerable cases |
|---|---:|---:|---:|---:|---:|---:|
| No retrieval | 9/34 (26.5%) | 1 | 24 | 0.294 | 0/34 | 0 |
| Dense | **27/34 (79.4%)** | 4 | 3 | 0.493 | 31/34 (91.2%) | 3 |
| Hybrid + reranker | 26/34 (76.5%) | 4 | 4 | 0.451 | 30/34 (88.2%) | 2 |

Dense originally appeared to have 28 correct judgments. On `java26.3-045`, “Can I stop a trial spawner summoning mobs by placing torches around it?”, its complete answer was **“I do not know.”**, yet the judge returned `correct`. The reference evidence says, “The light level around a trial spawner does not affect how it summons entities.” The aggregate now treats every pure refusal on an answerable question as incorrect, giving **27/34**, while preserving the original judge output in the raw file and the original summaries. A refusal is not a correct answer to that factual question.

Retrieval improves these automated answer scores over no retrieval. The paired mean score difference, counting correct/partial/incorrect as 1/0.5/0, is +0.574 for dense minus no retrieval (95% bootstrap interval +0.368 to +0.765). The reranker minus dense difference is −0.029 (−0.162 to +0.103); this run does not establish a reranker advantage. The intervals reflect uncertainty within this small curated set, not all Minecraft questions.

**Exact evidence coverage and answer correctness are different measurements.** Coverage checks whether the specific annotated quote appears in a retrieved chunk, not merely whether the source page was found. A quote hit does not show that the generator used the correct passage. Conversely, `java26.3-025` (curing a zombie villager) and `java26.3-045` (trial-spawner lighting) were answered correctly by the reranked variant even though the annotated quote was outside its top five or absent: other retrieved text supplied the relevant fact. The quote-hit rate is therefore neither a general relevance metric nor a replacement for answer scoring.

## Observed failure mechanisms

**Historical passages can override current evidence.** For `java26.3-018`, “What material can I use to repair elytra in an anvil?”, the current *Anvil* evidence at rank 1 says elytra can be repaired with **phantom membranes**. The reranked answer instead says, “Elytra can be repaired on an anvil using leather [3].” Passage 3 is *Java Edition 1.9/Development versions > 15w41a > Additions > Items*, which describes the old leather recipe. The correctness judge rejects the answer, but the faithfulness judge calls it supported because the retrieved historical passage contains it. This is a real version-selection failure: being supported by some retrieved text does not establish Java 26.3 correctness. Dense uses the current passage and answers phantom membranes.

**Relevant evidence can be retrieved but ignored.** For `java26.3-029`, “What food breeds adult tamed llamas?”, the reranked first passage contains the exact evidence, “Adult tamed llamas can be bred by being fed a hay bale.” Its answer is still “I do not know.” This is a generation refusal despite sufficient evidence, rather than a retrieval miss.

**Retrieving the page can miss the answer-bearing section.** For `java26.3-040`, “What can I use to collect leaf blocks themselves?”, the reference is **shears or a Silk Touch tool**. Neither variant retrieves the annotated breaking section. Dense refuses; the reranked answer incorrectly says leaf blocks cannot be collected and cites general leaf behavior. The page topic alone is not enough. For `java26.3-026`, zombie-villager conversion to drowned, dense places the exact exception at rank 6 and refuses with only five passages available. For `java26.3-032`, cats and ocelots making creepers flee, the reranker similarly leaves the quote at rank 7 and refuses.

**Closed-book answers confidently invert simple mechanics.** On `java26.3-017`, the no-retrieval answer says anvil repair loses enchantments; the source says the target retains them. On `java26.3-020`, it claims sugar cane requires light for photosynthesis; the source explicitly says it grows in complete darkness. On `java26.3-041`, it invents an age requirement for taming adult horses. These are factual failures, not differences in reference wording.

## The evaluators also fail

The corrected summary fixes the obvious pure-refusal false positive, but it does not turn the remaining LLM verdicts into human truth labels. For dense `java26.3-029`, the answer almost repeats the hay-bale evidence verbatim, yet the judge calls it partial. Reranked `java26.3-022` correctly describes a baby turtle becoming an adult and dropping its scute, but is also labelled partial. Reranked `java26.3-035` accurately includes the source's **random tick** condition and Nether restriction; its judge summary drops the word “random” and labels it partial. These examples show instability around paraphrases and additional source-supported detail. They are recorded for team checking rather than silently regraded by another AI.

Faithfulness verdicts have additional problems. For dense `java26.3-030`, the answer discusses llama taming, while the faithfulness judge extracts a claim about equipping a llama with a chest from the supplied passages. For reranked `java26.3-048`, the answer correctly cites passage 5 saying Nether portals cannot be activated in the End, but the judge labels that claim unsupported and lists unrelated passage content as answer claims. The summary's supported counts—31/32 dense and 30/32 reranked—must therefore be described as **same-model automated judgments**, not independently verified faithfulness rates. The dense denominator also includes its non-refusal stronghold response to a negative case, whereas the reranked denominator contains only factual answers.

The saved `negative_correct_refusal` counts are **strict pure-refusal counts**: 5/6 no retrieval, 5/6 dense, 6/6 reranked. They do not capture every valid explanation of an information limit. No retrieval explains that Thaumcraft is outside vanilla scope on `java26.3-058`, but is not counted because it does not use a pure refusal. Dense `java26.3-055` offers general stronghold-location methods and explicitly says the exact location cannot be determined without the seed or coordinates; it invents no coordinates, but is also not counted. Semantic refusal quality needs team annotation. These strict counts should not be presented as comprehensive negative-case accuracy.

The dataset, judge, and review process are all AI-assisted. All human-review fields remain unfilled. `results/verified/test/human_check.csv` lets team members compare every question, reference, quote, and answer and record their own verdicts. Test outputs were inspected for this failure analysis; any future prompt or retrieval changes informed by them need a new test set or an explicit statement that the original test was reused.

## Final crafting-tool results and remaining routing failures

The final run uses 40 recipe-derived quantity questions with items disjoint from previous sets. With the tool enabled, **37/40 are correct (92.5%, Wilson 95% interval 80.1–97.4%)**, compared with **1/40 without the tool (2.5%, 0.4–12.9%)**. All 37 correct tool-enabled answers use `calculator_exact`; all three failures remain in the LLM path and make no tool call. Of the 37 calls, 24 use the structured fallback route. The misses are:

| Actual question | Recipe-derived reference | Actual answer | Failure |
|---|---:|---|---|
| How many Wild Armor Trim Smithing Template do I need to craft 16 Wild Armor Trim Smithing Template? Reply with the number only. | 8 | “I do not know.” | No calculator call |
| How many Leather do I need to craft 6 Item Frame? Reply with the number only. | 6 | “I do not know.” | No calculator call |
| How many White Wool do I need to craft 2 Green Wool? Reply with the number only. | 2 | “1” | No calculator call; incorrect guessed quantity |

The calculator succeeds when reached; routing still does not cover every supported request. The score evaluates direct recipe batch requirements, not recursive crafting, reusing outputs as inputs, inventory-aware minimum-material planning, or every recipe variant. In particular, the self-template question's reference of 8 counts slots across eight batches; an inventory plan could reuse newly crafted templates and start with one. Its wording needs independent review and the score must be read under the direct-slot definition. The 0/20 false calls were measured on the **development** gameplay set and are not proof of zero false calls for unseen wording.

The preceding run is preserved in `results/verified/tool/`: 28/40 with the tool versus 2/40 without. It illustrates the earlier problems: a 2-banner question was routed with `count=12` and answered 72 wool; a 7-yellow-glass question had a correct tool result of 8 glass but the LLM answered 56. The final path validates quantities against the question and returns the requested ingredient count directly. Because the two runs use different 40-item sets, their 28-to-37 change is descriptive, not a paired estimate of the fix's effect. The paired comparison within the final set is the valid with-tool/without-tool comparison.

## Final demo limits

The final saved demo correctly returns **15 iron ingots** for three hoppers and answers both parts of a compound hopper question. Its transport explanation comes from a specific item-sorter layout and needs manual checking before being treated as a complete explanation of general hopper behavior; it is not covered by the quantity exactness score.

“Can I place grass on bedrock?” now reaches ordinary retrieval instead of being mistaken for a Bedrock Edition request. Its generated answer still claims bedrock does not allow placement of any blocks and cites *Grass Block > Trivia*, which supplies no such support. The question itself is ambiguous between short grass and a grass block, so this demo has no justified binary yes/no gold label. It exposes both ambiguous wording and unsupported explanation. The explicit “in Bedrock Edition” hopper question is correctly routed to a scope refusal. These saved demos follow the compound-query and edition-guard fixes; the later invalid-quantity guard does not change these positive queries, but the demos are not a fresh full benchmark of every final code path.

---

# Historical failure analysis — previous synthetic-pool runs

# Failure analysis — what breaks and why

Every example below is a real output, saved in `results/` unless marked otherwise. Categories were assigned by
reading the outputs (by Claude Code; the team should check them, see `results/retrieval_miss_sample.csv`).

Corrections after Codex's review (`docs/codex_review.md`, 2026-10-07): refusals are now only answers that say
nothing but "I do not know" (hedged answers are judged like any other); tool answers are scored by the number given
for the ingredient asked about, not the first number anywhere; items that share a display name are no longer
resolved silently; and the retrieval metric is called what it is, the source-page hit rate. The numbers below are
the corrected ones.

## 1. Retrieval: why the source-page hit rate stops at about 74%

The final retriever (BM25 + dense with RRF, then the cross-encoder, 256-token chunks) misses the labelled page in its
top 5 for **259 of the 1000** retrieval questions (`results/retrieval_misses.jsonl`, made by `python eval.py misses`).
hit@10 is only about 4 points higher (78%), so most misses are not near misses: something else is going on.
A random sample of 40 misses (seed 1) falls into four groups:

| Group | In the sample | What happens |
|---|---|---|
| The label is too strict | 19 / 40 | The question is answered on another page, and the retriever found that page. |
| The question is broken | 14 / 40 | Template text, off-topic or false-premise questions, or wrong references in the synthetic pool. |
| The question is unanswerable as written | 2 / 40 | It refers to context it does not give ("the dates listed in the 2013-2014 Maps topic"). |
| A real retrieval miss | 5 / 40 | The right page exists and was not retrieved. |

**The label is too strict (about half).** A hit only counts if a chunk comes from the page the question was
*generated from*, but many questions are answered on several pages. "What is the primary function of a Redstone
Comparator?" is labelled with *Java Edition removed features*; the system returned *Redstone Comparator* and
*Redstone components > Redstone comparator*, which are better. "What is a notable characteristic of the Snowy
Mountains biome?" is labelled *Wooded Hills*; the system returned three sections of *Snowy Mountains*.
*Mechanism:* the pool's generator saw one page, but a wiki repeats facts across pages, and our reranker scores
*relevance to the question*, not *being the source page*. So the hit rate understates how often a useful page is
found. It is not a strict lower bound on answer recall either: a hit can be a chunk of the right page that does not
contain the answer. Measuring real recall needs answer-bearing passages marked by hand.

**The question is broken (about a third).** The pool is machine-generated and some generations failed: 5 of the
1000 questions are unfilled templates (`$question`, `What {random.choice(question_types)} {subtopic} in {topic}?`),
others are off-topic ("What is the main purpose of the main() function in Java?"), invent things that are not in
the game ("the Lead sound ... indicates a Lead ore block"; "how bees behave when a player uses /setworldspawn"), or
come with a wrong reference ("the Nether Fortress is typically found in the Warped Forest biome"). No retriever
can "hit" these. *Mechanism:* the pool was generated by an LLM with no filtering for faithfulness.

**Real misses (about 1 in 8 misses, so roughly 3% of all questions).**
- *Near-duplicate pages:* "What mob was added in beta 1.13.0.4 but is not included in the behavior pack?" is on
  *Bedrock Edition unused features*; all top results came from *Bedrock Edition removed features*, a page with the
  same structure and vocabulary. Both embeddings and BM25 see almost the same text.
- *The answer is a minor fact on a page about something else:* "What type of entity is featured in the promotional
  artwork for the first Caves & Cliffs update?" (answer: a cat, on the *Cat* page). The question's words (Caves &
  Cliffs, artwork) point to other pages; the page's main topic (cats) is not in the question.
- *Vague question:* "What is a rare bug that can occur in Minecraft?" (the "Minceraft" title screen, *Easter eggs*):
  the question is too vague for any retriever.

**What the numbers say about the variants** (`results/RESULTS.md`): BM25 alone is 5–8 points of hit@5 below
dense retrieval at every chunk size. RRF fusion of the two changes hit@5 by +2.5, +0.8 and −0.8 points over dense
alone (128 / 256 / 512 tokens): fusing with a clearly weaker ranker helps little. Each hit@5 has a 95% interval of
about ±2.7 points, so none of these three differences is clearly beyond noise (a paired test would need per-question
results, which `eval.py retrieval` does not save). The cross-encoder helps most at rank 1 (hit@1 +4.4 to +5.7 points over
hybrid), because it reads the question and the passage together instead of comparing two separately computed
vectors, so it is better at putting the best passage first. Codex's 100-question reproduction subset
(`results/codex_review/retrieval.json`) found dense and reranker tied at hit@5 (78/100 each), so the reranker's
advantage over dense alone is small and not established; its gain over hybrid at rank 1 is the consistent part.
Chunk size changes hit@5 by less than 1 point, inside the 95% interval:
wiki sections are short, so most chunks end at a section boundary long before the cap (median chunk about 90 tokens
at every size).

## 2. Answers: what goes wrong in each variant

From `results/answers.jsonl` (100 held-out questions × 3 variants; judge verdicts checked against hand labels in
`results/judge_validation.json`).

**No retrieval: confident and wrong.** The closed-book model never says it does not know (0 refusals), and about a
quarter of its answers deny the question's premise (27 of 100 contain phrases such as "there is no", "does not exist"
or "is not a"): "Badlands are a biome that exists in the Nether, not in the Overworld";
"Magma carpet is not a trap in Minecraft ... it is a decorative block"; "there is no official biome called Snowy
Taiga Hills". Only 16% of its answers match the reference. *Mechanism:* a 4B model has seen little detailed Minecraft
text and fills gaps with fluent guesses; without passages nothing tells it that it is guessing.

**With retrieval: right more often, but it refuses a lot.** Hybrid + reranker answers 69 of 100 questions and 49% of
those match the reference (34% of all questions); dense-only answers 60 (53%). Of the 31 reranker refusals, the
labelled page was among the 5 passages in 16 cases. A further 4 reranker answers (2 dense) are *hedged*: they make
claims and then say they do not know the rest. Some refusals are right:
- 6 questions are real chemistry (isotopes, atomic numbers), generated by the pool from the Minecraft Education
  *Element* page. The wiki does not contain the answers, so "I do not know" is the correct reply.

Others are over-cautious; the 4B model does not connect a passage to an oddly worded question:
- "What type of operator is used to compare two values in the Bedrock Edition's PATHCOMMAND?" The first passage is
  *Argument types > Bedrock Edition > CommandCompareOperator*, whose text is "Must be one of <, <=, =, >=, and >."
  (exactly the reference answer), but the question calls it "PATHCOMMAND" and the model refuses.

*Mechanism:* the prompt says to answer only from the passages and otherwise reply "I do not know"; a small model
follows the second half too eagerly when the wording differs from the passage. This is the price of the low
hallucination rate.

**The reranker's gain shows up as fewer refusals.** Compared with dense-only, the reranker refuses 9 fewer
questions (31 vs 40) while its accuracy on answered questions is about the same (49% vs 53%). The paired difference in judge
score (+0.04, 95% CI −0.03 to +0.11) is not significant with 100 questions; the paired BERTScore difference (+0.043,
CI +0.005 to +0.083) is. *Mechanism:* the cross-encoder puts the passage that contains the answer higher in the top 5
(hit@1 61% vs 57% in the retrieval ablation), so the model more often finds something it can answer from.

**Why BERTScore ranks closed-book first.** Over all 100 questions, BERTScore F1 is 0.36 for closed-book but 0.28 for
the reranker, the opposite of the judge. Over *answered* questions only, the order flips (0.47 reranker, 0.36
closed-book). *Mechanism:* BERTScore measures token-embedding similarity to the reference. "I do not know." shares
almost nothing with any reference, so every refusal scores very low, while a fluent wrong answer about the same
topic shares many words with the reference and scores well. BERTScore measures similarity, not truth, which is why
it is paired with the judge.

**Faithfulness: mostly grounded, with typical slips.** The faithfulness judge rates 59 of 68 reranker answers as
fully supported (87%; one more verdict could not be parsed and is not counted), but it is lenient: on 16
hand-labelled answers it missed 4 of the 5 that were only partly supported, so the real rate is lower (11 of 16 in
that sample). All 6 hedged answers, which the first version never checked, were rated only partly supported. The
slips found:
- *Citing a neighbouring passage:* "Design F ... is composed of AND, OR and NOT gates [4]" cites a passage about the
  XOR gate's Design F for a question about the XNOR gate.
- *Repeating the question's premise:* "the groaning sounds ... trigger the zombie's pursuit of the player" is in the
  question, not in the passage (zombies pursue on sight).

**The judges themselves.** A one-step 1–5 judge (the first run, `results/answers_run1_summary.json`) called 87 of 100
closed-book answers fully correct, including plainly wrong ones, and agreed with hand labels on only 14 of 36. The
final judge first writes down the reference fact and the answer's claim, then decides; it agrees with hand labels on
27–28 of 36, equally across the three variants (Cohen's kappa 0.51–0.64). Its typical error is calling a partial
answer correct. Running the judge again can change one or two verdicts (temperature 0 and a fixed seed are not
fully deterministic on a GPU). The judge is the same model as the generator, so it may favour its own style; the
hand labels are the check on that, with two limits. The run-1 labels were used to choose the judge, so agreement on
them is calibration, not validation; and the run-2 labels share 12 question texts with run 1 (different answers,
since run 2 was generated again), so they are not a fully independent set. All labels were made by Claude Code; an
independent check by the team, with fresh examples and the source passage at hand, is still needed.

## 3. The crafting tool: a first design that failed, and why

The first design offered the craft tool in the same prompt as the five passages, with an instruction to call it for
crafting amounts (`results/tool_run1_before_fix.json`, 40 test questions). It reached only **11/40** with the tool
(3/40 without). The first scorer took the first number anywhere in the answer and reported 15/40 and 2/40: it
counted 4 refusals as correct because they repeat the requested count ("I do not know how many Jungle Planks are
needed to craft 10 Jungle Buttons"), and missed "9 Wooden Shovel requires 18 sticks." (correct, 18). What happened in
the 40 tool-enabled answers:

| Outcome | Count |
|---|---|
| Real tool call, right answer | 11 |
| Real tool call, wrong product passed (`purple dye` for Purple Wool, `stained glass` for Brown Stained Glass) | 2 |
| Real tool call, result misread ("20" sand for 5 Orange Concrete Powder; the tool said 4) | 1 |
| No call: answered "I do not know" from the passages | 20 |
| No call: wrote the call as plain text, e.g. `[craft tool]{"item":"diorite_wall","count":11}` | 6 |

*Mechanisms.* (1) The system prompt said "use only the passages; otherwise say you do not know", and five long
passages pushed the 4B model to that rule instead of the tool. On the dev questions, with the passages in the prompt
it called the tool for 12 of 40 (even after the tool instruction was reworded); given only the question, for 35 of
40. (2) The prompt told the model to cite the tool as `[craft tool]`, and the model imitated that text format instead
of emitting a real tool call. (3) The question names both an ingredient and a product, and the
model sometimes passed the ingredient.

*Fix.* A two-step agent (`mcqa.plan_tools`): the model first sees only the question and may call the tool (native
tool calling, up to three rounds); if it calls nothing, a second prompt forces a yes/no decision as JSON constrained by
a schema; then the final answer is written from the passages plus the tool results, with no tools offered. The tool
also returns a ready-made sentence ("To craft 5 Orange Concrete Powder you need 4 Sand, ... in total"), the schema
says the item is the product, and the prompt gives one worked example (hoppers, an item in neither question set).
All of this was tuned on 40 **dev** questions about other items (38/40,
`results/tool_dev_before_citation_fix.json`), and the test questions were run afterwards: **33/40**
(`results/tool_run2_before_citation_fix.json`). The demo then showed that the final answer cited an unrelated
passage for numbers that came from the tool ("To craft 3 hoppers, you need 15 iron ingots [5]", where [5] was about
iron armour; a demo run, not saved), so the answer prompt now asks for `[tool]` as the source of tool facts. That
change came from the demo, not from test errors, and dev and test were both run again: **38/40** dev, **35/40** test
(`results/tool_run3_before_name_fix.json`).

Codex's review then found that the game's English names are shared by several items: every armor trim template is
"Smithing Template", every disc "Music Disc", every banner pattern "Banner Pattern", and the lookup silently took one
of them (the Wild template, the Ward disc, the Skull pattern). Two test questions asked for "Smithing Template" and
meant the Coast and Ward templates; the tool computed the Wild recipe, whose amounts happen to be the same, so both
were scored right for the wrong reason. Now a shared name returns an "ambiguous" error with the options, the items
get specific names ("Coast Armor Trim Smithing Template"), and the test was run once more with those names:
**33/40** (`results/tool.json`; 82.5%, 95% CI 68.0–91.3), 1/40 without the tool, no false calls. This is the final
result. Every earlier run is kept; the differences between them (33–35) are two questions.

**What still fails (7 of 40 test questions):**
- *No call at all* (6): e.g. "How many Iron Ingot do I need to craft 3 Bucket?", "How many Melon Slice do I need to
  craft 15 Melon Seeds?", "How many Diamond do I need to craft 12 Coast Armor Trim Smithing Template?". Neither the
  native tool call nor the JSON fallback fired; the answer step, which only has passages, says "I do not know" or
  guesses ("84" for the template; the answer is 42).
- *Wrong count passed* (1): for "How many Honeycomb do I need to craft 15 Honeycomb Block?" the model called
  `craft(item="honeycomb block", count=90)`; the right call (count 15) gives 60.

Codex's own small live check (`results/codex_review/live_summary.json`, 8 differently worded recipe questions) found
the same weaknesses: 6/8 correct with the tool and 1/8 without (scored there by the first number in the answer);
"How much iron does a hopper need?" made no call,
and for two anvils the tool returned the right numbers but the answer still said "I do not know". Phrasing that
differs from "How many X do I need to craft N Y" is the main open problem.

The final agent made **no** false tool call on 40 ordinary questions (1 of 40 on the dev side, before the citation
fix: "What is one of the items that can be crafted at a Cauldron?", which is close to a crafting question).

**Corpus coverage is part of why the tool matters.** The corpus has no *Hopper*, *Crafting* or *Cinnabar* page (pages
were chosen by how often the question pool asks about them), so for "How many iron ingots do I need to craft 3
hoppers?" the five retrieved passages are about anvils, iron farms and achievements. The answer is right only
because the tool reads Mojang's recipe file (`docs/demo_output.md`).
# Latest continuation — frozen before/after comparison

`results/improvement_review/` preserves a separate 28-case study and 88 actual responses from the source before
and after the latest changes. The dataset was selected before generation; only dev cases guided the generic
two-clause recipe parser. Test recipe quantities changed from 5/6 to 6/6; explicit canonical/two-clause forms
became direct calculator calls instead of model planning. This is direct ingredient arithmetic, not trained
reasoning. Only six recipe test products are involved, and recipe structures can overlap across item IDs.

General factual accuracy did not demonstrate an improvement: automatic test dense 7/8 → 6/8 and rerank 7/8 →
7/8. The saved analysis notes identify apparent false partial judgments and an alternate valid Wolf passage that
does not contain the exact gold quote. Original automatic labels remain intact. A private-world-health response
correctly declined the exact value while adding general guidance, so the strict bare-refusal metric rejected it.

Compound explanations remain a concrete failure: the Acacia Sign answer gives the correct six-plank quantity but
claims a crafting table is not needed and that planks need one. The quantity score does not grade those claims.
Other compound requests still pay native tool planning and generation, around 11 seconds in this small study.
No final test failure was used to tune the implementation afterward. See `results/improvement_review/analysis_notes.md`
and `human_check.csv` for inspectable examples and independent review.

Scope filtering is a heuristic, not complete Java 26.3 verification. It preserves raw pinned sources but removes
obvious history/other-edition evidence in a conservative passage view. In already inspected diagnostics it loses
two useful follow-up quotes from mixed paragraphs. Dense embeddings still contain original edition clauses while
BM25/reranking/generation see the filtered view. These limitations remain explicit rather than being hidden by
a claim that filtering makes every answer current or correct.

---
