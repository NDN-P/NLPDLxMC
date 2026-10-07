# AI Audit — MCQA: Minecraft Wiki Q&A
**Team:** [NAME 1], [NAME 2], [NAME 3], [NAME 4]
**AI Tools Used:** Claude Code, Codex

---

## 1. Tool Inventory

| AI Tool | Primary Use in This Project |
|---|---|
| Claude Code | [FILL IN: e.g., topic research; wrote the Minecraft Wiki fetcher, the 256-token chunker, the dense / BM25 / RRF / cross-encoder retrievers, the crafting tool, `eval.py` and the documentation; ran the experiments] |
| Codex | [FILL IN: e.g., suggested candidate project topics] |
| [FILL IN: any other AI tool] | [FILL IN: its primary use] |

---

## 2. Prompt Log (minimum 5 entries)

### Entry 1 — Choosing the domain and corpus (Minecraft Wiki, 312 pages)
**Prompt sent:**
> [FILL IN: paste the real prompt you sent]

**What AI generated:**
[FILL IN: summarize what the AI produced]

**What you changed or rejected:**
[FILL IN: be specific — what you changed, fixed, restructured or rejected]

---

### Entry 2 — Token-aware chunking (256 tokens, paragraph-aligned, "Page > Section" prefix)
**Prompt sent:**
> [FILL IN: paste the real prompt you sent]

**What AI generated:**
[FILL IN: summarize what the AI produced]

**What you changed or rejected:**
[FILL IN: be specific — what you changed, fixed, restructured or rejected]

---

### Entry 3 — Retrieval pipeline (BAAI/bge-small-en-v1.5 + BM25, RRF k = 60, ms-marco-MiniLM-L6-v2 reranker)
**Prompt sent:**
> [FILL IN: paste the real prompt you sent]

**What AI generated:**
[FILL IN: summarize what the AI produced]

**What you changed or rejected:**
[FILL IN: be specific — what you changed, fixed, restructured or rejected]

---

### Entry 4 — Agentic loop: crafting-calculator tool from Mojang's Java Edition 26.3 recipe files
**Prompt sent:**
> [FILL IN: paste the real prompt you sent]

**What AI generated:**
[FILL IN: summarize what the AI produced]

**What you changed or rejected:**
[FILL IN: be specific — what you changed, fixed, restructured or rejected]

---

### Entry 5 — Evaluation harness (BERTScore + LLM-as-Judge, Recall@k / MRR ablation)
**Prompt sent:**
> [FILL IN: paste the real prompt you sent]

**What AI generated:**
[FILL IN: summarize what the AI produced]

**What you changed or rejected:**
[FILL IN: be specific — what you changed, fixed, restructured or rejected]

---

## 3. Decision Journal (minimum 5 decisions)

| # | Decision | Owner | Reason (in your own words) |
|---|---|---|---|
| 1 | Chunk size = 256 tokens maximum (bge tokenizer), paragraph-aligned inside one wiki section, "Page > Section" prefix, no overlap | [FILL IN: ...] | [FILL IN: ...] |
| 2 | Embedding model = BAAI/bge-small-en-v1.5 | [FILL IN: ...] | [FILL IN: ...] |
| 3 | Retrieval = BM25 + dense hybrid with RRF (k = 60), then cross-encoder/ms-marco-MiniLM-L6-v2 reranks the top 20 to the top 5 | [FILL IN: ...] | [FILL IN: ...] |
| 4 | Evaluation metrics = BERTScore + LLM-as-Judge (plus Recall@k and MRR for retrieval, exact match for crafting quantities) | [FILL IN: ...] | [FILL IN: ...] |
| 5 | Ablation design = dense-only vs. BM25-only vs. hybrid RRF vs. hybrid + reranker at 128/256/512-token chunks; no retrieval vs. dense vs. hybrid + reranker for answers; with vs. without the crafting tool | [FILL IN: ...] | [FILL IN: ...] |

---

## 4. Error Catch Log (minimum 2 entries)

### Error 1
**What the AI said:**
[FILL IN: ...]

**Why it was wrong:**
[FILL IN: ...]

**How you fixed it:**
[FILL IN: ...]

---

### Error 2
**What the AI said:**
[FILL IN: ...]

**Why it was wrong:**
[FILL IN: ...]

**How you fixed it:**
[FILL IN: ...]

---

## 5. Contribution Map

| Team Member | Human Contribution | AI Tools Used |
|---|---|---|
| [NAME 1] | [FILL IN: ...] | [FILL IN: ...] |
| [NAME 2] | [FILL IN: ...] | [FILL IN: ...] |
| [NAME 3] | [FILL IN: ...] | [FILL IN: ...] |
| [NAME 4] | [FILL IN: ...] | [FILL IN: ...] |

---

## 6. What Would Break? (Answer WITHOUT using AI)

Answer all three questions in your own words.

**a)** If you removed the cross-encoder reranker (cross-encoder/ms-marco-MiniLM-L6-v2, which reranks the top 20
hybrid RRF results to the top 5) from your pipeline, what specifically changes in output quality and why?

[FILL IN: ...]

**b)** Why did you chunk your documents at 256 tokens? What would happen to retrieval quality if you used 2× (512)
or ½ (128) that size?

[FILL IN: ...]

**c)** Your ablation compares Variant A: dense-only (BAAI/bge-small-en-v1.5) vs. Variant B: BM25 + dense hybrid with
RRF + cross-encoder reranker. Pick the result that surprised you most and explain the mechanism behind it — not
just "variant A scored higher" but why technically.

[FILL IN: ...]
