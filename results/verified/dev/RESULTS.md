# Source-grounded Java benchmark — dev

AI-curated and source-checked, awaiting independent team review. This is not human-certified accuracy.

Correctness and BERTScore below cover answerable questions only. Expected refusals are measured separately.

| Variant | Correct | Partial | Refused answerable | BERTScore F1 | Evidence in top 5 | Correct negative refusal |
|---|---:|---:|---:|---:|---:|---:|
| none | 9/16 | 2 | 0 | 0.372 | 0/16 | 2/4 |
| dense | 13/16 | 1 | 2 | 0.491 | 13/16 | 4/4 |
| rerank | 12/16 | 3 | 1 | 0.512 | 15/16 | 4/4 |

Paired differences on the same answerable questions (95% bootstrap intervals):

| Comparison | Mean | 95% CI |
|---|---:|---|
| rerank - dense: score | 0.0 | [-0.188, 0.188] |
| rerank - dense: bertscore_f1 | 0.02 | [-0.07, 0.125] |
| rerank - none: score | 0.219 | [0.062, 0.406] |
| rerank - none: bertscore_f1 | 0.139 | [0.055, 0.225] |
| dense - none: score | 0.219 | [-0.031, 0.469] |
| dense - none: bertscore_f1 | 0.119 | [0.011, 0.225] |

Common questions answered by dense and rerank: 13; BERTScore: {'none': 0.391, 'dense': 0.572, 'rerank': 0.563}.

Faithfulness counts (supported / valid, unparsed):
- none: 0/0, 0 unparsed.
- dense: 14/14, 0 unparsed.
- rerank: 14/15, 0 unparsed.

Evidence-hit counts require the entire curated quote in a top-five passage from the cited page. They are conservative for alternate valid passages and evidence spanning chunk boundaries.

All judgments are automatic; generator and judge share a model. See config.json, answers.jsonl and human_check.csv.

Pure factual refusals score incorrect; original automatic judgments remain in raw answers.
Overrides: {'none': 0, 'dense': 0, 'rerank': 0}.
