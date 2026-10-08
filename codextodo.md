# Codex work record - Minecraft NLP with DL term project

## Standing instructions

- Codex helps build, train, evaluate, debug, and review this project.
- Record every work session and meaningful process in this file: objective, inputs, commands/actions, changes, observed results, decisions, and remaining work.
- Keep completed actions separate from plans and unverified claims. Record failures and corrections; do not invent evaluation scores, training runs, or audit entries.
- Preserve and coordinate with Claude Code's existing work. `claudetodo.md` is Claude's separate record; do not overwrite it.
- The Minecraft application must run locally without paid API calls.
- Current control state: the user's 2026-10-07 command "ok fix for me. make everything to perfection" authorizes implementation corrections, source-grounded benchmarking, fresh evaluation and technical deliverable completion. Preserve prior evidence and do not fabricate human contributions or unaided answers.

## Project requirements already read

Source: `Class NLP with DL/Term Project/PROJECT_INSTRUCTION.pdf` (all eight pages read earlier in this chat).

- Real corpus: at least 50 documents or equivalent, in a language the team can evaluate.
- Token-aware chunking with a justified size.
- CPU-compatible SentenceTransformers dense retrieval.
- At least two approved course evaluation metrics and at least two system variants, with actual saved results and interpretation.
- Runnable repository with README, demonstration script/notebook, and evaluation script.
- `AI_AUDIT.md` using the assignment's exact skeleton prompt: five or more prompt entries, five or more decisions, two or more real AI errors caught, contribution map, and the team's own unaided "What Would Break?" answers.
- Training/fine-tuning is an optional assignment extension, but the user has explicitly included training in Codex's support role. Training scope and success criteria remain to be established. Downloading models or building an embedding index is not a training run.
- Presentation slides are handled separately; the assignment's individual technical Q&A still requires team understanding.

## Pending work

- [x] Review the full implementation and trace retrieval, generation, crafting tools, and evaluation (2026-10-07; findings in `docs/codex_review.md`).
- [x] Verify corpus provenance, extraction structure, size and version/edition limits (312 real pages; mixed editions/history documented; 26.3 recipe pin checked).
- [x] Reproduce tests and index structure/chunk lists; record outcomes (full old retrieval experiment was not rerun).
- [x] Fix confirmed implementation/evaluation issues and finish technical deliverables; model/routing/judge limits and human-only requirements remain explicitly documented.
- [ ] Optional future adaptation: establish a training objective/data split/hardware plan before any agreed training run. No fine-tuning was performed or needed for the mandatory pretrained RAG baseline.
- [x] Run controlled retrieval ablations and two required answer metrics (new dev/test paired variants, BERTScore and LLM judge; raw rows saved).
- [x] Check exact reference quotes/revisions and inspect failures; keep automatic scores explicitly AI-assisted.
- [ ] Team independently verifies references and answer judgments, with its own labels.
- [x] Verify cached local runtime, live demos and historical-source resume command; clean package check follows below.
- [x] Finish README, source inventory, results and failure analysis from observed evidence.
- [x] Maintain authentic AI audit evidence and preserve original skeleton/prompt history.
- [ ] Team supplies real names/contributions and writes explicitly unaided Section 6 itself.

## Process log

### 2026-10-06 - Earlier research in this chat (retrospective summary)

- Read the complete project brief, extracted its requirements, rendered the PDF for inspection, and removed the temporary rendered files.
- Compared tax, labour, university, student-loan, technical, and hobby Q&A topics using source research; the user selected Minecraft as the direction.
- Verified official Minecraft release information and discussed fixing one edition/version for reproducible evaluation.
- Researched development-tool models, local answer models, and CPU-compatible embeddings. The user chose fully local application inference.
- Hardware check: `nvidia-smi --query-gpu=name,memory.total --format=csv,noheader` reported an NVIDIA GeForce RTX 5070 Laptop GPU with 8151 MiB VRAM. RAM/CPU queries through `Get-CimInstance` were inaccessible in this environment.
- Suggested, but did not install or benchmark, Qwen3.5 4B Q4_K_M through Ollama and multilingual-e5-small on CPU. These suggestions do not establish which models the current code actually uses.
- No model training, application evaluation, or implementation changes were performed by Codex during that research.

### 2026-10-06 - Expanded role and work-record initialization

**User instruction:**

> you task is not just review you have to help build,train,evaluate and do not forget to record every process in codextodo.md

**Objective:** establish a project-specific Codex log and inspect the current workspace before further commands.

**Actions and commands:**

- Inspected `C:/Users/guymy/OneDrive/Desktop/NLP/NLPDL` with `Get-Location`, `Get-ChildItem`, and `rg --files`.
- Searched the containing NLP workspace for `AGENTS.md`, `codextodo.md`, and `CLAUDE.md`; no applicable AGENTS/CLAUDE file appeared. An existing `Senior project/codextodo.md` belongs to a different project and was left untouched.
- Read the ponytail skill and applied it to keep future implementation changes focused on actual requirements.
- Read `claudetodo.md` and `requirements.txt`; inventoried data/docs and searched top-level code for retrieval, model, training, and evaluation components.
- Ran `git status --short`; it reported that this directory and its parents are not a Git repository. No Git state was changed.
- Delegated an independent, read-only inventory to a subagent; no models, downloads, training, or evaluations were started.
- Created this `codextodo.md` in the actual project root.

**Observed state:**

- Existing code: `mcqa.py`, `demo.py`, `eval.py`, and `test_mcqa.py`.
- Existing records: `claudetodo.md` and `docs/ai_prompt_history.md`.
- Existing data includes `pages.jsonl`, `crafting.json`, and `chunks_256.jsonl`.
- Code contains dense/BM25/hybrid retrieval, cross-encoder reranking, a local Ollama answer path, a crafting tool, BERTScore, and LLM-as-Judge evaluation.
- Claude's log reports Minecraft Java 26.3 recipe extraction and model downloads. These are handoff claims until independently verified.
- Claude's handoff lists remaining fetching/indexing, evaluation, README, sources, failure analysis, and AI audit work. Files may have changed since that handoff; verify current state before executing follow-up commands.
- Existing model and evaluation choices must be assessed against the current language scope and the request for local operation; no automatic model replacement has been made.

**Outcome:** role and record established; no application code changed, training performed, or evaluation scores claimed.

**Next:** follow the user's next command, coordinate with Claude's current work, and append concrete build/training/evaluation evidence here as work proceeds.

### 2026-10-06 - Survey-only boundary and independent inventory

**User instruction:**

> at the moment you can survey project but wait for me to let you continue

**Scope:** read-only survey of the project, with updates to this required log. Further build/training/evaluation work waits for the user.

**Actions:**

- Received the subagent's independent source-code and artifact inventory. It read the existing files and ran a small standard-library JSON inventory; it did not change files, run models, download anything, train, or evaluate the system.
- Confirmed the implementation currently selects `BAAI/bge-small-en-v1.5` on CPU, `cross-encoder/ms-marco-MiniLM-L6-v2`, and local Ollama `qwen3:4b-instruct`; answer evaluation selects `distilroberta-base` for BERTScore.
- Confirmed the code has dense, BM25, hybrid, and reranked variants, chunk-size comparisons, answer/judge evaluation, crafting-tool evaluation, and question-set saving. The question-set saving code is newer than the handoff note that lists it as unfinished.
- Checked current JSONL corpus counts and existence of index/results/deliverable artifacts with a small read-only Python script. Corpus collection appears to be progressing during inspection: separate observations returned different row counts. These are snapshots, not final corpus counts.

**Survey findings:**

- Latest parsed snapshot: 400 Wiki records, 294 records with non-empty text, and 246 unique usable titles; zero unparsed JSONL lines. These counts are not a validation of content quality or version consistency.
- The 256-token chunks and embedding index exist. Other chunk sizes and actual saved evaluation results remain to be verified.
- The synthetic Q&A pool is present; it must be distinguished from the real Wiki corpus and human-validated reference answers.
- Minecraft Java 26.3 crafting data is present. The handoff claims provenance and SHA-1 verification; independently verify those before treating them as established evidence.
- The required README and AI audit, and planned source inventory/failure analysis, were absent in this survey.
- No model-training/fine-tuning implementation was found in the initial inventory.
- The subagent observed a virtual-environment Python-location warning during its small JSON inventory. Its command succeeded, but interpreter reproducibility should be checked later.
- Model readiness, prior test-pass claims, inference quality, corpus correctness, and evaluation validity have not been independently established by Codex.

**Outcome:** survey recorded. No application code edited, models installed, training performed, or evaluation run by Codex.

**Next:** wait for the user's continuation command.

### 2026-10-07 - Review and evaluation resumed

**User instruction:** "review and evaluate".

