# Actual Codex prompts and work

These are exact user messages from this conversation. They document instructions, not a claim that the user independently wrote the resulting code.

| Prompt | Observed work |
|---|---|
| `you task is not just review you have to help build,train,evaluate and do not forget to record every process in codextodo.md` | Created the project-specific record; distinguished plans from evidence. No fine-tuning was performed. |
| `at the moment you can survey project but wait for me to let you continue` | Surveyed files only and respected the continuation boundary. |
| `review and evaluate` | Independent code/data/evaluation review, existing tests, chunk/index reproduction, retrieval subset, BERTScore/judge repetition and local diagnostics. |
| `ok fix for me. make everything to perfection` | Validated intervening Claude fixes, corrected remaining issues, added source-grounded benchmark and regression checks, ran fresh local experiments and completed technical documentation. |

The user answered **“Fully local — no API charges”** to the question about paid APIs versus local operation, and **“Claude has finished”** to the concurrency question before editing resumed. These answers establish constraints and coordination, not human approval of every model-generated design detail.

Full process evidence is in `codextodo.md`. `docs/codex_review.md` and `results/codex_review/` preserve the earlier pre-correction review. `results/pipeline_dev/` contains development probes, including failures. New source-backed experiments are under `results/verified/`.

Team members must supply authentic names/contributions, independent labels and the assignment's unaided answers. Codex has not supplied those on their behalf.
