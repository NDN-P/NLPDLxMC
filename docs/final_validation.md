# Final technical validation — 2026-10-07

The local implementation, saved evaluations, setup instructions and technical package are complete. This is a
tested course project, with known model failures. Independent team checking is recommended; the personal audit
and presentation remain submission work. No paid API calls, model downloads or fine-tuning occurred during this correction session.

## What changed

- Distinguish a bare refusal from factual claims plus uncertainty; check all claimed answers for faithfulness.
- Validate judge JSON/verdicts, retry malformed output once, and exclude failed verdicts from valid denominators.
- Never award factual correctness to a pure refusal. Preserve the original judge output and record any override.
- Reject ambiguous recipe names, invalid quantities and explicit other-edition requests; accept Java questions about
  the bedrock block. Generic names ask for clarification instead of selecting a variant.
- Give the planner matching official one-craft recipe context. Preserve explicit user quantities on matching calls
  and record the original model arguments. Return a validated direct ingredient quantity for standalone queries;
  compound requests still receive a generated answer. Successful recipes also survive a bare generator refusal.
- Add source-backed, page-disjoint benchmark splits; checkpoint raw answers, passages, rankings and judgments;
  keep expected refusals separate from factual metrics. Named output directories allow clean reruns.
- Print UTF-8 on Windows and preserve existing human-check sheets. Improve demo/setup errors and keep an authentic
  AI audit, original skeleton, prompts, work log and all historical experiments.

## Source-grounded gameplay evaluation

The frozen dataset contains 60 cases: 50 answerable facts across 25 pinned Wiki pages, 5 unavailable-world-state
queries, and 5 scope refusals. Dev/test are 20/40 cases, with 8/17 disjoint answerable source pages. Every factual
reference has an exact contiguous quote and revision; the quotes fit individual 128/256/512-token chunks.
References never enter retrieval or training. They are AI-curated and source-checked, not independently human
certified or tested inside Minecraft Java 26.3. The corpus itself includes historical and other-edition material.

**Untouched test split:** 34 factual cases plus 6 expected refusals, 120 saved question/variant rows.

| Variant | Correct | Partial | Factual refusals | BERTScore F1 (facts) | Supporting quote in top 5 | Strict negative refusal |
|---|---:|---:|---:|---:|---:|---:|
| No retrieval | 9/34 | 1 | 0 | 0.294 | — | 5/6 |
| Dense | 27/34 | 4 | 3 | 0.493 | 31/34 | 5/6 |
| Hybrid + reranker | 26/34 | 4 | 2 | 0.451 | 30/34 | 6/6 |

Paired judge-score gain over no retrieval: dense +0.574, 95% bootstrap CI [0.368, 0.765]; rerank +0.544,
CI [0.382, 0.706]. Rerank minus dense is −0.029, CI [−0.162, 0.103]; its BERTScore difference is −0.042,
CI [−0.109, 0.012]. These observations support retrieval, without establishing a reranker advantage. The registered
reranked default was retained; the test set was not used to select a new retriever or tune gameplay prompts.

On dev's 16 factual cases, correctness is 9/16, 13/16, 12/16 and BERTScore .372/.491/.512. Dev's 4 negative cases
have strict refusals 2/4,4/4,4/4. The raw answers and all comparisons remain under `results/verified/dev/` and `test/`.

The same local model generates and judges. Its test verdict falsely credited a dense refusal on `java26.3-045`;
the final aggregator scores it incorrect, reducing dense from the original 28 to 27. Original answer judgments
and `summary_original_judge.json` are retained; aggregation hashes identify the correction. Other judgment errors
remain for independent review. Faithfulness is automatic support classification, not factual truth. Strict negative
refusal means a bare refusal; a useful explanatory refusal can miss this metric. See `failure_analysis.md`.

## Crafting evaluation

The seed-17 diagnostic test exposed changed product counts and rewritten calculator totals: 28/40 with tools versus
2/40 without. Its inspected failures motivated the general quantity constraint and direct calculator renderer.
That run is preserved under `results/verified/tool/` and is not treated as the final clean holdout.

The frozen seed-29 final set contains 40 different product IDs, excluding prior saved dev/test products, explicit
development/few-shot examples and every seed-17 product. Gold quantities use official Java 26.3 recipe slots and
batch rounding; no LLM judge is used.

| Variant | Correct | Accuracy | 95% Wilson CI | Tool called |
|---|---:|---:|---|---:|
| Without tool | 1/40 | 2.5% | [0.4, 12.9]% | 0/40 |
| With tool | 37/40 | 92.5% | [80.1, 97.4]% | 37/40 |