**Objective:** independently assess Claude's completed implementation, deliverables, tests, saved experiments, and local inference. Distinguish reproduced evidence from Claude's claims and identify remaining problems.

**Initial actions:**

- Read the current file inventory, README, requirements, Claude handoff, existing Codex log, test file, and evaluation entry points.
- Confirmed that Claude has added corpus/index files for three chunk sizes, saved retrieval/answer/tool experiments, judge-label files, results documentation, and an AI audit skeleton since the prior survey.
- Delegated read-only implementation, evaluation-method, and deliverable reviews to separate agents. They will not edit the project or this log.
- Changed the control state above to reflect the user's continuation; no application code changed.

**Verification plan:** run existing tests, independently check artifact counts/metric arithmetic/splits, inspect source and reference quality, and exercise cached local models on controlled cases. Keep new review results separate from Claude's outputs.

**Status:** in progress; reported completion, scores, and reproducibility are still being verified.

**First verification results and actions:**

- Existing `python -m unittest test_mcqa -v`: 7/7 passed. `pip check`: no broken requirements. Compilation of the application, evaluation, demo, tests, judge-selection and review scripts passed.
- The sandbox prevented the first localhost Ollama connection (`WinError 10013`). Retried the same local read with sandbox escalation; automatic review allowed it. Ollama returned the three cached model tags. No models downloaded.
- Verified runtime Python 3.14.7, torch 2.14.1+cpu; CPU embeddings and GPU inference through Ollama are separate runtimes. The sandboxed venv emits a base-Python location warning while commands still succeed; unsandboxed local checks did not emit that warning.
- Added `scripts/codex_review.py` as an independent review harness. It enforces Hugging Face offline mode and writes only under `results/codex_review/`; Claude's experiments are preserved.
- Ran artifact checks: 400 stored records, 14 missing, 312 distinct real pages, 816,730 words; recipe metadata 26.3, 1010 craftable IDs, 236 tags, 1841 names. Question-pool SHA-256 matches `docs/sources.md`.
- Recomputed all saved answer-summary arithmetic, including paired bootstrap intervals: identical to Claude's summary. Retrieval/answer exact-question overlap and tool dev/test item overlap are both zero.
- Started offline chunk/index verification and a 100-question, four-variant retrieval reproduction subset. Started a separate local live evaluation of eight paired recipe questions and six qualitative demo questions; these are diagnostic cases, not a population accuracy benchmark.

**Confirmed review concerns so far:**

- General corpus/questions mix editions and history, while product scope says Java 26.3. The current synthetic references are not a verified Java 26.3 benchmark; labels were made by Claude rather than the team.
- Six saved answers combine factual claims and uncertainty but the substring abstention detector skips their faithfulness checks.
- The first-number crafting scorer counts four explicit refusals as correct in the historical first tool run. Strict number-only scoring gives 11/40 rather than 15/40 there; final 35/40 vs 1/40 and dev 38/40 are unchanged by that parsing check.
- Duplicate display names silently select one recipe: generic "Banner Pattern" selects Skull, "Smithing Template" selects Wild, and "Music Disc" selects uncraftable Ward. Two ambiguous template questions in the saved tool set hide the identity error behind matching quantities.
- `AI_AUDIT.md` remains a skeleton with 46 FILL IN placeholders and unnamed team members. Its explicitly unaided section remains the team's responsibility.

**Changes:** review harness and this record only; no application/evaluation logic or Claude results altered. Independent runs remain in progress.

**Completed independent evaluation:**

- `scripts/codex_review.py retrieval`: completed in 109 seconds. Rebuilt all three chunk lists identically: 15,076 / 10,128 / 8,592 chunks, maximum token lengths 128 / 256 / 512, no over-budget chunks. Median lengths 88 / 96 / 83 tokens. Embedding arrays have correct row counts and 384 columns, finite values and unit norms. Re-encoding 24 passages differs by at most 1.3411e-7.
- Ran all four retrievers on a seed-7 subset of 100 saved retrieval questions at 256 tokens. Source-page hit@5: dense 78/100, BM25 61/100, hybrid 75/100, rerank 78/100. Saved individual rankings and question subset. This reproduces a subset, not the complete 1,000-question experiment or a new test set.
- `scripts/codex_review.py metrics`: recomputed BERTScore for 12 saved questions x 3 variants on cached CPU model. All 36 scores match their saved four-decimal values (maximum difference 0.0).
- `scripts/codex_review.py live`: completed 16 paired recipe answers plus six qualitative cases through the actual retriever/planner/generator. Eight independently specified recipe quantities: 6/8 correct with tool vs 1/8 without; tool called on 7/8. Milk-bucket quantity for two cakes triggered no tool call. Two anvils returned correct tool numbers but the generator still refused. Hopper wording "How much iron does a hopper need?" also refused without calling. These are small diagnostic cases, not a representative accuracy estimate.
- `scripts/codex_review.py judge`: reran 12 saved correctness judgments; all 12 verdicts match. Forced faithfulness evaluation of all six mixed responses skipped by the current shortcut: all six automatically rated `partly`. This exposes omitted claims but is not independent human validation.
- `scripts/codex_review.py scoring`: strict numeric scoring confirms final tool 35/40 vs 1/40 and dev 38/40; historical first with-tool run is 11/40, with four refusal false positives under the old scorer. Raw changed rows are saved separately.
- Independently demonstrated ambiguous item resolution using cached crafting data and recorded the intended Coast/Ward IDs in the two affected tool questions. Generic display names resolve to a different variant.
- Reviews also identified an unparsed faithfulness verdict included in the checked denominator, judge calibration/validation overlap, and the unsupported claim that source-page hit rate is a guaranteed lower bound on answer relevance.

**Deliverables and decision:**

- Created `docs/codex_review.md` with prioritized findings, exact source locations, independent results, reproducibility limits and recommended next work. New raw artifacts are in `results/codex_review/`; the harness is `scripts/codex_review.py`.
- Core implementation and required metric/ablation coverage are present. Do not call the project submission-ready until scoring/name defects, scoped reference validation and the personal audit are addressed.
- No application code, Claude experiment output, model weights, or `claudetodo.md` changed. No downloads, API charges or model training occurred. Training remains optional under the brief and has no justified experiment objective yet.
- Pending checklist items remain pending wherever this review reproduced only a subset, verified metadata rather than every source fact, or identified unfinished work. Do not mark the full 1,000-question retrieval study / 100-question answer generation as rerun by Codex.

**Outcome:** requested review and independent evaluation completed; implementation corrections and team-authored submission work remain for the next authorized work session.

**Final verification:** recompiled the expanded review harness successfully, inventoried all eleven independent result files, and rechecked Git status (still not a repository). Requested the review report in the Codex file panel; the app returned a queued opening. Final response links the report and this record.

### 2026-10-07 - Corrections and final technical completion

**User instruction:** "ok fix for me. make everything to perfection". User confirmed Claude has finished editing.

**Objective:** repair real defects, strengthen local answers, add an evidence-backed Java benchmark, execute controlled evaluations, and finish reproducible technical documentation. Perfection is a quality target, not a claim of error-free factual performance.

**Initial actions and decisions:**

- Re-read current source, tests, Claude handoff and skill guidance. Found intervening Claude fixes: pure refusals/hedging, null faithfulness counting, quantitative parser, ambiguous item names, renamed source-page metric and rescored/re-run experiments. Current final tool claim is 33/40, not the pre-fix 35/40; verify from current raw files.
- Asked about concurrent edits; user answered "Claude has finished". Proceed without overwriting a live writer.
- Delegated pipeline/tool changes and focused tests to one agent; delegated source-backed benchmark construction to another. Root owns evaluation integration, documentation, audit and this log.
- Further agent creation/reuse hit the session's agent-thread limit; root will implement evaluation integration directly. This does not block the work.
- Requested real team names/contributions asynchronously. Fill only verifiable AI activity from the actual history; leave unaided course answers for the team, as the assignment requires.
- Keep cached models and existing dependencies. No speculative fine-tuning: measure the corrected pretrained RAG first. Keep the mixed-edition synthetic experiment clearly separate from the new scoped benchmark.

**Status:** in progress. Changes, commands, real results and remaining personal work will be appended below.

**Implementation and benchmark progress:**

