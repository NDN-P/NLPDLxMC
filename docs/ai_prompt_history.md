# Real prompts sent to Claude Code for this project (for AI_AUDIT.md)

Copied word for word from the chat with Claude Code (2026-10-06), by the team member who sent them. Use these for the
Prompt Log in `AI_AUDIT.md`; add your own prompts to other tools yourselves. Write "what you changed or rejected"
yourselves: nothing below says what a human changed.

| # | Prompt (exact) | What Claude produced |
|---|---|---|
| 1 | check C:\Users\guymy\OneDrive\Desktop\NLP\Class NLP with DL. This is my classroom there are term project can i used the senior project as this project? If not give me a plan. | Read the term-project brief; said the senior project (ThaiQty, a tool-calling benchmark) does not fit (no corpus, retrieval or Q&A; different team size; double-submission risk); proposed a plan |
| 2 | any topic that's good to go? | Three domains with checked public sources: Thai personal income tax, Thai labour rights, KMITL regulations |
| 3 | list more interesting and unique thing to do codex present กยศ. student-loan Q&A and a Thai-language pandas troubleshooting assistant. | Assessed Codex's two ideas and listed more, each tied to a brief extension (GraphRAG, tool calling) |
| 4 | so the game was interesting i searched up on minecraft RAG someone have done it,minecraft is good choice because it contain many data path etc | Checked licences (Minecraft Wiki CC BY-NC-SA 3.0); suggested twists: crafting calculator tool, crafting graph, Thai questions |
| 5 | what another game if not minecraft | Stardew Valley, Factorio, Terraria with checked wiki licences |
| 6 | test (with a pandas snippet reading minhaozhang/minecraft-question-answer-630k) | Found the snippet needs `huggingface_hub`; found the dataset is synthetic (generated from wiki pages by glaive.ai) and has a `source` page column; advised using it only as a question pool |
| 7 | is this topic valid? | Checked the topic against every requirement of the brief; drafted a message to ask the instructor |
| 8 | Fine minecraft seem good idea so finished project for me except slide presentation that will be later do not forget claudetodo.md | Wrote `mcqa.py`, `eval.py`, `demo.py`, `test_mcqa.py`; chose the models, chunk sizes, variants and metrics (see the decision list below) |
| 9 | why not using latest minecraft version? | Switched the crafting data from the community dataset (newest: 1.21.11) to Mojang's official 26.3 files (latest release) |
| 10 | continue claudetodo.md | (new chat, 2026-10-07) Finished the fetch, built the indexes, ran every experiment, wrote the docs and the `AI_AUDIT.md` skeleton (see below) |
| 11 | expected time to finish? | A time estimate per remaining step (about 2–2.5 hours) |
| 12 | l will sleep and be back around 10 hours.So do everything that make this project successful. already set to bypass permissions.Do not stop. Check everything double check triple check i want this project to have no mistake | Checked every result before using it; found and fixed the unused tool and the broken judge (see below); re-ran the experiments; reproduced the data and index in a clean copy; wrote the results into the docs |
| 13 | @"C:\Users\guymy\OneDrive\Desktop\NLP\NLPDL\docs\codex_review.md" | Checked Codex's review finding by finding against the saved data, fixed findings 2–5, re-ran the affected evaluations (see below) |

## Decisions Claude made (unless your team reviewed and approved or changed them, the honest owner is [AI-decided])

- Corpus: the 400 Minecraft Wiki pages with the most questions in the pool, as plain text via the wiki API, pinned by revision id.
- Chunking: paragraph-aligned chunks inside one section, prefixed with "Page > Section", no overlap; sizes 128/256/512 tokens
  compared, measured with the embedding model's own tokenizer.
- Embedding model: BAAI/bge-small-en-v1.5 (CPU-friendly, 512-token limit) with its query instruction.
- Retrieval: dense (cosine), BM25, hybrid with reciprocal rank fusion (k = 60), hybrid + cross-encoder reranker
  (cross-encoder/ms-marco-MiniLM-L6-v2, top 20 reranked).
- Generator and judge: qwen3:4b-instruct through Ollama, temperature 0 (the same model judges, so self-preference bias is possible;
  `results/judge_check.csv` is for checking the judge by hand).
- Metrics: Recall@1/5/10 and MRR for retrieval; BERTScore (distilroberta-base) and LLM-as-Judge for answers; exact match for the
  crafting tool.
