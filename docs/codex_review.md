# Codex review and independent evaluation — 2026-10-07

**Historical review, before the authorized corrections.** The subsequent fixes, fresh source-grounded evaluations,
actual remaining failures and submission status are documented in [final_validation.md](final_validation.md).
The findings and original raw review evidence below are preserved; their old source line numbers describe that snapshot.

The project is a working local RAG prototype with substantial experiment evidence. It meets the corpus, CPU retrieval, two-metric and multiple-ablation requirements. It is **not ready for final submission**: the benchmark does not establish current Java 26.3 accuracy, several evaluation bugs need correction, and the team's AI audit is unfinished.

This review preserves Claude's application code and saved experiments. Independent checks are in `results/codex_review/`; the repeatable harness is `scripts/codex_review.py`. All model runs used cached models and local Ollama. No downloads, paid calls or training were performed.

## Findings, in priority order

### 1. [P1] Establish a trustworthy Java 26.3 benchmark

`eval.py:53–60` samples synthetic references without checking them against the pinned Wiki. `eval.py:106–120` then instructs the judge to treat those references as truth. The corpus also includes other editions and historical content: 19 of the 100 answer questions and 163 of the 1,000 retrieval questions explicitly mention Bedrock, Education, Pocket or Console editions. Others are off-topic or have faulty premises.

For example, the saved enchantment reference says the maximum level is 10; its retrieved passages instead distinguish experience-level requirements from enchantment levels and explain command-created levels 0–255. A model may disagree with that reference for legitimate reasons. Thus the reported 16/32/34% figures measure agreement with an imperfect synthetic pool, not verified current Java gameplay correctness. The README discloses this limitation, but disclosure does not repair the benchmark.

Keep the synthetic experiments as exploratory evidence. Add a separate, team-checked set with current Java questions, verified answers, exact source revisions and answer-bearing passages. Include deliberately unanswerable and out-of-domain cases and report them separately. Evaluate the existing variants on the same questions. Decide how to handle historical and other-edition corpus sections before presenting the system as Java 26.3 specific.

### 2. [P2] Partial answers are treated as complete refusals

`eval.py:143–144` detects uncertainty by substring. `eval.py:159–163` then skips faithfulness for the entire response, including factual claims preceding “I do not know.” Six saved responses are affected: two dense and four rerank. Two are even judged correct while simultaneously counted as abstentions.

The enchantment example claims the maximum level is 30 and then abstains on the question's second part; its claims are never checked. Distinguishing pure refusals gives dense 40 and rerank 31, rather than 42 and 35. The current answered-only comparisons therefore need revision. In this review, bypassing the shortcut made the local faithfulness judge label all six omitted responses `partly` supported. These are automatic diagnostics, not human judgments.

Classify pure refusal separately from partial answering; evaluate all substantive claims and recompute the summaries. Also fix `eval.py:217–233`: one null faithfulness verdict is included in “65 checked,” although only 64 verdicts are valid. Report attempted, valid and unparsed judgments separately.

### 3. [P2] The crafting scorer accepts numbers inside refusals

`eval.py:323–325` takes the first number anywhere in the response; `eval.py:338–339` compares it to the gold quantity. Four first-run refusals merely repeat the requested product count and are counted as correct. Strict numeric parsing, allowing a `[tool]` citation, changes the historical with-tool result from **15/40 to 11/40**. A verbose correct answer can also be rejected when it mentions the product count before the ingredient count.

The **final 35/40 versus 1/40 and dev 38/40 results survive this stricter parsing check**. This verifies number extraction, not correct item identity. Replace first-number scoring with an explicit answer format or validated extraction; correct the historical tables while preserving original runs. `results/codex_review/tool_scoring.json` records the four false successes.

### 4. [P2] Duplicate item names silently select one recipe

`mcqa.py:327–330` overwrites duplicate display names. Generic “Banner Pattern” selects the Skull pattern, “Smithing Template” selects Wild armor trim, and “Music Disc” selects the uncraftable Ward disc. `mcqa.py:314` also removes the identity distinction from displayed results.

Two saved test questions intend Coast and Ward templates but ask only for “Smithing Template.” Selecting Wild produces the same requested quantities, hiding the identity error. Preserve variant-specific names, reject ambiguous generic names, and use specific names in evaluation questions. Add a focused regression check for these real collisions when fixing the code.