- Root tightened pure-refusal parsing (citations/newlines do not disguise a refusal; claims plus uncertainty still get checked), validates required judge JSON fields/verdicts with one retry, and makes numeric extraction reject negated/conflicting amounts.
- Added `test_eval.py`: six meaningful checks cover the above bugs, null judgment denominators, answer-bearing evidence rather than same-page matches, and separation of refusal cases from factual BERTScore. All six passed.
- Updated the original review harness to use the current refusal/scorer API; its older outputs remain historical evidence.
- Added `scripts/benchmark_eval.py`: validates exact quote/revision provenance and disjoint dev/test source pages; checkpoints all three no-tool answer variants; records hashes/model digest; computes BERTScore, judge correctness, faithfulness, supporting-evidence retrieval and expected-refusal behavior separately. Human-check CSV is emitted without invented labels.
- Benchmark agent created `data/java_benchmark.jsonl` and `docs/benchmark_sources.md`: 60 unique cases (50 answerable across 25 pages, 5 unavailable-state questions, 5 out-of-scope questions). Dev/test 20/40; source pages disjoint 8/17. Quotes fit individual 128/256/512 chunks. SHA-256 `5a9b8743462d255b2babb29b724b5bb70daa6d673fac9333c2875c0442179795`.
- Ran benchmark validation and compilation successfully. Metadata is explicitly AI-curated/source-checked and `human_reviewed=false`; this improves factual provenance without pretending independent human validation.
- Confirmed Claude's current saved tool score is 33/40 vs 1/40 after specific-name corrections. Earlier raw runs stay available.
- Added `scripts/preflight.py` for a read-only no-download installation/cache/Ollama check. Evaluation uses cached models only.
- Pipeline agent is addressing quantity validation, item IDs, ambiguity termination, intent wording and a calculator-backed fallback when generation refuses despite a successful tool result; development traces are isolated in `results/pipeline_dev/`. Do not tune on the new benchmark test split.

**Additional completion work:**

- Local preflight passed: Python 3.14.7, SentenceTransformers 6.1.0, torch 2.14.1, BERTScore 0.3.13, all cached models/data and Ollama available. `pip check` reports no broken requirements; current helper/evaluation files compile.
- Initialized a local Git repository (no remote or publication). Prior course files, caches and large rebuildable model/index data remain excluded by `.gitignore`.
- Preserved the original standardized AI audit skeleton in `docs/AI_AUDIT_skeleton.md`, then filled actual AI tools, five exact user prompts, AI-owned design reasons and three real errors/corrections in `AI_AUDIT.md`. First patch attempt was rejected because it targeted the same file twice; applied targeted updates successfully. Personal names/contributions and unaided answers remain explicit placeholders, not fabricated content.
- Updated README with benchmark provenance, resume/config controls, cache/setup commands and corrected scope/chunking/ambiguity descriptions. Historical experiments remain labelled historical.
- Added friendly demo startup/data/service errors and normal exit handling; no new dependencies.
- Routing development exposed incorrect model assumptions about recipe ingredients. Pipeline agent is checking generic official-recipe candidate context before model planning rather than per-question hardcoded routing.

**Frozen pipeline and evaluation execution:**

- Pipeline agent completed official-recipe candidate context before native/structured planning, strict positive integer quantities, namespaced IDs, structured ambiguity termination, consistent edition scope and a calculator-backed response only when a successful tool result is followed by a bare model refusal. `answer_mode` distinguishes LLM, clarification, calculator fallback and scope refusal. Retrieval indexes are unchanged.
- Previously failing developer cases now answer hopper 5 iron, two cakes 6 milk buckets and two anvils 6 iron blocks. Non-recipe diamond/cow probes made no tool calls. A developer probe caught calculator fallback overriding an other-edition request; fixed with an early edition guard and a regression test. Earlier failed probes remain in `results/pipeline_dev/`.
- Full test discovery after integration: 19/19 passed; compilation passed. No new dependencies or model changes.
- Froze benchmark and pipeline before new evaluation. Started 20-question development benchmark (three variants, 60 responses) through cached models/local Ollama, saving each completed row. The 40-question test split has not been used for tuning.
- Added `scripts/tool_benchmark.py` for 40 new product IDs, excluding previous saved dev/test products and explicit developer/few-shot examples. Initial exclusion scan failed on old question rows without item IDs; inspected their schema, confirmed current ID-bearing set contains those same questions, and safely skipped the legacy duplicate rows. Fresh item overlap is zero; original experiments remain untouched.
- Demo, README, genuine prompt history and audit evidence updated. Original audit skeleton and historical result files are preserved. No human names, labels or unaided responses have arrived yet.

**Further defect exposed and corrected:**

- Development benchmark completed: 16 factual cases and 4 expected refusals, 3 variants/60 saved rows. Judge-correct none 9/16, dense 13/16, rerank 12/16; factual BERTScore .372/.491/.512. Expected-refusal matches 2/4,4/4,4/4. Raw verdicts/evidence and bootstrap comparisons are saved. No prompt tuning used these results.
- Started the untouched 40-question gameplay test and the seed-17 fresh 40-item recipe test on the frozen v1 process. Each process holds its imported v1 code. Saved that exact source in `results/verified/source_v1/` before further edits.
- The fresh tool run exposed general count/answer corruption: planner changed requested 2 banners to 12, 10 trapdoors to 30, and the generator rewrote correct batch quantities. This is a real new concern justifying another correction; the run remains diagnostic evidence, not a clean final holdout after inspection.
- Added explicit request constraints for unambiguously parsed "How many X ... craft N Y?" questions. Matching tool calls retain the user's N; original model arguments are preserved separately. Successful matching calculator facts are returned directly as `calculator_exact`, so the model cannot multiply or rewrite them. This uses question text and recipe data, not benchmark gold. Natural wording still uses model planning. Main no-tool gameplay path is unchanged.
- Added a regression test proving changed model count is constrained and the correct numeric result bypasses generation. Full discovery now 20/20 passed.
- Started a new seed-29, 40-item holdout under `results/verified/tool_final/`, excluding all earlier recipe sets, explicit development/few-shot products and all seed-17 products. Preserve v1 results and disclose direct calculator modes; do not describe the gain as learned arithmetic or fine-tuning.
- README patch initially missed its older command spelling; reapplied matching hunks successfully. No completed experiment was overwritten.

**Execution interruption and recovery:**

- The gameplay test stopped at 56 saved rows because the Windows legacy output encoding could not print a fraction slash in one generated answer. The completed row and judgments were safely checkpointed before printing.
- Added `scripts/resume_gameplay.py` to load the exact saved v1 module, point it at the same pinned data, verify the original source/config hashes and emit UTF-8. Resumed only unfinished test rows; do not silently label v1 results as the later tool-correction code. The no-tool answer branch itself was not changed by the quantity correction.
- Seed-29 final tool evaluation is running independently with the corrected version. Initial four tool-enabled quantities matched their references. All aggregate claims still await completed runs.

**Final usability audit:**

- Reused two agents for read-only final checks. They found no need for new dependencies or architecture; they identified missing named output directories, human-check CSV overwrite, Windows Unicode printing, and a compound-question edge case in the new exact calculator renderer.
- Original seed-17 tool experiment completed: 28/40 with tools vs 2/40 without, 39/40 tool calls, 0/20 false calls on fixed non-recipe dev cases. It is retained as diagnostic v1 evidence after its failures motivated the quantity correction.
- Corrected documentation to show one-craft recipe context, explicit count constraints and deterministic quantities. Replaced the unproven faithfulness 'upper bound' assertion with the observed leniency limitation; corrected source-label descriptions to disclose judge selection/calibration overlap.
- Will preserve annotated human-check sheets on all report/check generation, add named rerun outputs and UTF-8 printing, and restrict exact numeric rendering to standalone quantity questions. Final numeric holdout will retain the source hash under which it actually ran; no test-specific routing fixes.

**Completed fresh runs and final corrections:**

- Gameplay test finished all 40 questions x 3 variants (120 rows); dev had 60 rows. Test BERTScore none/dense/rerank .294/.493/.451; supporting quotes hit top 5 in 31/34 dense and 30/34 rerank cases. Negative strict refusals 5/6,5/6,6/6.
- Inspecting refusal rows caught a judge falsely marking dense 'I do not know' correct for trial-spawner torches. Preserved original raw verdicts and original summary/report copies. Shared factual_verdict/points now award zero credit to pure factual refusals, with explicit override counts and aggregation hashes. Corrected test scores are 9/34,27/34,26/34; dev unchanged 9/16,13/16,12/16. Paired rerank-minus-dense score −.029 CI[−.162,.103]; dense-minus-none +.574 CI[.368,.765]. This correction did not regenerate or tune answers.
- Final seed-29 crafting holdout finished: 37/40 with tools vs 1/40 without, CI[80.1,97.4]% for tools; 37 tool calls, 24 structured-routing calls; all 37 successful outputs calculator_exact, 3 no-call failures. Zero overlap with prior product sets and 0/20 false calls on fixed development negatives. No claim of learned arithmetic. Saved exact tool-era sources under source_v2 before final usability changes.
- Added named --output directories to both evaluators, UTF-8 console output, and shared create-once grading-sheet writer with a preservation regression. Completed original run configs/answers were not overwritten.
- Fixed exact numeric output dropping a second question; count constraints still apply, but compound queries use generation. Narrowed the edition guard so grass on bedrock and bedrock-breaking questions remain valid Java questions. Added/updated regression checks; 21 tests passed before the grading/refusal additions.
- Updated the v1 resume helper to load original mcqa/eval/evaluator source, verify actual snapshot hashes, and delegate reports to the current safe aggregator. Updated README rerun paths, version distinctions and observed scores; no per-test routing tuning.

