"""Self-checks for the logic that is easy to get wrong:  python -m unittest test_mcqa -v"""
import unittest
from unittest import mock

import mcqa

FAKE = {"version": "test",
        "names": {"minecraft:hopper": "Hopper", "minecraft:iron_ingot": "Iron Ingot", "minecraft:chest": "Chest",
                  "minecraft:torch": "Torch", "minecraft:stick": "Stick", "minecraft:diamond": "Diamond",
                  "minecraft:coal": "Coal", "minecraft:charcoal": "Charcoal"},
        "tags": {"#minecraft:coals": ["minecraft:coal", "minecraft:charcoal"]},
        "recipes": {"minecraft:hopper": [{"file": "hopper", "slots": ["minecraft:iron_ingot"] * 5 + ["minecraft:chest"],
                                          "makes": 1}],
                    "minecraft:torch": [{"file": "torch", "slots": ["#minecraft:coals", "minecraft:stick"], "makes": 4}]}}


class TestMcqa(unittest.TestCase):
    def test_explicit_quantity_cannot_be_changed_or_remultiplied(self):
        q = "How many Iron Ingot do I need to craft 3 Hopper? Reply with the number only."
        with mock.patch.object(mcqa, "crafting_data", return_value=FAKE):
            args = mcqa.constrained_args(q, {"item": "hopper", "count": 15})
            self.assertEqual(args["count"], 3)
            result = mcqa.craft(**args)
            retriever = mock.Mock()
            retriever.search.side_effect = AssertionError("exact quantity needs no Wiki lookup")
            with mock.patch.object(mcqa, "plan_tools", return_value=[{"args": args, "result": result}]), \
                    mock.patch.object(mcqa, "chat", side_effect=AssertionError("calculator quantity must not be rewritten")):
                out = mcqa.answer(q, retriever)
            self.assertEqual((out["answer"], out["answer_mode"]), ("15 [tool]", "calculator_exact"))
            self.assertEqual((out["sources"], out["passages"]), ([], ""))
            self.assertEqual(mcqa.constrained_args(q, {"item": "chest", "count": 2})["count"], 2)
            native = {"tool_calls": [{"function": {"name": "craft", "arguments": {"item": "hopper", "count": 15}}}]}
            with mock.patch.object(mcqa, "chat", return_value=native) as chat:
                planned = mcqa.plan_tools(q)
            chat.assert_called_once()  # stop after the validated amount, instead of an unnecessary follow-up round
            self.assertEqual(mcqa.exact_quantity(q, planned), 15)

    def test_compound_quantity_question_keeps_the_other_request(self):
        q = "How many Iron Ingots do I need to craft 3 Hopper? How does a hopper transport items?"
        with mock.patch.object(mcqa, "crafting_data", return_value=FAKE):
            result = mcqa.craft("hopper", 3)
            with mock.patch.object(mcqa, "plan_tools", return_value=[{"result": result}]), \
                    mock.patch.object(mcqa, "chat", return_value={"content": "15 iron ingots; hoppers move items."}) as chat:
                out = mcqa.answer(q)
        chat.assert_called_once()
        self.assertEqual(out["answer_mode"], "llm")
        self.assertIn("move items", out["answer"])

    def test_rrf_rewards_agreement(self):
        self.assertEqual(mcqa.rrf([[1, 2], [2, 3]]), [2, 1, 3])

    def test_chunks_fit_the_budget_and_skip_gallery(self):
        count = lambda s: len(s.split())
        page = {"title": "Hopper", "text": "Intro one two\n== Crafting ==\n" + "w " * 30 + "\n== Gallery ==\nimage"}
        chunks = mcqa.chunk_page(page, 12, count)
        self.assertTrue(all(count(c["text"]) <= 12 - 2 for c in chunks))  # 2 tokens left for [CLS] and [SEP]
        self.assertEqual(chunks[0]["text"], "Hopper\nIntro one two")
        self.assertTrue(all(c["text"].startswith("Hopper > Crafting\n") for c in chunks[1:]))
        self.assertEqual(sum(c["text"].count("w") for c in chunks[1:]), 30)  # nothing lost
        self.assertFalse(any("image" in c["text"] for c in chunks))

    def test_long_word_is_split(self):
        count = len  # one "token" per character
        pieces = mcqa.split_long("ab " + "x" * 50, 8, count)
        self.assertTrue(all(count(p) <= 8 for p in pieces))
        self.assertEqual("".join(pieces).replace(" ", ""), "ab" + "x" * 50)

    def test_craft_scales_and_rounds_up(self):
        with mock.patch.object(mcqa, "crafting_data", lambda: FAKE):
            self.assertEqual(mcqa.craft("hoppers", 3)["ingredients"], {"Iron Ingot": 15, "Chest": 3})
            torch = mcqa.craft("Torch", 10)  # one craft makes 4 torches, so 10 torches need 3 crafts
            self.assertEqual((torch["crafts"], torch["ingredients"]), (3, {"any Coals (e.g. Coal)": 3, "Stick": 3}))
            self.assertIn("error", mcqa.craft("diamond", 1))
            self.assertIn("error", mcqa.craft("dragon egg", 1))
            self.assertEqual(mcqa.craft("hopper", 2)["answer"],
                             "To craft 2 Hopper you need 10 Iron Ingot, 2 Chest in total (2 crafts, each makes 1).")

    def test_item_names_singular_and_plural(self):
        names = {"minecraft:diamond_boots": "Diamond Boots", "minecraft:torch": "Torch"}
        self.assertEqual(mcqa.find_item("diamond boot", names), "minecraft:diamond_boots")
        self.assertEqual(mcqa.find_item("Torches", names), "minecraft:torch")
        self.assertEqual(mcqa.find_item("diamond_boots", names), "minecraft:diamond_boots")
        self.assertEqual(mcqa.find_item("minecraft:DIAMOND_BOOTS", names), "minecraft:diamond_boots")
        self.assertEqual(mcqa.find_item("DiamondBoots", names), "minecraft:diamond_boots")

    def test_invalid_quantities_are_not_silently_changed_to_one(self):
        with mock.patch.object(mcqa, "crafting_data", lambda: FAKE):
            for count in (0, -2, "-2", "0", 1.5, True, None, "2.5"):
                with self.subTest(count=count):
                    self.assertEqual(mcqa.craft("hopper", count)["error_code"], "invalid_count")
            self.assertEqual(mcqa.craft("minecraft:hopper", "2")["ingredients"]["Iron Ingot"], 10)
            with mock.patch.object(mcqa, "chat") as chat:
                for count in ("0", "-2", "1.5"):
                    out = mcqa.answer(f"How many Iron Ingots do I need to craft {count} Hoppers?")
                    self.assertEqual(out["answer_mode"], "clarification")
                chat.assert_not_called()

    def test_bad_tool_calls_become_errors(self):
        with mock.patch.object(mcqa, "crafting_data", lambda: FAKE):
            self.assertIn("error", mcqa.run_tool("craft", {"item": "hopper", "count": "many"}))
            self.assertIn("error", mcqa.run_tool("smelt", {"item": "hopper"}))
            self.assertIn("error", mcqa.run_tool("craft", "hopper"))  # arguments not an object
            self.assertEqual(mcqa.run_tool("craft", {"item": "hopper"})["count"], 1)

    @unittest.skipUnless((mcqa.DATA / "crafting.json").exists(), "run `python mcqa.py fetch` first")
    def test_real_recipe(self):
        self.assertEqual(mcqa.craft("hopper", 2)["ingredients"], {"Iron Ingot": 10, "Chest": 2})

    @unittest.skipUnless((mcqa.DATA / "crafting.json").exists(), "run `python mcqa.py fetch` first")
    def test_shared_names_are_ambiguous(self):
        # every armor trim template is called "Smithing Template" in the game's English names
        self.assertIn("ambiguous", mcqa.craft("smithing template", 2)["error"])
        self.assertEqual(mcqa.craft("Smithing Templates", 2)["error_code"], "ambiguous_item")
        self.assertIn("ambiguous", mcqa.craft("music disc", 1)["error"])
        coast = mcqa.craft("coast armor trim smithing template", 2)
        self.assertEqual(coast["item"], "Coast Armor Trim Smithing Template")
        self.assertIn("Cobblestone", coast["ingredients"])  # the Wild template would need Mossy Cobblestone

    def test_planner_stops_at_ambiguity_and_answer_asks_the_user(self):
        ambiguous = {"error": "ambiguous", "error_code": "ambiguous_item",
                     "options": ["Coast Armor Trim Smithing Template", "Wild Armor Trim Smithing Template"]}
        native = {"content": "", "tool_calls": [{"function": {"name": "craft",
                    "arguments": {"item": "smithing template", "count": 2}}}]}
        with mock.patch.object(mcqa, "chat", return_value=native) as chat, \
                mock.patch.object(mcqa, "run_tool", return_value=ambiguous):
            result = mcqa.answer("What do I need for 2 smithing templates?")
        self.assertEqual(chat.call_count, 1)  # no second call lets the model invent Coast or Wild
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertIn("Which specific item", result["answer"])
        self.assertIn("Coast Armor Trim", result["answer"])

    def test_calculator_result_survives_a_generator_refusal(self):
        native = {"content": "", "tool_calls": [{"function": {"name": "craft",
                    "arguments": {"item": "hopper", "count": 3}}}]}
        with mock.patch.object(mcqa, "crafting_data", lambda: FAKE), \
                mock.patch.object(mcqa, "chat", side_effect=[native, {"content": "NO_TOOL"},
                                                           {"content": "I do not know."}]):
            result = mcqa.answer("How much iron do 3 hoppers need?")
        self.assertIn("15 Iron Ingot", result["answer"])
        self.assertIn("[tool]", result["answer"])

    def test_other_edition_cannot_trigger_java_calculator_fallback(self):
        with mock.patch.object(mcqa, "chat") as chat:
            result = mcqa.answer("How much iron does a Bedrock Edition hopper need?")
        self.assertEqual(result["answer_mode"], "scope_refusal")
        self.assertEqual(result["tool_calls"], [])
        chat.assert_not_called()
        self.assertFalse(mcqa.other_edition("Can I mine bedrock in survival?"))
        self.assertTrue(mcqa.other_edition("What is this recipe in Minecraft Bedrock?"))
        self.assertFalse(mcqa.other_edition("Can I place grass on bedrock?"))
        self.assertFalse(mcqa.other_edition("What materials do I need for bedrock breaking?"))

    def test_tool_answer_scoring(self):
        import eval as ev
        q = "How many Iron Ingot do I need to craft 3 Hopper? Reply with the number only."
        self.assertEqual(ev.answer_number("15", q), 15)
        self.assertEqual(ev.answer_number("15 [tool]", q), 15)
        self.assertEqual(ev.answer_number("To craft 3 hoppers, you need 15 iron ingots [tool].", q), 15)
        self.assertIsNone(ev.answer_number("I do not know how many iron ingots are needed to craft 3 hoppers.", q))
        self.assertIsNone(ev.answer_number("You need 3 hoppers.", q))


if __name__ == "__main__":
    unittest.main()
