"""Checks the preselected evaluation's provenance and explicit-ingredient scoring."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import eval as ev
from scripts import improvement_eval as check


class ImprovementEvaluationTests(unittest.TestCase):
    def test_frozen_sources_recipes_and_dataset_tampering(self):
        rows = check.validate()
        self.assertEqual(sum(q["kind"] == "answerable" for q in rows), 12)
        self.assertEqual(sum(q["kind"] == "recipe" for q in rows), 12)
        # Modifying a reference after seeing answers must not silently resume the same run.
        with tempfile.TemporaryDirectory(dir=check.ROOT) as folder:
            path = Path(folder) / "changed.jsonl"
            changed = [dict(q) for q in rows]
            changed[0]["reference_answer"] = "Changed after generation"
            path.write_text("".join(json.dumps(q)+"\n" for q in changed), encoding="utf-8")
            with patch.object(check, "DATASET", path):
                with self.assertRaisesRegex(ValueError, "dataset changed"):
                    check.validate()

    def test_varied_wording_scores_only_requested_ingredient(self):
        scorer_question = "How many Magenta Dye do I need to craft"
        self.assertEqual(ev.answer_number("For 9 terracotta you need 2 Magenta Dye. [tool]", scorer_question), 2)
        self.assertIsNone(ev.answer_number("I do not know how much Magenta Dye is needed for 9 terracotta.", scorer_question))
        self.assertIsNone(ev.answer_number("Use 2 Magenta Dye, or 3 Magenta Dye.", scorer_question))


if __name__ == "__main__":
    unittest.main()
