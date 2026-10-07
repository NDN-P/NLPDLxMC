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
