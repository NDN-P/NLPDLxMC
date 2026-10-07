# New recipe-item holdout

40 new product IDs excluded from all prior saved tool question sets and known recipe development probes.
Gold quantities come from version-pinned recipe slots; this measures the complete routing/calculator/answer pipeline.

| Variant | Correct | Accuracy | 95% Wilson CI (%) | Tool called |
|---|---:|---:|---|---:|
| without_tool | 1/40 | 2.5% | [0.4, 12.9] | 0 |
| with_tool | 37/40 | 92.5% | [80.1, 97.4] | 37 |

False calls on 20 fixed non-recipe dev cases: 0.
Tool-enabled response modes: {'calculator_exact': 37, 'llm': 3}.

A calculator-backed fallback is explicitly recorded; gains do not demonstrate learned arithmetic or model training.
