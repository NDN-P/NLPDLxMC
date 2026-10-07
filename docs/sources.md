# Data sources and inventory

Everything the system reads, where it came from, which exact version was used, and under what terms.

## 1. Corpus: Minecraft Wiki pages (real, human-written)

- **Source:** the Minecraft Wiki, <https://minecraft.wiki>, read through its MediaWiki API (`action=query&prop=extracts`,
  plain text, section headings kept as `== ... ==`).
- **Which pages:** the 400 page titles that the question pool (section 3) asks most about. After following redirects
  and merging titles that point to the same page, the corpus has **312 distinct pages, about 817,000 words**.
  Titles that failed as written were looked up again ignoring letter case, %-escapes and the move of `Tutorials/...`
  pages to the `Tutorial:` namespace; 14 of the 400 titles still have no page (e.g. `Block_State`, `Branch_Mining`,
  `Tree_Farming`) and were skipped.
- **Pinned version:** every page is stored with its revision id and timestamp. The full list, with a permanent link to
  the exact revision (`https://minecraft.wiki/?oldid=<revid>`), is in [`corpus_inventory.csv`](corpus_inventory.csv)
  (rebuild it with `python mcqa.py sources`). The text itself is saved in `data/pages.jsonl`; revisions are dated
  2026-02-11 to 2026-10-06 (fetched 2026-10-06/07).
- **Language:** English.
- **Licence:** Minecraft Wiki text is CC BY-NC-SA 3.0 (non-commercial reuse with attribution and the same licence).
  Images are not used. This is a non-commercial course project; `data/pages.jsonl` keeps the attribution (title and
  revision of each page).
- **Cleaning:** sections named Gallery, Renders, Screenshots, References, External links, Navigation and Videos are
  dropped (they are lists of images or links, not prose).

## 2. Crafting recipes (for the craft tool)

- **Source:** Mojang's official Minecraft **Java Edition 26.3** client (pinned release, 2026-09-15), found through
  Mojang's version manifest `https://piston-meta.mojang.com/mc/game/version_manifest_v2.json`.
- **Integrity:** the downloaded `client.jar` is checked against the SHA-1 published in the manifest:
  `e877b6a07acd633fb3bb475002175cec036e7b87`.
- **What is extracted:** crafting-table recipes (`data/minecraft/recipe/*.json`, shaped and shapeless only),
  item tags (`data/minecraft/tags/item/*.json`) and English names (`assets/minecraft/lang/en_us.json`):
  **1010 craftable items, 236 item tags, 1841 names**, saved as `data/crafting.json`.
- **Packaging:** neither the full jar nor `crafting.json` is committed (see `.gitignore`);
  `python mcqa.py fetch` rebuilds `crafting.json` from Mojang's servers. Saved evaluation cases retain selected
  recipe slots and derived quantities for inspection, rather than the full game recipe catalog.

## 3. Question pool (for evaluation only, never retrieved from)

- **Source:** Hugging Face dataset `minhaozhang/minecraft-question-answer-630k`
  (`data/train-00000-of-00001.parquet`, SHA-256 `564e47059f4d9eabda2cd98992fb6663013fcdf3eb059906ae9d3b031a9c3268`):
  **630,378** question/answer pairs with a `source` column naming the wiki page each pair came from (13,664 pages).
- **What it is:** a filtered version of `naklecha/minecraft-question-answer-700k` (CC BY-NC-SA 3.0), whose pairs were
  **generated synthetically** from Minecraft Wiki pages (by glaive.ai). It is therefore **not** the corpus (the brief
  requires a real corpus) and its answers are only imperfect references.
- **How it is used:** (1) to choose which wiki pages to fetch, (2) as evaluation questions whose `source` page is the
  retrieval label, (3) its answers as references for BERTScore and the LLM judge. The exact questions used are saved in
  `results/questions_*.jsonl`.
- **Known limits:** the pairs were generated from an older wiki (about 2024), while the corpus and recipes are from
  2026 (Java 26.3), so some reference answers are outdated; some pairs are simply wrong.

## 4. Models (downloaded from Hugging Face / Ollama on first use)

| Role | Model | Notes |
|---|---|---|
| Embeddings (dense retrieval) | `BAAI/bge-small-en-v1.5` | 33M parameters, CPU, 384-dim, 512-token limit, MIT |
| Reranker | `cross-encoder/ms-marco-MiniLM-L6-v2` | 22M parameters, CPU, Apache-2.0 |
| Generator and LLM judge | `qwen3:4b-instruct` (Ollama, Q4_K_M) | temperature 0, seed 0, Apache-2.0 |
| BERTScore | `distilroberta-base` | `bert-score` 0.3.13, rescaled with baseline |
| Judge comparison only (`scripts/judge_selection.py`) | `llama3.2:3b`, `qwen3:4b` (Ollama) | candidates that were tested as judges and not chosen |

## 5. Hand labels (made during the project)

AI-generated calibration/checking labels: `results/judge_labels_run1.jsonl` and
`results/judge_labels_run2.jsonl` (36 answers each, correct / partial / incorrect), `results/faithful_labels_run2.jsonl`
(16 answers, supported / partly / unsupported) and `results/retrieval_miss_sample.csv` (40 retrieval misses, by cause).
They were made by Claude Code (the second sets without seeing the judge's verdicts) and should be checked by the team.
Run 1 was used to choose the judge, and the two correctness sets share 12 question texts. They are not independent
human validation. The later `data/java_benchmark.jsonl` uses exact pinned source quotes and disjoint dev/test source
pages; its provenance and limitations are recorded in `docs/benchmark_sources.md`.
