# Improvement comparison

AI-curated before generation; exact pinned source/official recipe checked; not independently human or game verified.

12 factual cases use 12 source pages absent from the earlier factual benchmark; dev/test pages are disjoint. 12 recipe products exclude previous saved tool sets. Cases were frozen before generation.

| Implementation | Split | Variant | Facts correct | BERTScore F1 | Evidence @5 | Pure negative refusals | Recipe quantities correct |
|---|---|---|---:|---:|---:|---:|---:|
| before | dev | dense | 4/4 | 0.457 | 4/4 | 2/2 | 0/0 |
| before | dev | rerank | 4/4 | 0.454 | 4/4 | 2/2 | 6/6 |
| before | test | dense | 7/8 | 0.636 | 6/8 | 2/2 | 0/0 |
| before | test | rerank | 7/8 | 0.605 | 8/8 | 2/2 | 5/6 |
| after | dev | dense | 4/4 | 0.452 | 4/4 | 2/2 | 0/0 |
| after | dev | rerank | 4/4 | 0.458 | 4/4 | 1/2 | 6/6 |
| after | test | dense | 6/8 | 0.654 | 6/8 | 2/2 | 0/0 |
| after | test | rerank | 7/8 | 0.6 | 7/8 | 2/2 | 6/6 |

Correctness and faithfulness are automatic judgments from the same local model as the generator; BERTScore measures textual similarity. Pure factual refusals score incorrect. The small sample has wide uncertainty and does not certify current-version game behavior.

Recipe scoring checks only the requested direct ingredient amount, not the rest of a compound explanation, inventory reuse, or recursively gathered materials. Different wording is tested explicitly. Negative counts require a pure refusal and are not comprehensive semantic refusal accuracy.

Raw answers preserve citations, tool calls, supporting quotes, rankings, and response time excluding judges. Source snapshots and configuration hashes distinguish implementations; old evaluations remain unchanged. First-call CPU model loading affects latency; these timings are illustrative, not a rigorous performance benchmark.

Dev cases may guide changes; test outputs must not guide tuning. No training or independent human labeling was performed.
