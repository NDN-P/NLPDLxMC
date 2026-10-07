# Demo session

This is the preserved earlier session. Current traces, including exact calculator output, compound requests and
known failed explanations, are in `results/verified/demo_final.json` and discussed in `docs/failure_analysis.md`.

Recorded 2026-10-07 with `demo.py` (chunk size 256, qwen3:4b-instruct, hybrid + reranker, craft tool on). Each block is the exact output for one question: the five retrieved passages (page > section), any craft-tool calls, then the answer.

## How many iron ingots do I need to craft 3 hoppers?

```text
$ python demo.py "How many iron ingots do I need to craft 3 hoppers?"
  [1] Anvil > Obtaining > Crafting
  [2] Tutorial:Nether survival > Farming > Iron production
  [3] Tutorial:Achievement guide > On a Rail > Travel by minecart to a point at least 500m in a single direction from where you started
  [4] Tutorial:Achievement guide > Body Guard > Create an Iron Golem
  [5] Tutorial:Achievement guide > Iron Man > Wear a full set of Iron Armor
  tool: craft({'item': 'hopper', 'count': 3}) -> To craft 3 Hopper you need 15 Iron Ingot, 3 Chest in total (3 crafts, each makes 1).

To craft 3 hoppers, you need 15 iron ingots [tool].
```

## What happens when I take fatal damage while holding a Totem of Undying?

```text
$ python demo.py "What happens when I take fatal damage while holding a Totem of Undying?"
  [1] Tutorial:Advancement guide/Adventure tab > Postmortal
  [2] Tutorial:Achievement guide > Cheating Death > Use the Totem of Undying to cheat death
  [3] Tutorial:Combat > Allies > Foxes
  [4] Tutorial:Exploring a Nether fortress > Preparing the equipment > Fire Resistance
  [5] Tutorial:Exploring a woodland mansion > Navigating the mansion

When you take fatal damage while holding a Totem of Undying, you will not actually die; instead, you will use up the totem, your health will regenerate (from Absorption and you gaining 1 HP), and you will gain the advancement [1]. This applies to any source of damage except void damage [1].
```

## How many Cinnabar do I need to craft 8 Cinnabar Stairs?

```text
$ python demo.py "How many Cinnabar do I need to craft 8 Cinnabar Stairs?"
  [1] Tutorial:Time-saving tips > In-game tips > Crafting
  [2] Tutorial:Achievement guide > MOAR Tools > Construct one type of each tool
  [3] Anvil > Obtaining > Crafting
  [4] Tutorial:Achievement guide > Music to my Ears > Play a music disc in a Jukebox. (PlayStation exclusive)
  [5] Tutorial:Furniture > Miscellaneous > Fancy jukebox
  tool: craft({'item': 'cinnabar_stairs', 'count': 8}) -> To craft 8 Cinnabar Stairs you need 12 Cinnabar in total (2 crafts, each makes 4).

You need 12 Cinnabar to craft 8 Cinnabar Stairs [tool].
```

## What do I need to make a cake?

```text
$ python demo.py "What do I need to make a cake?"
  [1] Tutorial:Achievement guide > The Lie! > Bake a cake using: wheat, sugar, milk, and eggs
  [2] Tutorial:Shelters > Expansions > Cake factory
  [3] Tutorial:Advancement guide/Husbandry tab > Birthday Song
  [4] Tutorial:Achievement guide > The Lie! > Bake a cake using: wheat, sugar, milk, and eggs
  [5] Tutorial:Furniture > Living room furniture > Shelves
  tool: craft({'item': 'cake', 'count': 1}) -> To craft 1 Cake you need 3 Milk Bucket, 2 Sugar, 1 any Eggs (e.g. Egg), 3 Wheat in total (1 craft, each makes 1).

To make a cake, you need 3 milk buckets, 2 sugar, 1 egg, and 3 wheat [tool]. These ingredients can be obtained by milking cows, harvesting sugar cane, collecting chicken eggs, and growing wheat on farmland [1][4].
```

## Who won the 2022 FIFA World Cup?

```text
$ python demo.py "Who won the 2022 FIFA World Cup?"
  [1] 2023 Mob Vote Event > (intro)
  [2] Mentioned features > Brief mentions > Mentioned in 2022
  [3] April Fools' Day jokes > List of April Fools' jokes > 2022
  [4] Mentioned features/Red Dragon > History
  [5] Bedrock Edition > Development > Beta and Preview test versions

I do not know.
```