All 37 successes used `calculator_exact`; 24 calls came through structured routing. Three cases made no tool call
(Wild Armor Trim Smithing Template, Item Frame and Green Wool). There were 0/20 false calls on fixed non-recipe
**development** cases. This is a pipeline result on canonical quantity wording, with deterministic arithmetic; it
does not show learned arithmetic or fine-tuning. Item-level exclusions do not prevent shared recipe structure.

## Verification and source versions

- 23 regression tests pass, including real cached recipe checks, ambiguity, invalid quantity inputs, batch rounding,
  compound requests, refusal/judge/scorer safeguards, source evidence, and preservation of human annotations.
- Application/evaluation/scripts compile; all 60 source cases validate; named output CLI options work; local
  preflight reports ready with no missing data/models/service. Package dependencies have no broken requirements.
  The extracted package also passes all 23 tests (using the existing recipe cache only for the real-recipe checks),
  source validation and report regeneration. Starting its demo before rebuilding indexes reports the missing data clearly.
- Prior independent verification reproduced all three chunk lists exactly and checked embedding dimensions,
  finite values/unit norms. A 100-question retrieval reproduction and 36 BERTScores were saved in `codex_review/`.
  The entire older 1,000-question retrieval experiment was not rerun after these tool/evaluation corrections.
- Actual final demo traces are saved in `results/verified/demo_final.json`: exact 15 iron for 3 hoppers; natural
  wording 5 iron for a hopper; compound request retained; explicit Bedrock Edition refused. The bedrock-block demo
  also contains an unsupported generated assertion, recorded as a limitation rather than a successful fact check.
- Gameplay raw generation uses `results/verified/source_v1/`; seed-29 crafting uses `source_v2/`. Config files record
  actual source/dataset/chunk hashes and cached model revisions/digest. Later scope/compound/input/usability fixes
  preserve positive canonical quantity behavior, verified by tests; scores remain labelled with their measured source.
- Python 3.14.7, CPU retrieval/BERTScore, local Ollama `qwen3:4b-instruct` Q4_K_M. GPU inference can vary despite fixed
  temperature/seed. Rebuilding the embedding index can also change floating-point details.

See README for separate rerun directories and the exact v1 resume helper. The package includes pinned pages,
benchmark references, code, saved results, source snapshots and logs; rebuildable indexes, models and full game
recipe data are excluded. Build local data/index before inference. A clean-copy check validates the packaged code
and benchmark; it is not a new internet installation on a second machine.

## Demo response time

**Historical demo latency correction, before the later continuation (2026-10-07):** a small local profile measured 16.3 seconds for first gameplay,
6.9 seconds for warm gameplay, and 4.9 seconds for a canonical recipe quantity. Ordinary default questions use
native planning, fallback routing and answer generation. The planner then stopped once a standalone direct quantity
was validated, and that answer bypassed Wiki retrieval; the same recipe probe took 2.6 seconds with one model call.
Compound/multistep requests keep the full pipeline. Demo status/timing is visible immediately; `--no-tool` reuses the
existing no-tool gameplay path and measured 2.8 seconds warm versus 7.0 seconds in default mode in the post-fix run.
First gameplay still loads CPU models (15.3 seconds in that run). Keep an interactive session open and ask a
gameplay question before the presentation. These are diagnostic timings, not population speed guarantees.
All 23 regressions pass, including the one-call/no-retrieval quantity shortcut. Raw probes and pre-change source
are in `results/latency_review/`; previous quality scores retain their frozen source labels and were not rerun.

## Later continuation: evidence control and easy demo launchers

The later source adds conservative current-Java passage views and masks historical/other-edition headings before
all four retrieval candidate paths. Stored pages, chunk IDs and embedding arrays are unchanged. On the 256-token
index, 7,438 of 10,128 chunks are eligible; 1,669 passage views are trimmed. This is a scope heuristic, not proof
that each surviving claim is valid in Java 26.3. It loses two useful quotes in an already inspected 50-fact
diagnostic because mixed paragraphs can carry valid Java facts after other-edition context. Dense embeddings
still encode original text; BM25/reranking/generation see the filtered text. New source citations link at the saved
Wiki revision and expose passage-view provenance.

Explicit recipe forms now use the same validated calculator directly, labelled `via="deterministic"` without
invented model arguments. Compound/other wording retains the model tool loop. Parsed product counts constrain
matching model calls even if ingredient aliases cannot be resolved. A generic two-clause form was added using
only new development cases before new test generation. All 40 previously inspected canonical recipe cases now
return their direct slot-quantity gold without a model call; this is regression evidence, not fresh accuracy.

