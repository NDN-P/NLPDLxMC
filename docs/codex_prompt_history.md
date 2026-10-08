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

Team names and IDs have now been supplied. Members must still supply their actual contributions/tools and the assignment's unaided answers. Independent labels are recommended for evaluation rigor. Codex has not supplied those on their behalf.

| Later prompt | Observed work |
|---|---|
| `i did try demo.It kinda slow on output.Is it need to be fix? or is it ok` | Measured cold/warm local timings, removed redundant exact-recipe work, added status feedback and optional fast gameplay mode. |
| `what is the future implement plan` | Recorded a proposed roadmap without implementing it in that turn. |
| `claude code hit limit for too long so i need you to continue. You can do everything to make improvement . and create demo bash for me i am lazy` | Authorized the current continuation: easy Windows/Bash launchers, source/evidence and crafting improvements, a separately frozen comparison and verification. See codextodo.md for actual outcomes rather than assuming every plan succeeded. |
| `does this match all the instruction provided in term project? If yes can you render me a slide that is easy to pitch` | Rechecked the brief and built/rendered the exact ten-slide pitch deck, with honest study provenance and remaining human submission requirements. The user selected English slides with Thai speaker notes. |
| `review everything one last time is it ready to summit?` / `limit hit continue` | Final requirements/code/evaluation/package review; corrected map alias precedence and an observed Ollama startup timeout, added regressions, reran 36 tests, checked the actual launcher and preserved selected live outputs including a grounding failure. Human names/contributions and unaided answers remain incomplete. |
| `team member are Natdanai Phurintanachot (67070230) and Nattapong Suphawirojlert (67070051)` / `just two people. professor accepted` | Supplied authentic names/IDs and confirmed the professor-approved two-person exception. Added the roster to the audit, cover and current submission documents; updated PDF/package. Individual contributions/tools and Section 6 remain pending rather than invented. |
