# New recipe-item holdout

40 new product IDs excluded from all prior saved tool question sets and known recipe development probes.
Gold quantities come from version-pinned recipe slots; this measures the complete routing/calculator/answer pipeline.

| Variant | Correct | Accuracy | 95% Wilson CI (%) | Tool called |
|---|---:|---:|---|---:|
| without_tool | 2/40 | 5.0% | [1.4, 16.5] | 0 |
| with_tool | 28/40 | 70.0% | [54.6, 81.9] | 39 |

False calls on 20 fixed non-recipe dev cases: 0.
Tool-enabled response modes: {'llm': 39, 'calculator_fallback': 1}.

A calculator-backed fallback is explicitly recorded; gains do not demonstrate learned arithmetic or model training.
