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
            self.assertEqual(mcqa.constrained_args("How much iron do 3 hoppers need?",
                                                  {"item": "hopper", "count": 15})["count"], 3)
            native = {"tool_calls": [{"function": {"name": "craft", "arguments": {"item": "hopper", "count": 15}}}]}
            with mock.patch.object(mcqa, "chat", return_value=native) as chat:
                planned = mcqa.plan_tools(q)
            chat.assert_not_called()  # explicit input can route directly to the existing validated calculator
            self.assertEqual(planned[0]["via"], "deterministic")
            self.assertNotIn("model_args", planned[0])
            self.assertEqual(mcqa.exact_quantity(q, planned), 15)

    def test_explicit_recipe_wording_is_deterministic_and_batch_aware(self):
        with mock.patch.object(mcqa, "crafting_data", return_value=FAKE), \
                mock.patch.object(mcqa, "chat", side_effect=AssertionError("explicit recipe needs no model")):
            for question in ("How many Iron Ingots for 3 hoppers?",
                             "How many Iron Ingots do 3 hoppers need?",
                             "How many Iron Ingots do I need to make 3 hoppers"):
                self.assertEqual(mcqa.answer(question)["answer"], "15 [tool]")
            recipe = mcqa.answer("What materials do I need to craft 10 torches?")
            self.assertEqual(recipe["answer_mode"], "calculator_recipe")
            self.assertEqual(recipe["tool_calls"][0]["result"]["crafts"], 3)
            self.assertIn("3 Stick", recipe["answer"])
            self.assertIsNone(mcqa.recipe_request("How many feathers does a chicken drop?"))
            self.assertIsNone(mcqa.recipe_request("What food breeds cows?"))
            self.assertIsNone(mcqa.recipe_request("Craft 3 hoppers and explain how they move items."))

    def test_two_clause_recipe_quantity_keeps_batch_rounding_and_extra_requests(self):
        with mock.patch.object(mcqa, "crafting_data", return_value=FAKE):
            with mock.patch.object(mcqa, "chat", side_effect=AssertionError("explicit recipe needs no model")):
                for question in ("I want 9 torches. How many sticks does the crafting recipe require? Reply with the number only.",
                                 "I need 9 torches. How many sticks do I need?"):
                    out = mcqa.answer(question)
                    self.assertEqual((out["answer"], out["answer_mode"]), ("3 [tool]", "calculator_exact"))
                    self.assertEqual(out["tool_calls"][0]["result"]["crafts"], 3)
            q = "I want 9 torches. How many sticks does the crafting recipe require? How do torches emit light?"
            self.assertIsNone(mcqa.recipe_request(q))
            native = {"tool_calls": [{"function": {"name": "craft", "arguments": {"item": "torch", "count": 99}}}]}
            with mock.patch.object(mcqa, "chat", side_effect=[native, {"content": "NO_TOOL"},
                                                             {"content": "3 sticks [tool]; torches emit light."}]) as chat:
                compound = mcqa.answer(q)
            self.assertEqual(chat.call_count, 3)
            self.assertEqual(compound["answer_mode"], "llm")
            self.assertIn("emit light", compound["answer"])
            self.assertEqual(compound["tool_calls"][0]["args"]["count"], 9)
            self.assertNotIn("via", compound["tool_calls"][0])  # this is an actual native model request

    def test_scope_filter_and_every_retrieval_stage_preserve_current_java(self):
        chunks = [
            {"title": "Java Edition 1.9/Development versions", "section": "Changes", "text": "Elytra uses leather"},
            {"title": "Anvil", "section": "History > Java Edition", "text": "Old repairs"},
            {"title": "Anvil", "section": "Usage > Repairing", "text": "Elytra uses phantom membranes"},
            {"title": "Grass Block", "section": "Usage", "text": "Grass can sit on bedrock blocks"},
            {"title": "Anvil", "section": "Usage", "text": "In Bedrock Edition: a different rule"},
            {"title": "Anvil", "section": "Usage", "text": "A rule [BE  only]"},
            {"title": "Chunk", "section": "Bedrock Edition > Loading", "text": "Different loading rules"},
        ]
        self.assertEqual([mcqa.scope_reason(c) for c in chunks],
                         ["historical", "historical", None, None, "mixed_edition", "mixed_edition", "other_edition"])
        mixed = {"title": "Item Frame", "section": "Usage", "text":
                 "Item Frame > Usage\nIn Java Edition, item frames are entities. In Bedrock Edition, they behave like signs. "
                 "They can be waterlogged.\nSneak to place a frame on a chest."}
        self.assertIsNone(mcqa.scope_reason(mixed))
        view = mcqa.current_text(mixed)
        self.assertIn("frames are entities", view)
        self.assertIn("Sneak to place", view)
        self.assertNotIn("Bedrock Edition", view)
        self.assertNotIn("waterlogged", view)  # do not detach another edition's follow-up sentence from its context
        r = object.__new__(mcqa.Retriever)
        r.chunks = chunks
        r.eligible = mcqa.np.array([2, 3])
        r.emb = mcqa.np.array([[10], [9], [4], [3], [8], [7], [6]], dtype=float)
        r.bm25 = mock.Mock()
        r.bm25.get_scores.return_value = r.emb[:, 0]
        model, reranker = mock.Mock(), mock.Mock()
        model.encode.return_value = mcqa.np.array([1.0])
        reranker.predict.return_value = mcqa.np.array([1.0, 2.0])
        with mock.patch.object(mcqa, "embedder", return_value=model), \
                mock.patch.object(mcqa, "reranker", return_value=reranker):
            for variant in ("dense", "bm25", "hybrid", "rerank"):
                ids = r.search("repair elytra", variant, 2)
                self.assertEqual(set(ids), {2, 3})  # filter before top-k; fill from eligible evidence
            self.assertEqual(r.search("repair elytra", "rerank", 2), [3, 2])

    def test_source_citation_points_to_the_saved_revision(self):
        retriever = mock.Mock()
        retriever.search.return_value = [0]
        retriever.chunks = [{"title": "Anvil", "section": "Usage", "text": "A current Java fact."}]
        mcqa.source_metadata.cache_clear()
        page = {"title": "Anvil", "revid": 123, "timestamp": "test"}
        with mock.patch.object(mcqa, "load_pages", return_value=[page]), \
                mock.patch.object(mcqa, "chat", return_value={"content": "A current Java fact [1]."}):
            out = mcqa.answer("A gameplay question?", retriever, use_tool=False)
        mcqa.source_metadata.cache_clear()
        self.assertEqual(out["sources"][0]["url"], "https://minecraft.wiki/?oldid=123")
        self.assertEqual(out["sources"][0]["revid"], 123)

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

    def test_item_id_wins_a_colliding_display_name(self):
        data = {**FAKE,
                "names": {"minecraft:map": "Empty Map", "minecraft:filled_map": "Map",
                          "minecraft:paper": "Paper", "minecraft:compass": "Compass"},
                "recipes": {"minecraft:map": [{"file": "map", "slots": ["minecraft:paper"] * 8
                                              + ["minecraft:compass"], "makes": 1}]}}
        with mock.patch.object(mcqa, "crafting_data", return_value=data), \
                mock.patch.object(mcqa, "chat", side_effect=AssertionError("explicit recipe needs no model")):
            for name in ("map", "maps", "minecraft:map", "empty map"):
                self.assertEqual(mcqa.craft(name)["ingredients"], {"Paper": 8, "Compass": 1})
            self.assertEqual(mcqa.find_item("minecraft:filled_map", data["names"]), "minecraft:filled_map")
            self.assertIn("error", mcqa.craft("filled map"))
            self.assertEqual(mcqa.answer("Craft a map?")["answer_mode"], "calculator_recipe")

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
        self.assertEqual(chat.call_count, 0)  # ambiguous explicit recipe is clarified without a model guessing
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
        with mock.patch.object(mcqa, "chat") as chat:
            self.assertEqual(mcqa.answer("How do I repair elytra in Java Edition 1.9?")["answer_mode"], "scope_refusal")
            self.assertEqual(mcqa.plan_tools("Craft a hopper in Minecraft Java 1.21"), [])
            chat.assert_not_called()
        self.assertFalse(mcqa.other_version("What does an anvil do in Java Edition 26.3?"))
        self.assertTrue(mcqa.other_version("Repair in Minecraft 1.9."))
        self.assertTrue(mcqa.other_version("Repair in Java Edition 23w14a?"))

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