**Regression and demo verification progress:**

- First 23-test run exposed two test-environment/fixture problems: summary fixture lacked newly required answer text, and Windows sandbox temporary-directory permissions denied creation/cleanup. Corrected fixture answers and used a temporary directory under the resolved project directory. The full 23-test suite then passed (no skipped real recipe checks).
- Current code compiles; 60-case source validation and both evaluators' --help with --output passed; local preflight again ready=true with no issues. No downloads.
- Additional final input check: explicit canonical zero/negative/fractional product requests now request a positive whole count before inference, rather than allowing the planner to reinterpret them. Positive-count evaluation behavior remains unchanged; extended the existing quantity-validation regression.
- Started five actual final demo probes on cached local models: numeric exact, natural hopper wording, compound numeric+mechanics, grass on bedrock, and explicit Bedrock Edition refusal. Save all actual traces in results/verified/demo_final.json; no invented demo output.

**Final evidence and package preparation:**

- All 23 tests pass after the final input guard, with real cached recipe checks included. pip check reports no broken requirements. Snapshot hash verification passed for mcqa/eval/evaluator in all four dev/test/tool/tool_final configurations.
- Verified documented v1 resume command through the exact frozen modules. It found all rows complete, generated no new answers, recomputed cached BERTScore, then safely reproduced the corrected report through the current aggregator; original source/config hashes matched. Standard Transformers unused language-model-head warnings and BERTScore non-writable-baseline warnings did not prevent completion.
- Final five demo probes completed: exact 15 [tool], natural hopper wording 5, compound hopper request retains both parts, Java bedrock-block query passes scope guard but produces an unsupported assertion, explicit Bedrock Edition refuses. Full outputs/passages/calls saved. These are diagnostics, not another aggregate accuracy score.
- Benchmark agent inspected the new raw outputs and prepended current failures to docs/failure_analysis.md while preserving all history: old-version elytra leather conflict, evidence ignored/ranked below top five, judge paraphrase/faithfulness errors, strict versus semantic refusal, three crafting no-call failures, demo ambiguity. No code/model tuning from those test outputs.
- Added docs/final_validation.md with measured results, source versions, regression evidence, limitations and human-only submission work. Marked historical review/demo documents accordingly. Clarified that full game files/catalog are excluded while evaluation snippets retain slots/quantities.
- Added self-template ambiguity disclosure: 8 is total recipe-slot consumption for eight batches; reusing outputs could need only one initial template. The frozen gold remains inspectable and requires team checking; no claim of inventory-optimized quantities.
- Technical work uses existing dependencies and standard library. No training, downloads, paid calls or publication. Local Git initialized earlier; next build a clean ZIP with pinned corpus/reference data, source/docs/tests/results and this log, excluding environments, indexes, course files and the full recipe catalog; verify it from an isolated copy.

**Clean package verification and technical completion:**

- Built initial dist/MCQA_submission_2026-10-07.zip: 121 selected files, 3,775,478 bytes. Verified ZIP CRC, each extracted file's SHA-256 against internal MANIFEST.json, and exclusions for environment/Git/course files/full recipe catalog/embedding arrays. Included pinned pages, new benchmark, authentic audit, all source snapshots/results and codextodo.md.
- Extracted into the workspace's dist/package_check/MCQA. Used the existing local recipe cache only in this check copy (not the ZIP) so both real-recipe tests could run. All 23 tests passed, zero skipped. Source validation passed for 60 cases; the documented named-output report reproduced corrected test metrics from the extracted package.
- Starting the clean-copy demo before index setup returned the expected readable missing-data message and exit 1. This is the intended setup requirement, not a fresh full installation on another machine; no downloads or model inference happened in the package check.
- Recorded final verification data and source hashes in results/verified/final_checks.json. Final README explains package contents/setup; report documents all observed limitations. Rebuild the ZIP once with final verification/log metadata and verify its CRC/manifest again; its final digest is in the .zip.sha256 sidecar.
- Technical correction session complete. Remaining requirements are real team identities/contributions, independent reference/judge grading and unaided AI audit Section 6, plus separately handled slides. Optional fine-tuning remains deferred until a concrete experiment objective/split exists. Known model failures are retained rather than hidden.
- Create a local automated Git snapshot of these verified deliverables and record the resulting commit below. No remote, PR, publication or human-author attribution is requested or performed.

**Local version control:**

- Local automated source/results snapshot commit completed successfully; Git history records its exact identity. No remote or publication was configured. Authorship is explicitly 'MCQA automated build', not a fabricated student contribution.
- Git reported automatic LF/CRLF conversion during staging. Added .gitattributes to disable text conversion so experimental source/data hash records survive checkout on Windows and other platforms; stage the exact existing bytes again and verify frozen source blobs against recorded hashes. This configuration fix changes no Python behavior.
- Final package metadata/log refresh uses the already tested source. No further model or full benchmark reruns are needed for documentation/byte-preservation changes.

**Final package exclusion correction:**

- Git-blob verification confirmed byte preservation and all source snapshot hashes. Building from tracked files then revealed only 115 files instead of the expected full set: on Windows, unanchored Test/ also ignored results/verified/test/ (8 evaluation files). The preliminary final ZIP was superseded before delivery.
- Anchored personal/course exclusions to the project root (/Test/ and /Class NLP with DL/), so saved test results are tracked and included. Add explicit required-artifact checks before the final rebuild, including test answers/config/summary/report/human sheet, pinned pages/benchmark, source snapshots, audit and work log. This affects packaging only; the initial extracted copy had contained these files and already passed 23 tests/source validation/report checks.
- Rebuild from the corrected tracked set, check all archive member hashes/CRC and required artifacts, and verify report regeneration from this final extracted ZIP. The final ZIP digest belongs in its SHA-256 sidecar; obsolete preliminary digests do not identify the delivered package.

**Delivered artifact verified:**

- Corrected final package contains all 123 tracked files plus its internal manifest, including every held-out test artifact. CRC, per-member SHA-256, exclusions and required-file assertions passed. Verified source/result Git snapshot a4acafd includes the complete test set.
- Extracted corrected ZIP into dist/package_check_final/MCQA. All 23 tests passed again using only the added local recipe cache for real-data checks; all 60 source cases validated; report regenerated corrected metrics successfully. No answers or judgments were generated by this package check.
- Final metadata refresh adds this completion record to the package without changing source, model output or results. Final archive identity is stored in dist/MCQA_submission_2026-10-07.zip.sha256; verify member CRC/hashes after the refresh. Source is locally versioned; no remote publication occurred.
- Outcome: authorized technical fixes, evaluations, documentation and reproducible package completed. Human contributions/unaided answers and independent labels remain pending by design; optional training has not been performed. The project is not described as flawless or fully ready to submit without that team work.

### 2026-10-07 — Exact assignment compliance check

**User question:** 'is this match the instruction 100%'

- Re-read AI_AUDIT.md and the final validation report; re-extracted and read all 8 pages of PROJECT_INSTRUCTION.pdf using bundled pypdf (no project dependencies installed, no inference or downloads). Applied the PDF reading workflow for exact textual checking, without editing the PDF.
- Cross-checked the literal mandatory stack: 312 real Wiki pages exceeds 50; token-aware chunking with size justification; CPU SentenceTransformers dense retrieval; BERTScore and LLM-as-Judge are both explicitly approved; multiple paired ablations with interpretation; README/demo/evaluation and saved results are present.
- Required full submission is not complete: AI_AUDIT still has unknown team names/contribution placeholders and three unaided Section 6 answers; presentation slides and live individual Q&A are separate human deliverables. Confirm the actual group contains 3–4 students. PDF pages 5–6 explicitly require no final placeholders and Section 6 without AI; page 7 requires individual unaided Q&A.
- Distinguished extra quality work from literal requirements: independent human answer grading is strongly recommended for evaluation rigor but not an explicitly named mandatory deliverable in the PDF. Fine-tuning is optional; no minimum answer-accuracy percentage or unprecedented domain is specified. Minecraft is not excluded from the permitted domain choice.
- Conclusion: mandatory technical components are implemented, but neither 100% submission completeness nor a 100% rubric score can be claimed. This compliance note updates the live work log after the delivered ZIP; no source/results/package was changed by this read-only check.

