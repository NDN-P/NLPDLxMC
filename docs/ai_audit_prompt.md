# The prompt used to generate `AI_AUDIT.md`

This is the course's "Standardized AI Audit Generation Prompt" (`PROJECT_INSTRUCTION.pdf`, pages 5–6), copied
exactly, with only the `[BRACKETS]` of "My project details" filled in. Team member names were not known, so they
stay as `[NAME 1]`–`[NAME 4]`. It was run in Claude Code on 2026-10-07; the output is `AI_AUDIT.md`.

```text
You are helping me create an AI Audit document for my NLP course term
project.

My project details:
- Project title: MCQA: Minecraft Wiki Q&A
- Team members: [NAME 1], [NAME 2], [NAME 3], [NAME 4]
- Domain: Minecraft (Java Edition) game knowledge: crafting, mobs, blocks, redstone, game mechanics
- AI tools we used: Claude Code (topic research, wrote the corpus fetcher, chunker, retrievers, crafting tool, evaluation scripts and documentation, ran the experiments); Codex (suggested candidate project topics)
- Corpus: 312 English Minecraft Wiki pages (about 817,000 words), plain text from the wiki API, each pinned to a revision id; plus Mojang's official Java Edition 26.3 recipe files for the crafting tool
- Embedding model chosen: BAAI/bge-small-en-v1.5
- Chunk size and overlap: 256 tokens maximum (bge tokenizer), paragraph-aligned inside one wiki section, each chunk prefixed with "Page > Section", no overlap
- Retrieval approach: BM25 + dense hybrid with RRF (k = 60) + cross-encoder reranker (cross-encoder/ms-marco-MiniLM-L6-v2, top 20 reranked to top 5)
- System variants compared in ablation: Variant A: dense-only vs. Variant B: BM25 + dense hybrid with RRF + cross-encoder reranker (also BM25-only and hybrid without reranker, each at 128/256/512-token chunks; no retrieval vs. dense vs. hybrid+rerank for answer quality; with vs. without the crafting tool)
- Evaluation metrics used: BERTScore + LLM-as-Judge (plus Recall@k and MRR for retrieval, exact match for crafting quantities)
- Optional extensions implemented: BM25 hybrid retrieval + RRF, cross-encoder reranking, agentic loop (tool-calling crafting calculator)

Generate a complete AI_AUDIT.md file in GitHub-flavored Markdown with these
exact six sections:

1. Tool Inventory — a table listing each AI tool and its primary role in
this project
2. Prompt Log — 5 entries, each with subsections: "Prompt sent", "What AI
generated", "What you changed or rejected". Pre-fill the project context in
the headers but leave the actual prompts and outputs as [FILL IN: paste the
real prompt you sent] and [FILL IN: summarize what the AI produced]
3. Decision Journal — a table of 5 rows for key design decisions with
columns: #, Decision, Owner ([Human] / [AI-suggested, Human-approved] /
[AI-decided]), Reason. Pre-fill the Decision column with the actual
decisions from my project details above (chunk size, embedding model,
retrieval approach, evaluation metrics, ablation design). Leave Owner and
Reason as [FILL IN: ...]
4. Error Catch Log — 2 entries with subsections: "What the AI said", "Why
it was wrong", "How you fixed it". Leave all content as [FILL IN: ...] — do
NOT invent errors
5. Contribution Map — a table with columns: Team Member, Human
Contribution, AI Tools Used. Pre-fill the team member names. Leave
contributions as [FILL IN: ...]
6. What Would Break? — three questions pre-filled with our specific system
details:
 a) Refer to our actual second retrieval stage or reranker if we have
one, or dense retrieval if not
 b) Reference our actual chunk size of 256 tokens
 c) Reference our actual two ablation variants by name

IMPORTANT RULES:
- Do NOT fabricate or invent any prompt content, error descriptions, or
decisions
- Every piece of real content must be a [FILL IN: ...] placeholder
- Use our actual project details (model name, chunk size, domain, etc.)
wherever the structure allows
- Output ONLY the markdown file — no explanations before or after
```

Notes for the team:
- Add any other AI tools you used to the "AI tools we used" line and to the Tool Inventory.
- `docs/ai_prompt_history.md` has the real prompts sent to Claude Code, word for word, for the Prompt Log.
- The brief says the submitted `AI_AUDIT.md` must have **no** `[FILL IN: ...]` left; any unfilled section scores zero.
