# MCQA: Minecraft Wiki Q&A

A local question-answering system targeting Minecraft Java 26.3 gameplay. It retrieves from 312 real Minecraft Wiki pages (816,730 words,
including several editions and the game's history), cites the passages it used, and calls a crafting calculator built
from Mojang's official **Java Edition 26.3** recipe files when a question asks how many items a craft needs.

Term project for *Natural Language Processing with Deep Learning*. Everything runs locally on one laptop: retrieval on
the CPU, the language model in Ollama (tested on a laptop RTX 5070 GPU).

The verified source/results package is `dist/MCQA_submission_2026-10-07.zip`, with a SHA-256 sidecar and an internal
file manifest. It includes this README, source, tests, pinned pages, benchmark data, audit/work records and results.
Models and rebuildable runtime data are excluded; follow setup below before running inference on another machine.

```
                ┌─► dense: bge-small-en-v1.5, cosine (top 50) ─┐
question ───────┤                                              ├─► RRF, k=60 ─► top 20 ─► cross-encoder ─► top 5 passages ─┐
   │            └─► sparse: BM25 (top 50) ─────────────────────┘                          (ms-marco-MiniLM-L6-v2)         │
   │                                                                                                                       ▼
   └─► step 1, plan: question + matching one-craft recipes ──► craft(item, count) ──► tool results ──► step 2, answer:
       (native tool calls, up to 3 rounds; if none, a JSON-schema        (Mojang 26.3 recipes)            qwen3:4b-instruct
        yes/no decision as a fallback)                                                                    passages + tool
                                                                                                          results, ≤ 3 sentences,
                                                                                                          cites [1]..[5], [tool]
```

## How it works

1. **Corpus.** 312 Minecraft Wiki pages (about 817,000 words), plain text from the wiki API, each pinned to a revision
   id (`docs/corpus_inventory.csv`). Pages were chosen as the 400 titles the question pool asks most about.
2. **Chunking.** Paragraph-aligned chunks that never cross a section boundary, at most 256 tokens counted with the
   embedding model's own tokenizer (including `[CLS]`/`[SEP]`), each starting with `Page > Section` so the chunk says
   where it is from. A paragraph over the budget is cut into word windows; a "word" over the budget is halved.
   No overlap. Normal paragraphs are preserved; oversized paragraphs or commands can split sentences.
3. **Retrieval.** Dense (bge-small-en-v1.5 with its query instruction, cosine similarity on normalized vectors) and
   BM25 (lower-cased alphanumeric tokens, no stemming or stop words) each return 50 chunks; reciprocal rank fusion
   (k = 60) merges them; a cross-encoder reads (question, chunk) pairs for the top 20 and keeps the best 5.
4. **Crafting tool (agentic step).** Step 1: the LLM sees the question and matching one-craft recipes and may call `craft(item, count)`, which
   computes the ingredients from Mojang's official Java 26.3 recipe files; it may call it again (up to 3 rounds), for
   example for an ingredient's own recipe. If it makes no call, a second prompt forces a yes/no decision as JSON
   constrained by a schema. Step 2: a standalone explicit quantity query receives the matching calculator quantity
   directly; other questions use the LLM with passages and tool results. Facts cite their source
   (`[1]`–`[5]` for passages, `[tool]` for the craft tool).
5. **Model.** qwen3:4b-instruct (4B parameters, Q4_K_M) through Ollama, temperature 0 and a fixed seed. Prompts target
   current Java gameplay; explicit other-edition requests are rejected before retrieval or recipe calls.

The planner also receives matching official one-craft recipes to ground item knowledge; it still selects the product
through native or structured model output. Explicit "How many X do I need to craft N Y?" requests constrain matching
tool calls to the user's N, preserving the original model arguments in the trace. A successful matching direct
ingredient amount is returned as `calculator_exact` for standalone quantity queries. Ambiguity asks for clarification. If a successful
calculator result is followed by a bare model refusal, the calculator's complete validated recipe is displayed with
`[tool]`; `answer_mode=calculator_fallback` records this distinction. This is deterministic arithmetic, not trained
model arithmetic. Zero, negative, fractional and Boolean quantities are rejected.

## Key decisions and why

| Decision | Why | Evidence |
|---|---|---|
| Chunk size 256 tokens | 128 / 256 / 512 tied on retrieval (rerank source-page hit@5 74.4 / 74.1 / 74.5 %, 95% CI about ±2.7): wiki sections are short, so most chunks end at a section boundary (median about 90 tokens at every size). 256 gives the generator more context per passage than 128 and costs less reranking time and prompt length than 512. | `results/retrieval.json` |
| bge-small-en-v1.5 | Small (33M parameters) so it runs on a CPU; strong English retrieval model for its size; 512-token limit fits every chunk size tested. | — |
| BM25 + dense with RRF, then a cross-encoder | BM25 is meant to catch exact names (item ids, version numbers) that embeddings blur, and RRF merges ranks without tuning score scales; in our data, though, BM25 alone is 5–8 points below dense and fusion changes hit@5 by only −0.8 to +2.5 points. The cross-encoder reads question and passage together, which mainly improves the top rank. | At 256 tokens: hit@1 dense 57.4 %, hybrid 55.4 %, + reranker 61.1 % |
| Two-step tool agent | Offered together with the passages, the tool was called for only 14 of 40 crafting questions (11/40 correct). Shown the bare question first, the model called it for 35 of 40 dev questions; the JSON fallback catches most of the rest. | `results/tool_run1_before_fix.json`, `results/tool_dev.json` |
| Decomposed LLM judge | A one-step 1–5 judge called 87 of 100 closed-book answers fully correct and agreed with hand labels on only 14 of 36 answers. Writing down the reference fact and the answer's claim before the verdict raised that to 27–28 of 36. | `results/judge_selection.json`, `results/judge_validation.json` |
| Same 3-sentence limit for every variant | Without it, closed-book answers were 4× longer than RAG answers, which lowers BERTScore and sways an LLM judge. | `results/answers_run1.jsonl` |

## Install

Needs Python 3.14 (tested with 3.14.7) and [Ollama](https://ollama.com) (tested with 0.34.4). Retrieval needs no GPU;
Ollama uses a GPU if there is one (it also runs on a CPU, more slowly; not timed here).

```bash
python -m venv .venv
```

```bash
.venv\Scripts\pip install -r requirements.txt
```

```bash
ollama pull qwen3:4b-instruct
```

(On macOS/Linux use `.venv/bin/...` instead of `.venv\Scripts\...`.) The embedding, reranker and BERTScore models
download from Hugging Face on first use (about 0.5 GB in total).

## Build the data and the index

```bash
.venv\Scripts\python mcqa.py fetch
```

Downloads the question pool (119 MB), Mojang's 26.3 recipes (the client.jar is checked against Mojang's SHA-1 and
not kept) and the wiki pages. `data/pages.jsonl` is already in the repository, so the saved pages are **not**
downloaded again and you get exactly the page revisions we used (listed in `docs/corpus_inventory.csv`); only the 14
pool titles that have no wiki page are looked up again (about a minute). Delete `data/pages.jsonl` to fetch the
current wiki instead.

```bash
.venv\Scripts\python mcqa.py index 256
```

Chunks the pages and embeds the chunks (a few minutes on a CPU). The retrieval ablation also needs `index 128` and
`index 512`.

## Run the demo

Ollama must be running (open the Ollama app, or run `ollama serve`).

```bash
.venv\Scripts\python demo.py "How many iron ingots do I need to craft 3 hoppers?"
```

Without a question, `demo.py` asks for questions until you enter an empty line. It prints the retrieved passages
(page > section), any craft-tool calls with their results, and the answer.

The first gameplay answer loads the cached embedding/reranker and may also load Ollama's generator. Keep one
interactive session open during the presentation to reuse those models. The demo immediately shows loading/working
status and elapsed query time. Standalone validated quantity answers skip further planning and Wiki retrieval;
they cite `[tool]` and keep the actual calculator trace. Compound/multistep questions retain the full pipeline.

For faster general gameplay Q&A without the crafting calculator:

```bash
.venv\Scripts\python demo.py --no-tool
```

This uses the existing evaluated no-tool answer path, so it also bypasses crafting planning. Run the default demo
when demonstrating recipe tools. Small latency probes are saved separately in `results/latency_review/`; earlier
quality metrics keep their original source-version labels.

## Run the evaluation

| Command | What it does | Needs | Time here |
|---|---|---|---|
| `eval.py retrieval` | source-page hit@1/5/10 and MRR@10 for 4 retrievers × 3 chunk sizes, 1000 questions | indexes 128/256/512 | ~35 min (CPU) |
| `eval.py misses` | the questions the final retriever misses, for the failure analysis | index 256 | ~5 min |
| `eval.py answers` | no retrieval vs dense vs hybrid + reranker on 100 held-out questions: LLM judge, faithfulness, BERTScore | Ollama | ~40 min |
| `eval.py summary` | re-classify refusals, judge any answer not yet checked for faithfulness, recompute `answers_summary.json` (incl. paired bootstrap intervals) | Ollama, if a check is missing | seconds |
| `eval.py judgecheck` | agreement of the LLM judges with the hand labels in `results/*_labels_*.jsonl` | Ollama | ~3 min |
| `eval.py tooldev` | the crafting questions the tool prompts were tuned on (with vs without the tool) | Ollama | ~15 min |
| `eval.py tool` | 40 held-out crafting questions with vs without the tool, plus false calls on 40 other questions | Ollama | ~15 min |
| `eval.py rescore` | score every saved tool run again with the current answer parser | — | seconds |
| `eval.py report` | `results/RESULTS.md` from the saved JSON files | — | seconds |

Run each as `.venv\Scripts\python eval.py <command>`, for example:

```bash
.venv\Scripts\python eval.py report
```

The exact questions of each experiment are saved as `results/questions_*.jsonl`. Answers are generated at
temperature 0 with a fixed seed, but GPU inference is not bit-for-bit deterministic, so a re-run can change a few
answers or verdicts. Self-checks for the chunker, RRF and the craft tool:

```bash
.venv\Scripts\python -m unittest test_mcqa -v
```

## Results

Run all regression checks with `.venv\Scripts\python.exe -m unittest discover -v`.

The current source-grounded benchmark is in `data/java_benchmark.jsonl`: 60 new questions, including 50 answerable
facts across 25 pinned pages and 10 expected refusals. Exact reference quotes and revision links are included.
Development (20) and test (40) questions use disjoint answerable source pages. The dataset is AI-curated and
source-checked, with `human_reviewed=false`; independent team checking remains required. Test references are never
added to retrieval or training. See `docs/benchmark_sources.md`.

```powershell
.venv\Scripts\python.exe scripts\preflight.py
.venv\Scripts\python.exe scripts\benchmark_eval.py validate
.venv\Scripts\python.exe scripts\benchmark_eval.py report --split test
.venv\Scripts\python.exe scripts\benchmark_eval.py run --split dev --output results/verified/dev_repeat
.venv\Scripts\python.exe scripts\benchmark_eval.py run --split test --output results/verified/test_repeat
```

The evaluator resumes saved complete rows and refuses to mix changed code/data/model configurations in one run.
Reuse the same `--output` directory to resume an unchanged run; choose a new directory after changing a configuration.
Report generation preserves an existing human-check CSV. Gameplay dev/test used the frozen `source_v1` code;
the later tool corrections and usability fixes have their own versions. `scripts/resume_gameplay.py --split test`
loads the saved v1 modules and verifies their original configuration to resume that specific experiment.
It uses cached models only. Indexing and the first demo populate the embedding/reranker caches. Before the first
benchmark run, cache its BERTScore model once:

```powershell
.venv\Scripts\python.exe -c "from transformers import AutoModel, AutoTokenizer; AutoTokenizer.from_pretrained('distilroberta-base'); AutoModel.from_pretrained('distilroberta-base')"
```

Run `scripts/preflight.py` again after the initial setup. Model downloads require internet once; inference has no paid API calls.

`results/verified/dev/` and `results/verified/test/` contain raw answers/rankings, source evidence, BERTScore,
correctness and faithfulness judgments, configuration hashes/model revisions, summaries and blank human-check CSVs.
Factual metrics exclude expected-refusal cases; refusal performance has its own denominator. Retrieval evidence
hits require the actual supporting quote in a passage, not just a matching page title. The judge still shares the
generator model; automatic correctness is not human-certified accuracy. Pure factual refusals receive zero credit
even if the judge mistakenly marks them correct; the original verdict remains in the raw answer.

**Source-grounded test results** (34 answerable questions plus 6 expected refusals; all three variants use the same questions):

| Variant | Correct | BERTScore F1 (facts) | Supporting quote in top 5 | Correct negative refusal |
|---|---:|---:|---:|---:|
| No retrieval | 9/34 | 0.294 | — | 5/6 |
| Dense | 27/34 | 0.493 | 31/34 | 5/6 |
| Hybrid + reranker | 26/34 | 0.451 | 30/34 | 6/6 |

Retrieval improved both required metrics. Reranking did not establish an advantage over dense retrieval:
paired judge-score difference −0.029, 95% CI [−0.162, 0.103]. Development scores and complete intervals are in
`results/verified/dev/RESULTS.md` and `results/verified/test/RESULTS.md`. See `docs/final_validation.md` for failure analysis and source versions.

The current crafting regression uses 40 new product IDs, excluding earlier dev/test items and explicit development
examples and all seed-17 diagnostic products. Results are under `results/verified/tool_final/`:
**37/40 (92.5%) with tools versus 1/40 (2.5%) without**. All 37 successful answers used `calculator_exact`;
3 failures made no tool call. False calls were 0/20 on separate fixed non-recipe development cases.
The frozen tool source is `source_v2`; later scope/compound-question checks are documented separately.

```powershell
.venv\Scripts\python.exe scripts\tool_benchmark.py --seed 29 --output results/verified/tool_repeat
```

The earlier `results/verified/tool/` run scored 28/40 vs 2/40 and exposed count/answer corruption; it is diagnostic
evidence, rather than the final holdout after those failures were inspected.
It records numeric accuracy, actual tool calls, calculator fallback modes and false calls on separate non-recipe
development questions. Its saved recipe slots make quantity references inspectable.

### Historical synthetic-pool experiments

All numbers come from the files in `results/`; `results/RESULTS.md` has every table, and
`docs/failure_analysis.md` explains what breaks and why.

**Retrieval ablation** (1000 pool questions; metric: source-page hit rate, i.e. a chunk from the page the question
was generated from is in the top k. It is not answer recall: many questions are also answered on other pages, and a
hit need not contain the answer. hit@5 has a 95% CI of about ±2.7):

| Chunk size | Dense | BM25 | Hybrid (RRF) | Hybrid + reranker | Reranker hit@1 / MRR@10 |
|---|---|---|---|---|---|
| 128 | 70.8 % | 65.8 % | 73.3 % | 74.4 % | 61.9 % / 0.670 |
| **256** | 72.5 % | 65.0 % | 73.3 % | **74.1 %** | 61.1 % / 0.668 |
| 512 | 73.0 % | 65.0 % | 72.2 % | 74.5 % | 60.8 % / 0.668 |

(hit@5 unless marked.) The reranker gives the best hit@1 at every size; chunk size makes no measurable difference
because wiki sections are short. Codex's 100-question reproduction subset found dense and reranker tied at hit@5
(`results/codex_review/retrieval.json`), so the reranker's edge over dense alone is small.

**Answer quality** (100 held-out questions, same questions for every variant; metrics: LLM-as-Judge and BERTScore):

| Variant | Correct (judge) | Judge score | Refused | Correct, of answered | BERTScore F1 (all / answered) | Faithful (judge) |
|---|---|---|---|---|---|---|
| No retrieval | 16 % | 0.25 | 0 | 16 % | 0.359 / 0.359 | — |
| Dense only | 32 % | 0.40 | 40 | 53 % | 0.236 / 0.478 | 83 % of 60 |
| **Hybrid + reranker** | **34 %** | **0.44** | 31 | 49 % | 0.279 / 0.466 | 87 % of 68 |

"Refused" counts answers that are only "I do not know"; 2 dense and 4 reranker answers are hedged (claims plus
  "I do not know") and are judged like other answers. The faithfulness judge is lenient (it missed 4 of 5 partly
supported answers in an AI-labelled sample), so these rates may overestimate support.

Paired over the same questions, retrieval beats no retrieval clearly (judge score +0.19, 95% CI +0.085 to +0.295),
while hybrid + reranker vs dense is +0.04 (CI −0.03 to +0.11), not significant with 100 questions. BERTScore over
*all* questions prefers no retrieval only because "I do not know." scores low against any reference; over answered
questions it agrees with the judge. The judge agrees with hand labels on 27–28 of 36 answers (Cohen's kappa
0.51–0.64; `results/judge_validation.json`); these labels were made by Claude Code and the run-1 set was also used to
choose the judge, so this is calibration rather than independent validation.

**What these numbers do and do not show.** The references come from a synthetic question pool, not from verified
Java 26.3 facts, and the corpus covers every edition and the game's history: by a word search, 13 of the 100 answer
questions and 133 of the 1000 retrieval questions name Bedrock, Education, Pocket, Console or Legacy (Codex's broader
count: 19 and 163). So "correct" means "agrees with the pool's reference answer", a comparison between variants on
the same questions, not a measured accuracy on current Java gameplay. See `docs/codex_review.md`.

**Crafting tool** (40 held-out "how many X for N Y" questions with the gold number computed from the recipe files):

| Variant | Correct | Accuracy [95% CI] | Tool called |
|---|---|---|---|
| Hybrid + reranker, no tool | 1/40 | 2.5 % [0.4, 12.9] | — |
| First design: tool offered alongside the passages | 11/40 | 27.5 % | 14/40 |
| **Final two-step agent** | **33/40** | **82.5 % [68.0, 91.3]** | 33/40 (10 by the fallback) |

The final agent called the tool for none of 40 ordinary questions. The prompts were tuned on 40 separate dev
questions (38/40). An earlier test run gave 35/40, but two of its questions used the shared name "Smithing
Template", which the tool resolved to the wrong template (with the same amounts); with the names made specific the
planner skipped one of them. Answers are scored by the number given for the asked ingredient; refusals never count. Without the tool the model almost never knows exact recipe amounts, and several test items
(Cinnabar, Sulfur and Poplar blocks) have no page of their own in the corpus.

## Limitations

- **The historical evaluation questions are synthetic.** They come from an LLM-generated pool: some are broken (template text,
  off-topic chemistry, false premises) and some references are wrong or outdated (the pool predates Java 26.3).
  The retrieval metric treats the question's source page as the only right page, so it is a source-page hit rate,
  not answer recall.
- **The hand labels used to check the judges were made by Claude Code,** not by the team; the team should check
  them (`results/judge_labels_*.jsonl`, `results/faithful_labels_run2.jsonl`) and grade `results/judge_check.csv`.
- **The judge is the same model as the generator** (qwen3:4b-instruct) and may favour its own answers; it is
  lenient on partial answers and on partly supported answers.
- **A small generator refuses often** (31% with the reranker), sometimes when the passage does contain the answer.
- **Scope.** Recipe files are pinned to Java 26.3. General answer prompts target current Java gameplay and reject
  explicitly different-edition questions, but the underlying Wiki corpus remains mixed-edition and historical.
  The new source-grounded benchmark checks selected current gameplay facts, not every version-specific mechanic.
- **Hand labels overlap:** the two correctness label sets share 12 question texts, and run 1 was used to pick the
  judge.
- **Corpus coverage:** the 312 pages were chosen by how often the question pool asks about them, so common pages
  such as *Hopper* or *Crafting* are missing; the craft tool covers recipe questions, but other questions about
  missing pages cannot be answered.
- **The craft tool** handles crafting-table recipes (shaped and shapeless) only and uses an item's main recipe. An
  ingredient given as an item tag is shown as "any Planks (e.g. Oak Planks)", but one given as a plain list of
  alternatives is shown as its first item only (e.g. "White Wool" where any wool colour would do). A name shared by
  several items ("smithing template", "music disc", "banner pattern") requires clarification; the planner stops
  rather than guessing a variant. Quantity inputs must be positive integers.
- **Question wording.** Tool use was tuned on "How many X do I need to craft N Y?" questions; other wordings
  ("How much iron does a hopper need?") sometimes get no tool call (`docs/failure_analysis.md`).

## Files

| File | What it is |
|---|---|
| `mcqa.py` | the system: fetching, chunking, the four retrievers, the craft tool, answering with the tool loop |
| `eval.py` | retrieval ablation, answer evaluation (BERTScore + LLM-as-Judge), tool ablation, report |
| `demo.py` | command-line demo |
| `test_mcqa.py` | unit tests |
| `scripts/judge_selection.py` | how the LLM judge was chosen: five judge set-ups against hand labels → `results/judge_selection.json` |
| `results/RESULTS.md` | every result table, generated by `eval.py report` |
| `results/*.json`, `*.jsonl` | raw results: per-question answers, verdicts, tool calls; `*_run1*` and `*_before_*` files are earlier runs kept for the record |
| `results/questions_*.jsonl` | the exact evaluation questions of each experiment |
| `results/*_labels_*.jsonl`, `retrieval_miss_sample.csv` | hand labels (made by Claude Code, to be checked by the team) |
| `results/judge_check.csv` | 45 judged answers with an empty column for the team to grade by hand |
| `docs/sources.md` | where every dataset and model comes from, versions, licences |
| `docs/corpus_inventory.csv` | each wiki page with the exact revision used |
| `docs/failure_analysis.md` | what breaks and why, from real misses in the saved results |
| `docs/demo_output.md` | a real demo session: crafting questions (one item with no page of its own), a lore question and an off-topic question |
| `docs/ai_prompt_history.md` | the prompts sent to Claude Code, word for word, for `AI_AUDIT.md` |
| `docs/ai_audit_prompt.md` | the course's standard audit prompt as it was filled in and run |
| `docs/codex_review.md`, `scripts/codex_review.py`, `results/codex_review/` | an independent review by Codex, its harness and raw outputs; its findings 2–5 are fixed (see `docs/failure_analysis.md`) |
| `data/java_benchmark.jsonl`, `docs/benchmark_sources.md` | new question set, exact evidence/revisions, split and provenance |
| `scripts/benchmark_eval.py`, `results/verified/` | source-grounded evaluations with resumable raw rows, two course metrics and human-check sheets |
| `scripts/preflight.py`, `test_eval.py` | local readiness check and evaluation regressions |
| `docs/final_validation.md` | final observed metrics, fixes, source versions, remaining failures and submission requirements |
| `AI_AUDIT.md` | authentic AI activity; team names/contributions and explicitly unaided responses remain for the team |
| `docs/AI_AUDIT_skeleton.md` | preserved original output of the standardized skeleton prompt |

## Licences

Minecraft Wiki text: CC BY-NC-SA 3.0 (`data/pages.jsonl` keeps the title and revision of each page). The question pool
is derived from a CC BY-NC-SA 3.0 dataset. Minecraft recipe data belongs to Mojang. Full client archives and
`data/crafting.json` are excluded and rebuilt from Mojang's servers; evaluation cases retain inspected recipe slots
and quantities. Non-commercial course project.