### 2026-10-07 — Optional extension coverage

**User question:** whether this project covers the assignment's listed optional extensions.

- Checked current mcqa.py retrieval, rrf/CrossEncoder and plan_tools/craft implementations against the five extension descriptions supplied by the user. No source edits, training or model calls.
- Confirmed three implemented extensions: BM25+dense hybrid with RRF; cross-encoder reranking; model-selected crafting tool calls with up to three native planning rounds plus structured routing fallback. The direct quantity renderer is calculator output, not model training.
- LoRA fine-tuning and GraphRAG/multi-hop retrieval are not implemented. Multi-round recipe tool calls must not be described as GraphRAG or multi-hop retrieval.
- Existing comparisons measure retrieval variants and tool/no-tool outcomes. Current source-grounded test does not establish a reranker advantage over dense; extension presence alone does not guarantee a higher grade. The project goes beyond the mandatory stack without needing all five extensions; presentation must explain actual mechanisms, evidence and limitations.

### 2026-10-07 — Demo latency investigation and correction

**User report:** 'i did try demo.It kinda slow on output.Is it need to be fix? or is it ok'

- Applied the existing ponytail workflow: measured the real cached local pipeline before changing its behavior. A read-only agent inspected redundant work; root owns code/log edits. No model downloads, paid calls or training.
- Profile saved in results/latency_review/before.json: first gameplay 16.333 s (retrieval/model initialization 6.889 s, planning 7.152 s), warm gameplay 6.946 s (retrieval .306 s, native+fallback planning 4.424 s, final answer 2.215 s), warm canonical crafting 4.949 s (retrieval .357 s, two planning calls 4.590 s). Initial Ollama /api/ps was empty, so first inference also loaded the local generator. Timings exclude process/index startup (.351 s) and use Hugging Face offline caches. This is a small diagnostic, not a latency population benchmark.
- Ordinary questions pay native planning, fallback routing and final generation. Removing the fallback could lose valid recipe routing, so preserve it in default mode. Recipe-context matching costs only tens of milliseconds; not a useful optimization target.
- Reused explicit quantity parsing and extracted one shared validated-quantity helper. Standalone successful recipe requests now stop after the matching tool call and return before Wiki retrieval/reranking; compound/raw-material requests retain full planning+retrieval. Clarification also needs no Wiki retrieval. Original model arguments and official recipe trace remain available; no arithmetic or retrieval-model changes.
- Demo now immediately prints loading/working status and elapsed query time. Added --no-tool to reuse the existing evaluated no-tool pathway for faster general gameplay; default still includes crafting planning. Interactive use keeps CPU models cached rather than reloading for each separate command.
- Extended the existing quantity regression: one planning call, correct amount despite wrong model count, zero Wiki search for exact output. All 23 tests pass; compilation and --help passed. Measuring post-fix latency and live CLI behavior next; prior saved quality scores retain their actual source versions.

**Post-fix measurement and observed limits:**

- results/latency_review/after.json records current source hash, local model/GPU residency and five actual responses. Canonical crafting: 2.592 s first, 2.573 s warm, one native model call, no Wiki lookup, correct 15 [tool]. Pre-change warm case was 4.949 s with two planning calls plus retrieval. No context-dependent source citation is fabricated for a calculator answer.
- Default gameplay remains 7.016 s warm and uses all three model calls. Optional --no-tool gameplay took 2.781 s and returned the same cow/wheat fact with a real passage citation. Post-fix first gameplay took 15.291 s including 8.411 s CPU model initialization; first-run slowness still exists. These small measurements are not a broad latency benchmark, and before/after cold residency differed.
- Ollama /api/ps confirms the 4B Q4_K_M model is fully GPU-resident (size_vram equals size: 3,178,149,969 bytes). GPU availability is not the problem here. Preserved pre-change mcqa.py from the exact Git blob; its SHA matches before.json.
- Actual updated one-question CLI printed Loading saved index, Working, the tool trace and 15 [tool], finishing in 2.6 s. Added a visible gameplay-mode notice for --no-tool so users know the calculator is disabled. README and final validation explain mode, warm interactive use and source/version limits. Running one interactive no-tool session for two real questions verifies model reuse; save observed output below.
- Keep prior benchmark configs/answers untouched; no claim that the faster source itself has been independently re-evaluated for all gameplay/tool questions. No training, dependency/model changes, streaming protocol or speculative caching infrastructure added.

**Latency work completed:**

- Verified the actual --no-tool interactive CLI: first gameplay question 9.1 s, repeated question 2.5 s, with visible working status and normal blank-line exit. The repeated timing was corrected from the separate 2.8 s instrumented probe to the actual CLI output. This demonstrates process-local model reuse; cold start still takes longer.
- Replayed the new shared quantity validator over all 40 saved final tool traces without generating answers: all 37 calculator_exact cases reproduce their recipe gold; the 3 no-call cases remain without calculator amounts. Saved quantity_replay.json. This checks transformation consistency, not a new end-to-end accuracy estimate.
- Current tests: 23 passed; Python files compile; new CLI flag/help/default calculator and interactive gameplay mode run successfully. Earlier benchmark files remain unchanged and measured under their recorded source snapshots.
- Updating the local Git snapshot and existing submission ZIP with the validated latency changes, actual timing/replay evidence and latest work log. Preserve exact file bytes and required benchmark artifacts; verify ZIP hashes/CRC. No new model, dependency, fine-tuning or publication.
- Outcome: startup delay is expected, but redundant exact-recipe work was removed and status feedback added. The fast gameplay option disables crafting planning explicitly; default mode keeps agentic recipe routing and compound/multistep behavior. Timings are hardware/session-specific small probes.

### 2026-10-07 — Proposed future implementation roadmap

**User question:** 'what is the future implement plan'

- Reviewed the saved failures, final validation, assignment requirements and completed latency work. This entry records proposed next work; none of the features below were implemented or evaluated in this planning session. The application remains fully local with no paid API calls.
- Keep the existing dense/hybrid/reranker/tool baselines and frozen results. Three optional extensions already exist; implementing every listed extension is not necessary. Prefer correcting observed failures before adding architecture or training.

**Recommended order and completion criteria:**

1. **Version and edition evidence control — highest implementation priority.** Add explicit evidence metadata and filter current Java answers against historical/other-edition sections, preserving original documents for traceability. Observed target: the Elytra answer must not use a historical leather repair rule when answering for the pinned current Java version. Avoid treating every mention of the bedrock block as Bedrock Edition. Check current, historical and explicitly unsupported edition questions with source citations.
2. **Recipe routing and answer reliability.** Expand development cases for varied recipe wording, ambiguous names and compound requests. Reuse the existing parser/tool validation, preserve user quantities, and require a successful recipe trace before returning calculator claims. Clarify ambiguous items instead of guessing. Check both successful recipe calls and false calls on general gameplay; supported recipes missed by routing are a known limitation.
   - For general gameplay, select answer-bearing sections and check that generated claims follow the retrieved evidence. Target observed cases such as missing the leaf breaking section, refusing llama breeding despite retrieved evidence, and inventing a grass-on-bedrock explanation. A read-only second review confirmed these priorities; independent human grading remains recommended, not a literal mandatory requirement in the brief.
3. **Evaluate each meaningful change on new evidence.** Human-check references and sampled judge verdicts, retain existing cases as regression evidence, and collect a fresh final test set separated from development. Existing inspected tests must not be presented as a new untouched holdout. Compare the current source's dense/hybrid/reranker/tool variants, exact tool correctness, answer-bearing retrieval, appropriate refusals and cold/warm latency. Preserve historical runs with their actual source hashes; do not replace their outputs with new answers.
4. **Further demo speed only where measurement supports it.** The exact-recipe early return, loading/working feedback, elapsed time and optional --no-tool mode are already done. Next candidates are fewer planning calls for ordinary questions and streamed answer text. Measure routing coverage and answer quality before changing the default; streaming improves visible response time but does not itself reduce total generation work. A small local web interface is optional after reliability work, since the CLI already satisfies the demo requirement.
5. **Optional distinctive extension: recursive crafting/material planning.** Build on the official recipe catalog and existing calculator to explain intermediate ingredients for a requested item/count. First define recipe alternatives, batch rounding, reusable outputs, cycles and inventory assumptions; test against known recipe chains. Compare it with the existing direct ingredient calculator. Do not label a recipe traversal tool GraphRAG unless graph-based retrieval is actually implemented and evaluated.
6. **Optional training, last.** Consider LoRA only after a curated training/development split and a specific measurable objective such as routing or grounded answer format exist. Protect a new final test split from training and tuning. GPU generation is confirmed, but the installed project PyTorch is CPU-only; a compatible local GPU training environment and measured memory feasibility would need separate verification. No training is needed merely to claim another extension, and none has been performed in this session.

