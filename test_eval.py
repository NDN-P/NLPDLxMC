"""Regression checks for evaluation mistakes that can inflate or hide scores."""
import unittest
from unittest import mock
from pathlib import Path
import tempfile
import eval as ev


class EvaluationTests(unittest.TestCase):
    def test_check_sheet_preserves_human_grades(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as temp:
            path = Path(temp) / "human_check.csv"
            ev.write_check_sheet(path, ["id", "verdict"], [["q1", ""]])
            self.assertIn("q1", path.read_text(encoding="utf-8-sig"))
            path.write_text("id,verdict\nq1,correct\n", encoding="utf-8")
            before = path.read_bytes()
            ev.write_check_sheet(path, ["id", "verdict"], [["q1", ""]])
            self.assertEqual(path.read_bytes(), before)
    def test_benchmark_evidence_needs_the_answer_not_just_its_page(self):
        from scripts import benchmark_eval as bench
        q = {"title": "Bed", "evidence": "Sleeping is possible only in the Overworld."}
        wrong = {"title": "Bed", "text": "A bed comes in sixteen colours."}
        right = {"title": "Bed", "text": "Bed > Sleeping\nSleeping is possible only in the Overworld."}
        self.assertIsNone(bench.evidence_rank(q, [wrong]))
        self.assertEqual(bench.evidence_rank(q, [wrong, right]), 2)

    def test_benchmark_does_not_mix_expected_refusals_into_fact_metrics(self):
        from scripts import benchmark_eval as bench
        rows = []
        for v in ev.VARIANTS_QA:
            rows += [{"id": "a", "question": "answerable", "answer": "A fact.", "kind": "answerable", "variant": v,
                      "correct": {"verdict": "correct"}, "faithful": {"verdict": None},
                      "refused": False, "hedged": False, "bertscore_f1": 0.2, "evidence_rank": 2},
                     {"id": "b", "question": "negative", "answer": "I do not know.", "kind": "unanswerable", "variant": v,
                      "correct": None, "faithful": None, "refused": True, "hedged": False,
                      "bertscore_f1": 1.0, "evidence_rank": None}]
        s = bench.summarize(rows)["variants"]["dense"]
        self.assertEqual((s["answerable_n"], s["bertscore_f1_answerable"], s["negative_correct_refusal"]), (1, 0.2, 1))
        self.assertEqual((s["faithful_valid"], s["faithful_unparsed"]), (0, 1))

    def test_factual_refusal_cannot_receive_judge_credit(self):
        row = {"answer": "I do not know. [1]", "correct": {"verdict": "correct"}}
        self.assertEqual(ev.factual_verdict(row), "incorrect")
        self.assertEqual(ev.points(row), 0)
        self.assertEqual(row["correct"]["verdict"], "correct")  # original judge evidence is preserved

    def test_refusal_does_not_hide_claims(self):
        self.assertTrue(ev.refused("I don't know. [1]"))
        self.assertTrue(ev.refused(" I do not\nknow. "))
        self.assertFalse(ev.refused("The cap is 30. I do not know the other part."))
        self.assertFalse(ev.refused("You do not know."))
        row = {"answer": "The cap is 30. I do not know the other part.", "passages": "The cap is 5."}
        with mock.patch.object(ev, "ask_judge", return_value={"verdict": "partly"}) as judge:
            self.assertEqual(ev.judge_faithful(row)["verdict"], "partly")
            judge.assert_called_once()

    def test_numeric_scorer_rejects_refusals_negation_and_conflicts(self):
        q = "How many Iron Ingot do I need to craft 3 Hopper? Reply with the number only."
        self.assertEqual(ev.answer_number("15 [tool]", q), 15)
        self.assertEqual(ev.answer_number("To craft 3 hoppers, use 15 iron ingots.", q), 15)
        for answer in ("I do not know how to craft 3 hoppers.", "Not 15 iron ingots.",
                       "15 iron ingots are not needed.", "15 iron ingots or 30 iron ingots.", "-15 iron ingots."):
            self.assertIsNone(ev.answer_number(answer, q), answer)

    def test_invalid_judge_response_is_counted_as_failure(self):
        with mock.patch.object(ev.mcqa, "chat", return_value={"content": '[]'}):
            self.assertIsNone(ev.ask_judge("question", ev.CORRECT_SCHEMA)["verdict"])
        valid = '{"reference_fact":"5","answer_claim":"5","verdict":"correct"}'
        with mock.patch.object(ev.mcqa, "chat", side_effect=[{"content": "bad"}, {"content": valid}]):
            self.assertEqual(ev.ask_judge("question", ev.CORRECT_SCHEMA)["verdict"], "correct")

    def test_null_faithfulness_is_not_a_valid_verdict(self):
        rows = [{"question": "q", "variant": v, "answer": "A fact.", "refused": False, "hedged": False,
                 "correct": {"verdict": "correct"}, "faithful": {"verdict": None} if v != "none" else None,
                 "bertscore_f1": 0.5} for v in ev.VARIANTS_QA]
        with mock.patch.object(ev, "save") as save:
            ev.summarize_answers(rows)
        dense = save.call_args.args[1]["summary"]["dense"]
        self.assertEqual((dense["faithful_attempted"], dense["faithful_checked"], dense["faithful_unparsed"]), (1, 0, 1))


if __name__ == "__main__":
    unittest.main()
