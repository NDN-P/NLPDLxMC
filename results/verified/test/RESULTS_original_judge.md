# Source-grounded Java benchmark — test

AI-curated and source-checked, awaiting independent team review. This is not human-certified accuracy.

Correctness and BERTScore below cover answerable questions only. Expected refusals are measured separately.

| Variant | Correct | Partial | Refused answerable | BERTScore F1 | Evidence in top 5 | Correct negative refusal |
|---|---:|---:|---:|---:|---:|---:|
| none | 9/34 | 1 | 0 | 0.294 | 0/34 | 5/6 |
| dense | 28/34 | 4 | 3 | 0.493 | 31/34 | 5/6 |
| rerank | 26/34 | 4 | 2 | 0.451 | 30/34 | 6/6 |

Paired differences on the same answerable questions (95% bootstrap intervals):

| Comparison | Mean | 95% CI |
|---|---:|---|
| rerank - dense: score | -0.059 | [-0.176, 0.059] |
| rerank - dense: bertscore_f1 | -0.042 | [-0.109, 0.012] |
| rerank - none: score | 0.544 | [0.382, 0.706] |
| rerank - none: bertscore_f1 | 0.158 | [0.096, 0.218] |
| dense - none: score | 0.603 | [0.426, 0.765] |
| dense - none: bertscore_f1 | 0.199 | [0.136, 0.259] |

Common questions answered by dense and rerank: 29; BERTScore: {'none': 0.299, 'dense': 0.524, 'rerank': 0.501}.

Faithfulness counts (supported / valid, unparsed):
- none: 0/0, 0 unparsed.
- dense: 31/32, 0 unparsed.
- rerank: 30/32, 0 unparsed.

Evidence-hit counts require the entire curated quote in a top-five passage from the cited page. They are conservative for alternate valid passages and evidence spanning chunk boundaries.

All judgments are automatic; generator and judge share a model. See config.json, answers.jsonl and human_check.csv.