**Submission work that remains separate from implementation:**

- The real team must supply names, contribution mapping and reviewed decision explanations, and answer AI_AUDIT Section 6 without AI assistance as required by the brief. Independent human grading is recommended for rigor rather than an explicitly named mandatory deliverable. Slides, rehearsal and individual unaided Q&A remain human presentation work.
- Suggested scope if time is limited: finish version-aware evidence control, routing reliability and fresh evaluation; prepare reliable demo cases. Add recursive crafting only if those are complete. Defer LoRA and a larger interface until a concrete need and available time justify them.
- This planning-only update changes codextodo.md, not source, models, metrics or the existing submission ZIP. No implementation, inference, downloads, tests, publication or training was performed for this roadmap.

### 2026-10-07 — Continue after Claude limit: improvement and easy demo launchers

**User authorization:** Claude Code is unavailable due to usage limits; continue the project, make improvements, and create an easy demo Bash launcher. Screenshots are context about an interrupted review, not additional executable instructions.

- Applied ponytail: read current source/demo/preflight/evaluator/logs and Git state before edits. Git reports only the existing roadmap log change; no new Claude source changes. Claude's handoff is historical and its older results are not the current validated results.
- Parallel ownership: pipeline agent owns mcqa.py/test_mcqa.py (current-Java evidence filtering and validated deterministic recipe routing); evaluation agent owns a separately named, newly frozen source-grounded comparison; read-only audit agent checks remaining compliance/reproducibility issues. Root owns demo/launchers, documentation, integration, process record and package verification.
- Preserve pinned corpus/indexes, previous answers/judgments/source snapshots, human-only audit fields and original Claude history. No paid calls, model/dependency downloads or speculative training. A new comparison must retain baseline/improved source hashes, real outputs and limitations; existing inspected failures are development/regression evidence.
- Launcher plan: provide both double-click Windows .bat and Bash .sh, resolve their own project directory and local virtual environment, warm existing local models for interactive use, and show actionable setup failures. No automatic downloads or hidden long-running training.
- Implementation and verification are in progress; do not treat this entry as a completed outcome.

**Implemented startup work and interim verification:**

- Added demo.bat and demo.sh with quoted project-directory resolution, existing virtual-environment selection, forwarded arguments and interactive warmup. demo.py can start the installed local Ollama service with a hidden Windows process, verifies the expected cached generator exists, stays offline for Hugging Face inference, and displays source revision URLs where supplied. No missing model is downloaded automatically. Dense/BM25/hybrid/rerank can be selected explicitly for demonstration.
- Preflight now checks dependencies before importing NumPy/Hugging Face, returns readable setup guidance on incomplete installs, and has --demo so BERTScore's evaluation-only package/cache does not block demo readiness. Existing default preflight retains evaluation checks.
- Root startup/evaluator checks passed (3 demo startup cases, 2 preflight cases, 2 new frozen-evaluation cases). Bash syntax/help and Windows launcher help passed. The first Git Bash attempt failed on sandbox MSYS process namespace access; an authorized escalated execution of the installed Bash runtime succeeded. This was not an automatic-review rejection.
- A concurrent integration run caught one scope-filter reason-label assertion during pipeline editing; reported to its owning agent rather than editing shared files. Await final stable-source tests before freezing the new implementation.
- Read-only audit re-read all 8 assignment pages and found no missing mandatory technical component. Corrected README/prompt-history language overstating independent labels as compulsory; they are recommended for rigor. Preserved human-only audit fields. No standalone unfinished Claude review report exists in the project; original history/log artifacts remain intact.
- Evaluation preparation froze baseline a0870e1, source hashes and 28 new cases before generation: 12 quoted facts from 12 pages absent from the earlier benchmark, 4 negative cases and 12 new recipe products. Dev/test factual pages are disjoint; references are AI-curated and not independently human/game-verified. Baseline inference is running in a separate result folder; no old answer or judgment is replaced.

**Pipeline integration and real launcher checks:**

- Implemented current-Java scope control inside all four retrieval candidate paths; stored source/index files are preserved. The initial whole mixed-chunk exclusion lost 17/50 previously inspected fact quotes, so it was rejected in development. The final conservative in-memory sentence/context view retains 7,438/10,128 eligible chunks (2,129 history, 403 other-edition headings, 158 empty eligible views excluded; 1,669 text views trimmed). This is not full version verification. A diagnostic on already inspected sources retains 48/50 fact quotes; Leaves/Horse evidence loses useful follow-up context. Dense embeddings still encode original text while BM25/reranking/prompt use filtered views; limitation is explicit.
- Explicit supported recipe forms now use the validated calculator without model selection, trace via=deterministic with no invented model_args. Ambiguity, count validity, batch rounding and compound preservation still apply. Product-count constraints do not depend on resolving an ingredient alias. Sources point at actual stored revisions and identify chunk/passage-view provenance. Fixed context-managed page/index reads.
- Re-ran all 40 previously inspected final canonical recipe cases with chat patched to fail if called: 40 exact matching slot-quantity outputs, zero model calls. Saved tool_regression.json under source SHA100ac803...51d2. This is a regression check on seen cases, not fresh accuracy or inventory-optimized material planning.
- Added one generic two-clause parser based only on fresh development wording before new test outputs were inspected: I want/need N PRODUCT followed by a requested ingredient quantity. Fake Torch/Stick batch and compound/count regression checks pass. Preserved the unused initial after snapshot as source_candidate_dev_parser. Final comparison source SHA b5ae6351ba2b0c5b88a0f9acd1953b624589aadc2090ffd0b40b29110a70449d; no tuning after the final test starts.
- Full integrated suite now passes 34 tests; compilation and diff checks pass. Actual demo/evaluation preflight both report ready with cached models. Read-only launcher review caught missing lazy-import guidance and a command-line pause; root fixed both.
- Launched Windows .bat from the parent NLP directory: warmup 11.0 seconds, exact hopper quantity 15 [tool] displayed in 0.0 rounded seconds, current gameplay wheat/cow answer with saved revision link 6.9 seconds in default mode, explicit Bedrock Edition refused instantly. Raw console output saved in launcher_windows.txt. Startup began before the final two-clause parser patch, so this trace establishes launcher/common-path behavior, not every final parser form.
- Launched final Bash .sh from the parent directory through installed Git Bash: warmup 8.7 seconds, I want 9 torches / sticks query returned 3 [tool] in 0.0 rounded seconds. Raw output saved in launcher_bash.txt. Added demo-fast.bat as a small wrapper around the existing --no-tool gameplay option; launcher help passed. Only root launcher smoke calls ran after baseline evaluation finished; they ended before after-evaluation started.
- Baseline comparison finished all 44 rows including cached BERTScore. Final after source is frozen separately and generation proceeds sequentially without competing demo inference. Dev/test facts and recipe styles remain separately reported. Model judge limitations and direct-ingredient-only scoring of compound answers are disclosed.

**Completed new evaluation and documented limits:**

- Before/after generation is complete: 44 rows per implementation, 88 total, both actual source snapshots/configuration/data hashes and unchanged generator digest. The 28-case validator, report reproduction and evaluator regression checks pass. human_check.csv was created for all 88 rows without overwriting earlier sheets. runtime_metadata.json adds observed cached HF revision IDs/package/Python versions as supplemental metadata, preserving original generation configurations.
- New test recipe quantities: 5/6 before to 6/6 after; dev 6/6 both. All eight canonical/two-clause cases across splits route deterministically; four compound cases use model tool calls. Means by style, excluding startup/judges: canonical 3.687 to 0.008 seconds; two-clause 7.601 to 0.005; compound 11.908 to 11.128. These are small diagnostic timing samples rather than throughput guarantees.
- Automatic test facts: dense 7/8 to 6/8, rerank 7/8 to 7/8. Exact-quote @5 dense 6/8 both, rerank 8/8 to 7/8. New test negatives: 2/2 pure refusals per variant before/after. No general factual accuracy improvement is established. Analysis notes preserve apparent false partial judgments, valid alternate evidence, and the stricter-than-semantic pure-refusal metric. Original model labels remain untouched.
- Preserved compound explanation errors: correct Acacia Sign ingredient quantity with unsupported claims about needing a table and producing planks; quantity success is not full-answer success. No source/prompt tuning after final test inspection. Future work can use these inspected examples as development, but needs another untouched final set for a new generalization claim.
- Root reused eval.paired_differences on the frozen answers (no inference/new labels) and saved paired_stats.json with its aggregation code hash, recipe Wilson intervals and style medians. Dense test automatic score change -0.062 CI[-0.188,0]; rerank0 on eight pairs; BERTScore intervals include0. Recipe6/6 CI[61.0%,100.0%] underscores limited sample size and cannot certify universal accuracy.
- Updated README architecture/setup/results, final validation, failure analysis, demo transcript pointers, authentic AI audit decision/prompt entries and Codex prompt history. Human identities/contributions/unaided audit answers stay unfilled for the real team. No training/dependencies/downloads/paid calls/publication occurred. Existing source/results/history remain unchanged except live code/docs and separately named new evidence.
- Next finalize the local automated Git snapshot and submission ZIP, then verify manifest hashes/CRC/required artifacts and run the 34-check suite from a clean extraction using the existing cached runtime and a separately added local recipe cache. This is not a fresh installation or game verification on another machine.

