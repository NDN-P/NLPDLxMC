# AI Audit — MCQA: Minecraft Wiki Q&A
**Team:** Natdanai Phurintanachot (67070230), Nattapong Suphawirojlert (67070051)
**Team-size exception:** The professor approved our two-person team (the brief specifies 3-4 members).
**AI Tools Used:** Claude Code, Codex

---

## 1. Tool Inventory

| AI Tool | Primary Use in This Project |
|---|---|
| Claude Code | Source/topic research; initial corpus extraction, chunking, retrieval, crafting tool, evaluations, documentation and fixes recorded in `docs/ai_prompt_history.md`. |
| Codex | Requirements/topic research, independent review and metric reproduction, further fixes/tests, source-grounded benchmark, evaluation tooling, technical completion and the English pitch deck/Thai speaker notes; recorded in `codextodo.md`. |
| Local qwen3:4b-instruct | Application answers, recipe tool planning, automatic correctness and faithfulness judgments. Same-model judging can favour its own answers. |

---

## 2. Prompt Log (minimum 5 entries)

### Entry 1 — Choosing Minecraft
**Prompt sent:**
> so the game was interesting i searched up on minecraft RAG someone have done it,minecraft is good choice because it contain many data path etc

**What AI generated:**
Discussed Minecraft Wiki RAG, recipe tools, edition/version boundaries and the course requirements. Existing similar projects do not prevent an original experiment.

**What you changed or rejected:**
The user selected Minecraft. No independent student code change is demonstrated by this message.

---

### Entry 2 — Scope and work records
**Prompt sent:**
> you task is not just review you have to help build,train,evaluate and do not forget to record every process in codextodo.md

**What AI generated:**
Created the project-specific work record and inventoried implementation/data. No training run was invented; pretrained RAG meets the mandatory assignment scope.

**What you changed or rejected:**
The user expanded Codex's role and required process logging. Algorithm/code decisions remained AI work.

---

### Entry 3 — Survey boundary
**Prompt sent:**
> at the moment you can survey project but wait for me to let you continue

**What AI generated:**
A read-only inventory distinguishing actual files from unverified model/evaluation claims.

**What you changed or rejected:**
The user explicitly restricted implementation and inference until continuation.

---

### Entry 4 — Independent review
**Prompt sent:**
> review and evaluate

**What AI generated:**
The report in `docs/codex_review.md`, reproduced tests/metrics, and raw diagnostic results. It found invalid refusal classification, quantitative false positives, ambiguous item identities and weak benchmark references.

**What you changed or rejected:**
The user later authorized corrections. Claude also received the review and fixed several findings. These are AI-authored fixes; no student labels are claimed.

---

### Entry 5 — Corrections and completion
**Prompt sent:**
> ok fix for me. make everything to perfection

**What AI generated:**
Further fixes/regression tests, safer calculator handling, 60 new source-grounded Java cases with exact pinned quotes, resumable evaluation and setup checks. Observed results are saved; perfection is not claimed.

**What you changed or rejected:**
The user confirmed Claude had finished editing, enabling safe continuation. At that time, team names, contributions and independent labels had not yet been supplied.

---

### Entry 6 — Continue after Claude's limit

**Prompt sent:**
> claude code hit limit for too long so i need you to continue. You can do everything to make improvement . and create demo bash for me i am lazy

**What AI generated:**
Windows/Bash demo launchers, startup/preflight guidance, conservative Java evidence filtering, direct validated
recipe routing, regression checks and a separate frozen before/after evaluation. The evaluation records faster
explicit quantities and remaining unsupported explanations; it does not claim general accuracy improved.

**What you changed or rejected:**
The user authorized Codex to continue after Claude became unavailable and requested an easy demo launcher.
No independent student implementation or human validation is demonstrated by this instruction.

---

### Entry 7 — Requirements and pitch deck

**Prompt sent:**
> does this match all the instruction provided in term project? If yes can you render me a slide that is easy to pitch

**What AI generated:**
Rechecked all eight brief pages and generated ten English slides in the required order, with Thai speaker notes,
editable pipeline/result tables, a rendered PDF and timed demo guidance. The user selected "English slides with
Thai speaker notes". Historical and current experiments are labelled separately; universal accuracy is not claimed.

**What you changed or rejected:**
The user specified the presentation language and later supplied both members' names and IDs. Actual contributions,
rehearsal, individual explanations and the explicitly unaided Section 6 remain the real team's responsibility.
The deck and notes are AI-authored assistance.

---

## 3. Decision Journal (minimum 5 decisions)