### 5. Independent human validation is still outstanding

Claude produced every judge-validation label, as the documentation correctly states. Run1 labels are used by `scripts/judge_selection.py` to choose the judge; agreement on that set is calibration. Run2 overlaps run1 on 12 question strings and three identical question/variant rows, so it is not wholly independent either.

Team members should label new examples with source evidence, without seeing the judge's verdict. Keep AI-created labels clearly identified. Source-page hit rate is also not a guaranteed lower bound on relevance recall (`README.md:133–134`, `docs/failure_analysis.md:26`): a hit can come from a passage that does not answer the question. Use the descriptive name “source-page hit rate” until answer-bearing passages are checked.

### 6. Finish the submission audit and packaging

`AI_AUDIT.md` has 46 `[FILL IN:]` placeholders and unnamed team members. Complete the authentic prompts, decisions, corrections and contribution records using the available history. The assignment's explicitly unaided “What Would Break?” responses must be written by the team. The workspace is not currently a Git repository; prepare the final runnable repository/package after the corrections. Slides remain outside this review's scope.

## Independently executed checks

| Check | Observed result |
|---|---|
| Existing unit tests | 7/7 passed |
| Dependency consistency and compilation | Passed |
| Corpus inventory | 312 distinct pages, 816,730 words; 400 stored records including 14 missing titles |
| Recipe metadata | Java 26.3; 1,010 craftable IDs, 236 tags, 1,841 names |
| Question-pool checksum | Matches the documented SHA-256 |
| Evaluation separation | No exact retrieval/answer question overlap; no tool dev/test item overlap |
| Saved answer-summary recomputation | Exact match, including paired bootstrap intervals |
| Chunk reproduction | All 128/256/512 chunk lists identical to saved lists; zero over-budget chunks |
| Embedding checks | All arrays finite and normalized; 24 re-encoded passages agree within 1.35e-7 |
| BERTScore reproduction | 12 saved questions × 3 variants = 36 scores; all match at saved four-decimal precision |
| Correctness judge reproduction | 12/12 sampled verdicts match; this checks repeatability, not truth |
| Omitted-claim diagnostics | Six skipped mixed answers judged partly supported when actually checked |
| New recipe diagnostics | 6/8 correct with tool versus 1/8 without; tool called in 7/8 cases |

The fresh recipe set is small and diagnostic. It does not replace the 40-question experiment or support a general 75% accuracy claim. It exposes practical failures: two cakes prompted no tool call; two anvils produced a correct tool result but the answer still refused. “How much iron does a hopper need?” also triggered no call and returned “I do not know,” despite the more explicit hopper wording succeeding. Cake, Nether-bed, mob-experience and totem demo questions produced answers; the World Cup question correctly refused. The mob answer's universal experience-drop condition deserves source checking before use in a presentation.

On a seed-7 subset of 100 saved retrieval questions, using 256-token chunks:

| Variant | Source-page hit @1 | Source-page hit @5 | MRR @10 |
|---|---:|---:|---:|
| Dense | 64/100 | 78/100 | 0.708 |
| BM25 | 42/100 | 61/100 | 0.504 |
| Hybrid | 53/100 | 75/100 | 0.620 |
| Hybrid + reranker | 65/100 | 78/100 | 0.702 |

This is a reproduction subset of the original retrieval set, not a fresh held-out benchmark. Dense and rerank tie at @5 here; there is no basis to claim a reliable reranker advantage from this small check. Claude's larger saved answer comparison also has a rerank-versus-dense judge-score confidence interval crossing zero.

## What to do next

Correct the scorer, refusal classification and ambiguous item handling first. Then build and team-check the scoped reference set, rerun the same variants, and update the report with defensible labels and conclusions. Finish the personal audit and demonstrate the exact submitted installation. Fine-tuning is optional under the assignment; current evidence does not establish that training is needed before these data and evaluation problems are corrected.

Reproduction commands use the existing environment: `python -m unittest test_mcqa -v`, `python -m pip check`, and `python scripts/codex_review.py artifacts`, `retrieval`, `metrics`, `scoring`, `live`, or `judge`. The last two need local Ollama. They write only review outputs. The sandboxed environment emits a base-Python location warning despite successful runs; the same local unsandboxed check succeeded without it. Existing transformer/BERTScore loading warnings did not prevent the reproduced scores.