**Targeted scope check and snapshot:**

- Local automated Git snapshot a8e2c75 records the implementation/launchers/frozen comparison; no remote publication or human-author credit. Subsequent documentation and probe records are finalized below before the package refresh.
- Ran one targeted already-inspected Elytra history-conflict question; current answer uses phantom membranes from Anvil's saved current repair section, with revision links. The standalone first probe omitted HF offline flags and emitted a Hub metadata-request warning. This was a diagnostic process mistake, not a paid inference call; preserve its trace with that note and repeat explicitly offline rather than claiming it never contacted metadata services.
- The separate HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE rerun uses cached retrieval models and local Ollama, again returns phantom membranes and the quarter-durability repair detail. Cached revision IDs match the comparison's observed models. These are seen-case diagnostics, not another untouched accuracy test or proof of every generated claim. The production demo and comparison already set offline flags.

**Package verification and completion:**

- Local snapshot e9d74e8 includes the final technical documentation and both targeted diagnostic traces. Source SHA still exactly matches the final after-evaluation snapshot. A Git diff against a0870e1 confirms no earlier verified or latency result changed; shared corpus/chunk/embedding/recipe hashes match both new run configurations.
- Preserved the previous ZIP as dist/MCQA_submission_pre_continuation_a0870e1.zip with its own digest. Built the new submission ZIP from 160 tracked files plus MANIFEST.json, verified every member SHA-256 and ZIP CRC, and asserted required new launchers/evaluation/test artifacts and prior held-out results are included. Excluded environments, models, full recipe catalog, embedding/index arrays and personal/course folders.
- Extracted into dist/continuation_check_mkmlwgml/MCQA. Using the existing cached virtual environment plus local crafting.json added only to this check copy, all 34 tests passed, zero skipped; all 28 fresh cases validated; the 88-row comparison report reproduced with frozen source/dataset/evaluator checks. No new answers or judges ran in this package verification.
- Confirmed clean-copy error behavior: missing index shows readable fetch/index instructions and exit1; missing virtual environment from demo.bat --help shows setup guidance/exit1 without traceback or a blocking pause. This is a clean artifact extraction check, not an independent internet installation or game-mechanic certification.
- Saved results/improvement_review/final_checks.json with actual checks/source identities/limits. Final refresh adds only this verification metadata and process record to the already tested source package; verify member hashes/CRC again and store its final identity in the SHA-256 sidecar. No further inference/training/model changes or publication is needed.
- Outcome: authorized continuation, direct recipe speed/reliability improvements, scoped source evidence, easy launchers, separate frozen evaluation, documentation and reproducible technical package are complete. General gameplay improvement is unproven and compound explanations still need caution; those failures remain inspectable. Team identities/contributions/unaided audit and separately handled presentation remain human submission work. Optional LoRA/recursive planning were not added without a concrete demonstrated need.
### 2026-10-07 — Requirements confirmation and pitch deck

- User requested a fresh match against the term-project instructions and a rendered deck that is easy to pitch. The language preference is English slides with Thai speaker notes.
- Re-read all eight brief pages and independently cross-checked the mandatory stack, saved studies and exact ten-slide outline. Mandatory technical components are implemented. Full submission still requires real 3–4-person names/contributions, the team's unaided AI_AUDIT Section 6, rehearsal and individual Q&A. No universal-accuracy or perfect-grade claim is justified.
- Applying the presentations skill with the supplied Artifact Tool runtime, editable pipeline/results, source-labelled historical/current studies and individual rendered-slide inspection. Build files remain private under dist; final presentation artifacts will be separate. An unavailable template picker is not replaced with an invented template.
- The deck will show frozen v1 gameplay, frozen v2 tool and latest small-study results separately. Thai speaker notes are AI-authored presentation assistance, not unaided audit answers. Team names have not been supplied, so the cover will explicitly ask for the real names before submission.
- Work in progress; final rendering and verification are not yet complete.

**Completed presentation and verification:**

- Created presentation/MCQA_pitch_ready.pptx with exactly ten English slides in the brief's order: title/team/domain, motivation, full pipeline, two key-decision slides, two separate ablations, current two-metric evaluation, failure analysis and the AI audit's three decisions plus one actual scorer error. All ten slides contain Thai speaker notes and traceable project sources. The companion Thai_presenter_notes.md includes timing and three selected live-demo prompts. No unaided audit answer or human identity was generated.
- Used the bundled Artifact Tool with installed Tahoma and a private Node-library junction under dist/slides_build. Initial junction/path checks required authorized local escalation. Two initial validation attempts needed the supported complex-script font key and explicit runtime-library path; these were corrected without installing packages or changing project models. No automatic-review rejection occurred.
- Visual review caught reversed diagram arrowheads and a label crossing a connector. Corrected direction, cleaned the explicit recipe path and showed the retained bidirectional agentic tool loop. A conservative native-table overflow warning was removed by shortening the model table cells, preserving their meaning. No final package/layout/font warnings remain.
- Imported the exact final PowerPoint, rendered all ten slides at 2560×1440, inspected every slide individually and scanned deck flow. Verified unchanged render hashes across repairs where applicable. Five editable native tables are on slides 5–9; slide 3 uses editable pipeline shapes/connectors. No code dumps or fabricated accuracy claims. Native Microsoft PowerPoint execution was not performed.
- Applied the PDF skill to generate presentation/MCQA_pitch.pdf from the final renders. Reopened it: ten 960×540-point pages; rendered all ten with bundled Poppler and inspected each. The PDF is a visual copy; the editable PowerPoint contains the Thai notes. MCQA_preview.png is the overview.
- Independent read-only review confirmed ten slide/Thai-note pages, exact required topics/timing, valid source paths, honest AI ownership, and numeric agreement with frozen v1/v2 and current reports. No new inference, training, labels, benchmark outputs, runtime dependencies or publication were added.
- Updated README, final validation, AI audit prompt/tool inventory and Codex prompt history to record the actual presentation work. Technical requirements are met, including BM25/RRF, reranking and the tool loop. Full submission still needs authentic team names/contributions, unaided Section 6, rehearsal and individual Q&A. The cover name field is intentionally visible because the user has not supplied names.
- Next preserve the deck/documentation in a local snapshot and refresh the submission ZIP with hash/CRC verification. Existing technical source and experimental outputs remain frozen.

**Package check:** Preserved the pre-slide package as dist/MCQA_submission_pre_slides_3b22a95.zip with its digest.
Refreshed the working-copy submission ZIP: 166 members including all four presentation artifacts and required
historical/current evaluation files. Every member SHA-256 and ZIP CRC passes. The next local automated snapshot
and final refresh will record the commit identity in MANIFEST.json and the final archive digest in its .sha256
sidecar; the private verification report also records the result. No remote publishing is requested or performed.

- The first local commit attempt failed because Git has no configured author identity. Files were staged and the
  working-copy ZIP remained valid; no source or experimental result changed. Retrying with an explicit per-command
  Codex automation identity, without changing global settings or attributing the deck to a human student. The final
  archive refresh checks the resulting snapshot and records its actual identity in the manifest/sidecar.

### 2026-10-07 — Requested GitHub push

- User explicitly authorized pushing the completed project to GitHub. Existing origin is
  https://github.com/G9YzNDN/NLPDLxMC.git; local master tracks origin/main and initially has five unpushed commits.
- Confirmed the clean local snapshot and independently checked outgoing deliverables: implementation improvements,
  launchers, frozen evaluation evidence, documentation/audit, ten-slide deck/PDF/preview and Thai notes. Models,
  environments, rebuildable indexes, the full recipe cache, submission ZIP and course/personal folders are excluded.
- Attempted fetch before normal HEAD-to-main push. The GitHub sign-in helper stalled; stopped only that helper and
  retried a noninteractive read-only remote check. Git reported it could not authenticate or prompt for credentials.
  No remote branch has been changed, and this was not an automatic-approval rejection.