| # | Decision | Owner | Reason (in your own words) |
|---|---|---|---|
| 1 | 256-token chunks, section/paragraph boundaries, no overlap; compare 128/256/512 | [AI-decided] Claude | Original source-page hit rates were similar; 256 balances context and cost. Oversized paragraphs can cut sentences. |
| 2 | BAAI/bge-small-en-v1.5 | [AI-decided] Claude | Small English model runs on CPU and fits the maximum chunk size. |
| 3 | Dense/BM25 RRF, optional cross-encoder reranking | [AI-decided] Claude | Compare semantic and exact-name retrieval; measure jointly scored passage ranking rather than assuming a gain. |
| 4 | BERTScore, decomposed correctness judge, separate faithfulness/coverage/refusal counts | [AI-decided] Claude and Codex | Similarity is not truth; claims, refusals and failed judgments need correct denominators. Same-model judging remains a limitation. |
| 5 | Same-question answer variants and separate tool ablation; new page-disjoint dev/test benchmark | [AI-decided] Claude and Codex | Preserve old experiments, replace unverified-reference assumptions with inspectable source quotes, and keep test references out of retrieval/training. AI-curated references still need independent team review. |
| 6 | Direct routing for explicitly parsed recipes; retain the model tool loop for other requests | [AI-decided] Codex | The validated calculator can answer unambiguous quantities without model latency or changed totals. Deterministic traces are labelled separately from model-selected calls. |
| 7 | Conservative current-Java passage views with unchanged raw sources/indexes | [AI-decided] Codex | Historical/other-edition passages caused conflicting answers. Filtering keeps source provenance, but can remove valid mixed-paragraph evidence; surviving facts are not all game-verified. |

These are AI-owned reasons, not statements that a student independently made the algorithm choices. The fully local/no-paid-API requirement came directly from the user.

---

## 4. Error Catch Log (minimum 2 entries)

### Error 1
**What the AI said:**
The first tool run reported 15/40 correct and described four no-call successes as model knowledge.

**Why it was wrong:**
First-number extraction counted four explicit refusals that repeated a requested product quantity equal to the gold ingredient amount.

**How you fixed it:**
Codex exposed the raw examples. Claude changed the parser/rescored while preserving original flags; Codex added negation/conflict checks and regression tests. Historical with-tool score is 11/40. The discovery and fixes are AI-authored.

---

### Error 2
**What the AI said:**
Any response containing “I do not know” was an abstention and skipped by faithfulness evaluation.

**Why it was wrong:**
Six responses made claims before uncertainty. Two were both correct and abstained. A null judgment also counted as checked.

**How you fixed it:**
Claude distinguished pure refusal/hedging and valid/failed verdicts. Codex validated judgment JSON and tested citation/newline handling. All six omitted responses were automatically rated partly supported; this is not human validation.

### Error 3 — Item identity

Generic “Smithing Template,” “Banner Pattern” and “Music Disc” silently selected one variant. Shared display-name keys overwrote one another, and matching numbers masked wrong template identity. Claude made names specific and returned ambiguity; Codex stopped the planner from guessing after ambiguity and added structured choices and tests. The user must choose a specific item.

---

## 5. Contribution Map

| Team Member | Human Contribution | AI Tools Used |
|---|---|---|
| Natdanai Phurintanachot (67070230) | Built the model pipeline: corpus, chunking, dense and BM25 retrieval, RRF, cross-encoder reranking, local LLM answering and the crafting tool. Studied the whole project to understand every component. | Codex, Claude Code |
| Nattapong Suphawirojlert (67070051) | Evaluation: metrics (BERTScore, LLM-as-Judge), ablation runs and results. Studied the whole project to understand every component. | Claude Code |

---

## 6. What Would Break? (Answer WITHOUT using AI)

Answer all three questions in your own words.

**a)** If you removed the cross-encoder reranker (cross-encoder/ms-marco-MiniLM-L6-v2, which reranks the top 20
hybrid RRF results to the top 5) from your pipeline, what specifically changes in output quality and why?

The prob of answer chunk to be number one decrease but still in top 5.
We did 1000 question experiment.By removing cross-encoder it change from rerank to hybrid that have 3 retrieval variant(dense,bm25,rrf merge). So if we have question like "What material use to repair elytra" the answer is "Anvil>Reparing".
Dense rank in on #1,bm25 rank it #4.Hybrid avg two list so Armor>Unit repair rank #1 and answer chunk rank #2.

**b)** Why did you chunk your documents at 256 tokens? What would happen to retrieval quality if you used 2× (512)
or ½ (128) that size?

We chunk our documents to 256 not because it is better but it stay in the middle of 128 and 256. If 128 tokens it get cut into 4 chunks(256 tokens = 2 chunks) can cause LLM to see half story and answer incompletely but it only cause by long section.
512 can cause reranker and LLM to read longer text so it slower
and may make LLM follow worng path by having the right answer fact cover by other thing. So using 256 that between is right choice.

**c)** Your ablation compares Variant A: dense-only (BAAI/bge-small-en-v1.5) vs. Variant B: BM25 + dense hybrid with
RRF + cross-encoder reranker. Pick the result that surprised you most and explain the mechanism behind it — not
just "variant A scored higher" but why technically.

On our group test lately 40 questions,the two variant pick nearly the same chucks 31/40 on other 9 for example.We use our test question "Repair elytra with what?" The Variant A answer phantom membranes(correct answer) and Variant B answer leather(Wrong) the reason to that is because B bring old history page,it say elytra once repair by leather keyword search match "elytra" and "repair" in reranker say it relevant. but on anther hand The question is "Does a zombie villager become drown underwater?" A:"I do not know" , B:"No"(Correct Answer) the reason to that is B found Zombie Villager > behavior that say exactly that A not retrieve it. But it is a tie tie because final score A:27/34 B:26/34 mean no real difference and B is slower,A : 18ms per question. B : 373 ms per question so it's 20x.