Double-click `demo.bat` for the complete demo or `demo-fast.bat` for gameplay with calculator planning disabled.
`bash demo.sh` supports Windows Git Bash and macOS/Linux environment paths. Launchers resolve their own folder,
prepare cached models, and reuse one interactive process. Demo can start the installed Ollama service without a
helper window and never pulls models automatically. Initial retrieval-model caching is an explicit README setup
step; demo inference stays offline. Preflight `--demo` excludes evaluation-only BERTScore requirements and handles
missing packages with setup guidance.

Real Windows/Bash sessions from outside the project folder are saved under `results/improvement_review/`.
Preparation took 11.0/8.7 seconds in these two diagnostic sessions; hopper/torch quantities completed in 0.0
rounded seconds, while default gameplay took 6.9 seconds. These few measurements are not population latency
guarantees. The final generic Bash recipe was checked against the final parser; Windows startup began before that
last parser addition and establishes launcher/common-path behavior. The integrated suite passes 34 tests.

The new 28-case before/after study is separate from all prior reported evaluations: 12 facts on 12 pages absent
from the earlier 60-case source-backed benchmark, 4 negatives, and 12 new recipe products. Pages are disjoint
between new dev/test splits, but item exclusion does not imply new recipe structures. Cases/references were frozen
before generation and are AI-curated, not independently human/game-verified. Raw outputs/configurations/source
snapshots are in `results/improvement_review/`. Final source hash is recorded in its `source_after/manifest.json`.
The initial unused candidate is retained separately; new test outputs did not guide tuning. See its final report
for observed results; presence of the filter does not itself establish an accuracy gain.

The completed comparison contains 88 real responses. New test recipe quantities changed from 5/6 to 6/6; dev
quantities remained 6/6. Canonical/two-clause recipe generation means across dev/test changed from 3.687/7.601
seconds to 0.008/0.005 seconds; compound means were 11.908/11.128 seconds. This isolates direct calculator work
from model-driven compound requests, whose narrative claims remain unreliable. Automatic test facts were dense
7/8 → 6/8 and rerank 7/8 → 7/8; exact-quote retrieval was dense 6/8 → 6/8 and rerank 8/8 → 7/8. Alternate valid
passages and apparent judge false partials are documented, with original labels preserved. No general accuracy
gain is demonstrated by this small study. Both variants refused both test negatives; the dev private-world query
also illustrates why a helpful caveated refusal can fail a strict bare-IDK metric. Independent team review is
recommended. Supplemental runtime metadata records observed cached HF revisions without changing the frozen
generation configurations. No model downloads, fine-tuning or paid calls occurred.
Paired aggregation of the frozen answers is in `paired_stats.json`: test dense automatic score difference
−0.062, bootstrap 95% interval [−0.188, 0.000]; rerank score difference 0.000 on all eight pairs. BERTScore
differences have intervals containing zero. The six-case tool result has a wide Wilson interval [61.0%, 100.0%],
so 6/6 observed successes must not be presented as universal 100% accuracy. These intervals do not remove
same-model judge bias or certify population behavior.

## Remaining team work

1. Supply real team names and actual contributions in `AI_AUDIT.md`.
2. Write Section 6 unaided. The brief explicitly says **“Answer WITHOUT using AI”**; AI must not invent these answers.
3. Check benchmark references and grade `results/verified/test/human_check.csv` independently, particularly conflicting
   judge labels and examples in `failure_analysis.md`. Keep human judgments separate from original automatic outputs.
4. Add authentic names to the supplied ten-slide deck and rehearse the live demo/individual technical explanations.
   `presentation/MCQA_pitch_ready.pptx` has English slides, Thai speaker notes, editable architecture/results and the
   instructor's exact slide order. `presentation/MCQA_pitch.pdf` is the shareable rendered copy; the companion Thai
   notes include the 4–7-minute demo break. The notes are AI-authored, not unaided Section 6 responses.

The deck uses historical frozen v1 gameplay, frozen v2 tool and current small-study results separately. It does not
claim a consistent reranker benefit, human-certified accuracy or general accuracy improvement. All ten final
PowerPoint renders and all ten PDF pages were visually inspected. Package/layout/font/import checks pass with
zero final warnings; five native result/model tables and the pipeline remain editable in the PowerPoint. Native
PowerPoint execution was not tested. The team-name field is the only intentional cover placeholder.

Fine-tuning is optional under the course brief. This session first corrected and measured pretrained RAG; no training
experiment, improvement or student-authored decision is claimed. Any later adaptation needs its own objective,
training data, untouched evaluation split and hardware plan.