- Preparing the installed Git credential manager's sign-in flow. Authentication requires the user's GitHub login;
  do not read or print stored tokens, invent credentials, force-push, change global Git identity or create a new repository.
  Push/remote verification remain pending until authentication succeeds. Record the actual outcome here.

- The user supplied https://github.com/G9YzNDN/NLPDLxMC, confirming the existing destination. Device sign-in
  returned a GitHub OAuth server-error page and produced no authorization code. Started the installed credential
  manager's normal browser sign-in instead and requested the user's sign-in status. No password/token is requested
  in chat. The login helper remains pending; authentication is the only current blocker to fetch/push.

### 2026-10-07 — End-of-day shutdown and successful GitHub synchronization

- User reported browser sign-in failed with error 500 and supplied the GitHub error-page screenshot. The earlier
  login attempts ended without usable CLI credentials. Installed system Git/GCM and existing SSH checks did not
  provide authenticated access; no passwords, stored tokens or private keys were read or printed.
- User requested closing work for the day. Stopped the verified Ollama tray/server processes and confirmed no
  listener remained on port 11434. No Python/demo process was running. Closed Chrome, GitHub Desktop and the
  Settings/audio windows; sign-in activity reopened some work windows, which were closed again. The user
  interrupted before the entire desktop shutdown was finalized; ChatGPT and the gaming overlay remained open.
- User then explicitly resumed the push and reported completing GitHub Desktop login. CLI Git still needed its
  own credential-manager connection. The installed GCM browser flow succeeded with the signed-in browser,
  without another user question, credential extraction, dependency installation or global Git identity changes.
- Authenticated fetch succeeded. Both local HEAD and origin/main already pointed to
  6acdf78cd025e88479f89c428778f455c48c9a21. Normal push of HEAD to refs/heads/main succeeded with
  "Everything up-to-date"; an authenticated ls-remote independently confirmed that exact remote commit.
  The project code, frozen evaluation evidence, launchers and all four presentation artifacts are on GitHub.
- Recording this checkpoint in a local automation-authored commit, then synchronizing it to the same main branch
  and verifying the final remote hash. No force push, new repository, model restart, inference or training is needed.

### 2026-10-08 — Ollama suitability check

- User asked whether using Ollama is acceptable. Independently rechecked the original eight-page
  Class NLP with DL/Term Project/PROJECT_INSTRUCTION.pdf: pages 1–2 require corpus/chunking,
  SentenceTransformers dense retrieval, at least two course evaluation metrics and an ablation. The brief
  specifies no generator runtime or direct Transformers/Hugging Face loading requirement; LoRA is optional.
- Checked production mcqa.py: qwen3:4b-instruct is the model, Ollama serves it through localhost:11434/api/chat.
  Official Ollama API/FAQ documentation confirms local inference. Keeping this local generator satisfies the
  user's no-paid-API preference; using a runtime does not constitute fine-tuning or replace the RAG pipeline.
- Only this work record changed. No model/server restart, new inference, benchmark, installation, commit or push.

### 2026-10-08 — Final submission review

- User requested a last complete readiness review and then said "limit hit continue". Used independent reviews
  for the original eight-page brief/deliverables, implementation, and evaluation integrity; root checked tests,
  dependencies, actual demo startup, archive contents, and integrated findings. Assumed one local presenter.
- Required human fields remain: real 3-4 team names/contributions, all three explicitly unaided AI_AUDIT Section 6
  answers, and title-slide names. Nine FILL IN fields remain in the final audit in addition to name placeholders.
  The original audit skeleton is historical evidence and is not meant to be filled in instead of the final audit.
- Verified the mandatory corpus/chunking/CPU SentenceTransformers stack, two course metrics and ablations,
  three optional extensions, ten-slide order, Thai notes and editable tables/pipeline. All ten existing final
  slide renders were inspected and matched to the PDF pixels; no new visual defect found. Native PowerPoint was not run.
- All frozen main/tool/improvement summaries, counts and inspected source/data/config hashes reproduce. Human
  grading sheets remain blank; no human validation, team contribution or unaided answer was invented.
- Initial 34 tests and dependency checks passed. Exhaustive item-ID review then found the map alias collision:
  the filled map's display name overwrote the empty-map ID. Reversed lookup precedence and added a focused test.
  All 1,010 actual recipe product IDs now resolve correctly; arithmetic was checked at counts 1, 3 and 10.
- Actual demo cold start exposed a socket TimeoutError while polling the newly started Ollama server. Retried
  read timeouts within the existing startup deadline and tested both recovery and expiry with one launch.
  No larger runtime rewrite or new dependency was introduced. Only the review's own server was stopped for the rerun.
- Integrated suite now passes 36 tests. Pip reports no broken requirements; all 30 tracked Python files parse.
  A limited known-token/private-key pattern scan found no matches in tracked text. Full local preflight passes
  on the real host; sandbox Python prints a base-location warning, while real-host execution works normally.
- Real demo.bat ran from outside the repo, restarted Ollama, warmed models in 12.7 seconds and answered the
  hopper question correctly in 7.7 seconds. Four later smoke outputs are in results/submission_review/
  live_smoke_2026-10-08.json with source hashes, passages, traces and timings. Functional checks pass, but the cow
  answer adds an unsupported necessary lighting/enclosure condition from an optional indoor-farm tutorial.
  Explicitly marked that whole answer as not verified correct; the smoke sample is not a new accuracy benchmark.
- Published the full readiness report in docs/submission_review.md and linked it from README/final_validation;
  documented the live grounding failure and actual user prompts. The two fixes postdate frozen benchmark code;
  no historical snapshot, automatic judgment, reference, score or slide number was overwritten or relabelled.
- The old 166-member ZIP passes CRC/member hashes/sidecar and originally differed only in codextodo.md.
  Preparing a new dated archive containing the reviewed fixes and evidence; required human fields remain visible.
  Existing October 7 archives are retained. No fresh-machine installation, native slide playback, full benchmark
  regeneration, model download, fine-tuning or paid API call was performed.
- New 168-member October 8 archive passes CRC, every manifest member hash and required-file checks. Fresh
  extraction passes all 36 tests using the existing installed environment plus a copied excluded recipe cache;
  missing indexes produce the expected readable demo setup error. No fresh-machine compatibility is claimed.
  Private package evidence is in dist/final_submission_review_2026-10-08/package_check.json and package_tests.txt.
- Saving the reviewed files in a local checkpoint and refreshing the archive from that clean snapshot before
  the previously authorized GitHub synchronization. The new archive keeps a manifest and .zip.sha256 sidecar;
  dist/slides_build/package_verification.json records its final exact hash/source commit. It remains a draft
  submission until the required human fields are completed. No remaining code defect was identified in scope;
  unsupported generated claims and same-model judging remain disclosed quality limitations.

### 2026-10-08 — Supplied team roster and approved two-person exception

- User supplied Natdanai Phurintanachot (67070230) and Nattapong Suphawirojlert (67070051), then confirmed
  "just two people. professor accepted". Recorded the exception as user-confirmed professor acceptance of two
  members despite the brief's original 3-4-member wording. No additional member is required by the known approval.
- Added the exact roster to AI_AUDIT, README, current readiness documents, title slide and companion notes.
  Kept both members' contributions/personally used tools pending because none were supplied. Anonymous prompt
  actions remain separate; all three unaided Section 6 fields remain untouched. Independent read-only review agrees.
- Applied a targeted ArtifactTool edit to the existing deck. All ten slides rendered; package/layout/font/import
  checks pass with zero findings/warnings, five editable native tables retained. Slides 2-10 match their previous
  renders pixel-for-pixel; slide text and all ten speaker notes are preserved. Visually checked the new cover/montage.
- Regenerated the PDF with both names in its author metadata. All ten embedded page images match the final PPTX
  renders exactly; Poppler-rendered cover inspected. Updated preview/Thai-note introduction and preserved originals
  privately. Final PPTX SHA-256: 94ac0dfafa8b23bccfcfdda7e3498f093ebc61a53d27e7180057a927aa2e25f0;
  PDF SHA-256: 5c6723df50a10d9ac4cd0af75cab1bcc2bcaf5612a2fcd4e5269ba800064ad4c.
- Retained the prior reviewed ZIP as dist/MCQA_submission_before_team_names_1680730.zip plus its hash sidecar.
  The refreshed 168-member archive passes CRC, every member hash and required-file checks. Saving these edits
  in a local checkpoint, then rebuilding the archive from that clean snapshot and synchronizing the previously
  authorized GitHub main branch. Exact final source/hash checks are in dist/slides_build/package_verification.json.
- This roster/artifact change needs no new inference, training, dependency or code regression run. Prior 36-test
  evidence remains unchanged. Native PowerPoint playback and human contribution/unaided completion remain unverified.