- Crafting tool: Mojang's 26.3 recipe files; the tool returns direct ingredients and the model may call it again for intermediates.

Made during prompt 10 (2026-10-07):
- Page titles that failed were looked up again ignoring letter case, %-escapes and the `Tutorials/` -> `Tutorial:` move
  (recovered 92 of 106 missing titles; 14 still have no page).
- A "word" longer than the chunk budget (a 1,400-token command with no spaces) is halved until it fits; before this fix
  1–2 chunks per size were over the budget (found by re-counting every chunk with the bge tokenizer).
- The tool instruction is repeated after the question: with it only in the system prompt, qwen3:4b-instruct never
  called the craft tool once passages were in the prompt (it said "I do not know"); it called the tool without passages.
- Chunk size kept at 256: rerank Recall@5 was 74.4 / 74.1 / 74.5 % for 128 / 256 / 512 (a tie, 95% CI about ±2.7),
  so the choice was made on cost and context per passage, not on the 0.1-point lead of 512.
- The answer-quality questions are held out from the 1000 retrieval questions used to choose the chunk size.
- The 40-miss sample in `results/retrieval_miss_sample.csv` was categorised by Claude; the team should check it.

Made during prompt 12 (2026-10-07, while the user slept). Each one was found by checking a result, not assumed:
- **The craft tool was barely used** (first test run: 14 calls in 40 crafting questions, 15/40 correct by the first scorer, 11/40 after the fix below; 6 times the
  model wrote the call as text because the prompt asked it to cite "[craft tool]"). Claude redesigned it as a two-step
  agent (plan on the bare question with native tool calls, a JSON-schema fallback, then answer with passages + tool
  results), tuned it on 40 separate dev questions, then ran the test questions: 33/40, and 35/40 after the citation fix
  below. Item names now prefer the item over the block name ("Wheat", not "Wheat Crops").
- **The LLM judge was broken**: the one-step 1–5 judge called 87 of 100 closed-book answers correct and agreed with
  Claude's hand labels on only 14 of 36. Claude tested five judge set-ups against those labels (a reason-then-verdict
  prompt on qwen3:4b-instruct, llama3.2:3b and qwen3:4b with thinking; a decomposed prompt on qwen3:4b-instruct and
  qwen3:4b without thinking) and chose the decomposed prompt on qwen3:4b-instruct (27–28 of 36, the most even across
  variants); faithfulness became a separate check.
- **Answer length confounded the comparison** (closed-book answers were about 4× longer), so every variant now has
  the same "at most three sentences" rule; the answer experiment was re-run. The first run is kept as `*_run1*`.
- **Wrong citations in the demo**: numbers from the tool were cited to unrelated passages, so the answer prompt asks
  for `[tool]`; dev and test were re-run (38/40, 35/40) and the earlier test run is kept.
- Added answered-only metrics and paired bootstrap intervals, because a 2-point gap between two separate intervals
  says nothing about a paired comparison.
- All hand labels (`results/*_labels_*.jsonl`, `retrieval_miss_sample.csv`) were made by Claude, the second set blind
  to the judge; the team should check them, because Claude also wrote the system being judged.

Made after prompt 13 (the user pointed Claude to `docs/codex_review.md`, Codex's independent review). Claude checked
each finding against the saved data; findings 2–5 were confirmed and fixed:
- Claude's refusal detector treated any answer containing "do not know" as an abstention and skipped its
  faithfulness check; 6 answers made claims first. Now only a pure "I do not know." is a refusal (dense 40, rerank 31
  instead of 42, 35); the 6 hedged answers were judged (all "partly" supported); an unparsed verdict is no longer
  counted as checked.
- Claude's tool scorer took the first number in the answer, so 4 refusals in the first tool run counted as correct
  (15/40 reported, 11/40 real) and one correct verbose answer was missed. All saved runs were re-scored; the final
  runs did not change.
- Shared English names ("Smithing Template", "Music Disc", "Banner Pattern") silently picked one item. Now such names
  return an "ambiguous" error and the items get specific names; the test set was run again.
- "Recall@k is a lower bound" was an overclaim; the metric is now called the source-page hit rate.
- Claude also found its own failure analysis wrong: 4 run-1 answers it called "right from the model's own
  knowledge" were exactly those mis-scored refusals.
- Finding 1 (a verified Java 26.3 benchmark) needs the team: the README now states what the numbers do and do not show.
