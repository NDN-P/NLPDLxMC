# Final submission review - 2026-10-08

**Verdict: the technical project is ready with documented model limitations, but do not submit the current files unchanged.**
The team names/IDs are now supplied in the audit and title slide; individual contributions/tools and unaided
Section 6 answers still require the team's own input. Complete these before uploading.

**Roster update:** Natdanai Phurintanachot (67070230) and Nattapong Suphawirojlert (67070051).
The user confirmed that the professor accepted this two-person team; this is a user-confirmed exception to the
brief's original 3-4-member requirement, not a missing-member blocker.

This is a local Minecraft Java RAG assistant with a recipe calculator. The review assumes one presenter using
the prepared laptop. All eight pages of `Class NLP with DL/Term Project/PROJECT_INSTRUCTION.pdf` were checked,
along with the implementation, tests, evaluation evidence, audit, slides and existing package.

## Required before submission

1. **Fill both members' actual contributions and personally used tools.** Names/IDs have been supplied, but
   the contribution rows in `AI_AUDIT.md` remain incomplete. Recorded prompt actions are kept anonymous until
   a member identifies their own work. Invented contributions must not replace these fields.
2. **Write all three answers in AI_AUDIT Section 6 without AI.** All three are blank. The brief explicitly
   requires unaided answers and says an unfilled section scores zero. Other final-audit placeholders must also
   be filled; placeholders in the preserved original skeleton are historical evidence, not the final submission.
3. **Rehearse the timed presentation and individual Q&A.** The files cannot establish that every member can
   explain the pipeline. The planned presentation is 10 minutes, with a live demo at minutes 4-7, followed by
   5 minutes of individual questions. Use `demo.bat`, wait for Ready, and keep that process open.
4. **Package the completed human fields.** The reviewed archive remains a draft until those fields are filled.
   The submitted repository/ZIP and PDF must contain the final edits, not the earlier placeholder versions.

## Requirement checks

| Brief requirement | Verified evidence | Status |
|---|---|---|
| Real domain corpus, at least 50 documents | 312 pinned Minecraft Wiki pages with revision inventory | Pass |
| Token-aware chunking with justification | 128/256/512-token indexes; cached tokenizer check found zero over-budget chunks | Pass |
| CPU-compatible SentenceTransformers dense retrieval | BAAI/bge-small-en-v1.5; matching embedding rows and chunk counts | Pass |
| At least two course evaluation metrics | BERTScore and LLM-as-Judge, plus retrieval/tool diagnostics | Pass |
| Ablation with at least two variants and interpretation | No-retrieval/dense/rerank, chunk/retrieval comparisons, tools on/off | Pass |
| Runnable source, setup instructions, demo and evaluation files | README, requirements, launchers, demo.py, eval.py and saved outputs | Pass on this laptop |
| Optional technical extensions | BM25/RRF, cross-encoder reranking, bounded calculator tool loop | Implemented |
| Ten slides in required order | All 10 inspected; Thai notes on all 10; editable pipeline and five native tables; supplied names/IDs on cover | Pass |
| Team roster | Two real names/IDs supplied; professor's acceptance of two members confirmed by the user | User-confirmed exception |
| Complete six-section AI audit | 7 prompt entries, 7 labelled AI-owned decisions, 3 error catches; names/IDs supplied, contributions/tools/Section 6 incomplete | Must complete |

The brief sets no minimum accuracy score, generator runtime requirement, or mandatory fine-tuning experiment.
Ollama serves the existing local model. The presence of extensions does not guarantee a particular grade.

## Two bugs corrected during this review

- `mcqa.find_item`: display name "Map" overwrote the item-ID alias for the craftable empty map. Item-ID aliases
  now take precedence. `map`, `maps`, `minecraft:map` and `empty map` return 8 Paper + 1 Compass; explicit filled
  map still resolves separately. A regression test covers the recipe and direct question route. All 1,010 real
  recipe product IDs resolve correctly after the fix; arithmetic was checked at quantities 1, 3 and 10.
- `demo.ensure_ollama`: the initial live run reached the newly started service while its response was still slow.
  A socket read timeout escaped the startup retry. It now retries that timeout within the existing deadline.
  A regression tests recovery and deadline expiry, with only one server launch.

**36 tests pass**, `pip check` reports no broken requirements, and all 30 tracked Python files parse.
A limited known-token/private-key pattern scan found no matches in tracked text; this is not an exhaustive security certification.
Full local preflight passes, including evaluation dependencies and cached models. Windows `demo.bat` was run
from outside the project directory after stopping only the review's own Ollama helper: it restarted the service,
prepared models in 12.7 seconds, and answered the hopper quantity correctly in 7.7 seconds.

## Evaluation integrity

- The 60-case main and 28-case improvement datasets validate. Main dev/test contain 60/120 complete, unique
  variant rows. Recomputed saved summaries, intervals, refusals and evidence ranks agree exactly.
- The final tool comparison reproduces 37/40 with tools versus 1/40 without. Its frozen code and data hashes match.
- The separate improvement study has 44 complete rows before and after. Its reported scores, BERTScores, recipe
  quantities and timing arithmetic match raw outputs. Frozen source/data/model records remain unchanged.
- The slide claims match those measured studies. The two fixes above postdate the frozen improvement snapshot;
  they do not establish any new broad accuracy gain. The evaluated snapshot remains under
  `results/improvement_review/source_after/` and was not replaced by current code.

## Live demo quality and limits

Four selected checks and full retrieved passages are saved in `results/submission_review/live_smoke_2026-10-08.json`.
These are smoke checks, not a new accuracy benchmark or independent human evaluation.

| Question | Observed result |
|---|---|
| Iron ingots for 3 hoppers | Correct: 15, supported by the recipe tool |
| How to breed cows | Correct wheat fact, but an unsupported extra necessary condition about a lighted enclosure |
| Cow breeding in Bedrock Edition | Explicit scope refusal, as designed |
| Craft a map | Correct: 8 Paper + 1 Compass, direct calculator route |

The cow answer turns optional indoor-farm instructions from a retrieved tutorial into a universal requirement.
Its basic keyword/citation checks pass, but the entire answer must not be called correct. Explain this failure
if it appears during the demo; a citation alone does not prove that the model preserved the source's meaning.
The default hopper wording took 15.447 seconds in a separate process that loaded retrieval models; the map's
direct route took 0.003 seconds. Wording and model warmup matter; do not promise instant answers to every query.

Independent human grading remains blank: 0/60 main dev rows, 0/120 main test rows and 0/88 improvement rows.
It is recommended for rigor, especially with the same generator and judge, but is not a separate mandatory
deliverable in the brief. No human judgments, unaided answers or contributions were invented.

## Package and scope of verification

The prior 2026-10-07 archive passes CRC, every member hash and its SHA-256 sidecar. Before this review it contained
every tracked file and differed from the worktree only in the newer work log. It predates the two corrections above.
The refreshed reviewed archive is `dist/MCQA_submission_2026-10-08.zip`: 168 members, passing CRC/member-hash
checks and required-file checks. A fresh extraction passes all 36 tests using the existing environment and a
copy of the local recipe cache; without a rebuilt index the demo correctly prints setup guidance and exits.
It still requires the human fields listed above. Models, virtual environments, rebuildable indexes and the full
game recipe cache are excluded; follow README setup on another machine. The manifest records the actual source
commit and the sidecar records the final archive digest.

Not checked: a fresh internet installation on another computer, native PowerPoint playback, live individual Q&A,
or independent in-game/human validation. Full generation benchmarks were not rerun after these narrow fixes;
historical results retain their original frozen code provenance. No training or paid API calls were performed.
