# Interpretation of the paired comparison

These notes are an AI inspection of saved outputs, not independent human labels. Automatic scores in `summary.json` and raw judgments remain unchanged. No implementation changes were made in response to test outputs.

The 28 cases were selected before generation. Four factual pages and six recipe products form development cases; eight different factual pages and six different recipe products form test cases. The prior 60-case factual benchmark's pages and prior saved recipe products were excluded. The unused preliminary after snapshot is preserved in `source_candidate_dev_parser`; all reported after responses use the final `source_after` snapshot, SHA256 `b5ae6351ba2b0c5b88a0f9acd1953b624589aadc2090ffd0b40b29110a70449d`.

The clearest measured gain is deterministic routing for explicit standalone quantities. Across the four canonical cases, mean generation time falls from 3.687 s to 0.008 s; across the four varied two-clause cases, it falls from 7.601 s to 0.005 s. These are in-process response times after startup, excluding index construction, judging, and launcher warmup. All eight after traces record `via=deterministic`; this gain demonstrates structured parsing and recipe arithmetic, not model learning. The four compound cases still use native model tool calls, averaging 11.908 s before and 11.128 s after. Test recipe quantities improve from 5/6 to 6/6; this is a small sample.

The factual comparison does not establish improved accuracy. Automatic test correctness is dense 7/8 before and 6/8 after, and rerank 7/8 both times. Several judgments appear too conservative on inspection:

- `improve-006`, dense before/after: “A bone is used to tame a wild wolf” receives partial credit against “Bones are used to tame a wild wolf.” The question asks which item, not the probability that one bone succeeds.
- `improve-007`, dense after: the answer explicitly identifies the wither as the source of the Nether star; the judge labels its equivalent extracted claim partial.
- `improve-010`, rerank before/after: an answer explaining that a larger slime produces smaller slimes on death is labeled partial against the shorter reference stating that it splits into smaller slimes.

These suspected judge errors are flagged for human review; they were not silently corrected. Exact curated-quote retrieval at five remains 6/8 for dense and changes from 8/8 to 7/8 for rerank. The after wolf answer cites a different supporting passage, illustrating the conservative nature of requiring one exact selected quote.

Strict pure-refusal performance on test negatives remains 2/2 for each retrieval variant. On the development wolf-health question, the after rerank answer provides general visual guidance but explicitly says it cannot provide the private world's exact health value. It fails the pure-“I do not know” metric; that metric is not comprehensive semantic refusal accuracy.

The requested-ingredient scorer does not validate the rest of a compound answer. For example, `improve-028` after gives the correct six Acacia Planks but incorrectly says a crafting table is not required for signs and is required for planks. Its tool recipe contains seven ingredient slots. Such unsupported explanations remain a real generation limitation even though all twelve after quantities are correct. The direct calculator results should not be described as fully correct compound answers.

Version filtering is a conservative current-Java heuristic. It does not verify every mechanic against Java 26.3. Retrieval still uses the existing embeddings generated from the original text, while the eligible passages can be trimmed. The source quotations and official recipe slots are checked locally; actual gameplay and reference labels are not independently human verified.

`runtime_metadata.json` supplements the generation configurations with observed cached Hugging Face revisions and package/Python versions. It was collected after baseline generation and during after generation, rather than retroactively inserted into the original configurations. Both runs used local Ollama and offline cached models, with no downloads or training.
