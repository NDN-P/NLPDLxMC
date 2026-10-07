# Source-grounded Java gameplay benchmark

`data/java_benchmark.jsonl` contains **60 newly curated cases** for the project's Minecraft Java **26.3** scope: 50 answerable questions across 25 pinned Wiki pages, 5 questions requiring unavailable world/server state, and 5 questions outside the scope. These questions were written from the stored source pages, rather than sampled from the older synthetic question pool.

The benchmark is **source-grounded and AI-curated, not independently human verified**. Every row has `human_reviewed: false`. Exact source checks establish that each reference has supporting text; they do not replace a Minecraft player's review or make this a representative benchmark of every Minecraft mechanic.

## Fixed splits and provenance

| Split | Answerable | Unanswerable | Out of scope | Total | Answerable source pages |
|---|---:|---:|---:|---:|---:|
| dev | 16 | 2 | 2 | 20 | 8 |
| test | 34 | 3 | 3 | 40 | 17 |

Answerable source pages are disjoint between dev and test. Development questions are IDs `java26.3-001` through `java26.3-016`; test answerable questions are `java26.3-017` through `java26.3-050`. Negative cases are `java26.3-051` through `java26.3-060`, with their split explicitly stored in each row. Use dev for decisions about prompts, thresholds, and retrieval settings; keep the test split fixed and report any previous inspection or reuse.

The corpus legitimately contains reference passages for both splits: retrieving those passages is the task. Benchmark questions, reference answers, and annotations must never be added to the retrieval index or used to train on the test split. Crafting quantity questions are evaluated separately against the Java client recipes; these 50 answerable questions cover single-page gameplay facts and do not require recipe arithmetic.

The target `version` field means the assistant is being tested within its Java 26.3 scope. Wiki pages are revision-pinned snapshots with cross-edition content, rather than game-version-specific manuals. Selected evidence comes from current gameplay sections before History and avoids Bedrock-only, Education-only, removed, or speculative features. The underlying game itself was not launched to verify each fact, so version correctness remains subject to the source's accuracy and team review.

## Row schema

- `id`, `split`, `kind`, `edition`, `version`, `question`: stable case identity and scope.
- `reference_answer`: concise factual reference, or expected refusal for negative cases. `reference` and `answer` are equivalent compatibility fields.
- `expected_behavior`: `answer`, `abstain`, or `scope_refusal`.
- `source` / `title`, `revid`, `source_timestamp`, `section`, `source_url`: exact source identity and a link to its revision.
- `evidence`: an exact contiguous excerpt of the saved plain-text source. `evidence_start_char`, `evidence_end_char`, and `evidence_sha256` make it checkable without a live website.
- `human_reviewed`, `provenance`: explicit origin and review status.
- `reason`: why a negative case cannot be answered by this assistant. Such cases deliberately have null source fields and empty evidence; absence of source text is not presented as a supporting citation.

For answerable retrieval scoring, finding the named page alone is insufficient. The retrieved text must contain the evidence, after whitespace normalization. All 50 evidence excerpts occur intact in at least one same-title chunk at **128, 256, and 512** tokens in the existing indexes. Two initially longer quotations crossed 128-token chunk boundaries; their references and evidence were narrowed to a sufficient excerpt before the benchmark was frozen. The longest retained excerpt is 44 words.

## Source map

Links point to the exact revision stored in `data/pages.jsonl`.

| IDs | Split | Page and pinned revision | Facts tested |
|---|---|---|---|
| 001–002 | dev | [Bed, 3822900](https://minecraft.wiki/w/Bed?oldid=3822900) | Sleeping dimension; time-based processes |
| 003–004 | dev | [Campfire, 3818480](https://minecraft.wiki/w/Campfire?oldid=3818480) | Fuel-free cooking; hopper loading |
| 005–006 | dev | [Powder Snow, 3822965](https://minecraft.wiki/w/Powder_Snow?oldid=3822965) | Leather boots; bucket collection |
| 007–008 | dev | [Bubble Column, 3786839](https://minecraft.wiki/w/Bubble_Column?oldid=3786839) | Soul sand; source-water requirement |
| 009–010 | dev | [Composter, 3816852](https://minecraft.wiki/w/Composter?oldid=3816852) | Farmer workstation; collecting bone meal |
| 011–012 | dev | [Cauldron, 3823172](https://minecraft.wiki/w/Cauldron?oldid=3823172) | Nether water storage; washing armor dye |
| 013–014 | dev | [Blast Furnace, 3823002](https://minecraft.wiki/w/Blast_Furnace?oldid=3823002) | Smelting scope; fuel efficiency |
| 015–016 | dev | [Item Frame, 3818661](https://minecraft.wiki/w/Item_Frame?oldid=3818661) | Java entity status; placement on chests |
| 017–018 | test | [Anvil, 3822941](https://minecraft.wiki/w/Anvil?oldid=3822941) | Retaining enchantments; elytra repair |
| 019–020 | test | [Sugar Cane, 3810018](https://minecraft.wiki/w/Sugar_Cane?oldid=3810018) | Java bone meal restriction; light independence |
| 021–022 | test | [Turtle, 3813329](https://minecraft.wiki/w/Turtle?oldid=3813329) | Breeding food; scute drops |
| 023–024 | test | [Sheep, 3821761](https://minecraft.wiki/w/Sheep?oldid=3821761) | Grazing and wool regrowth; retaining dye |
| 025–026 | test | [Zombie Villager, 3821562](https://minecraft.wiki/w/Zombie_Villager?oldid=3821562) | Curing; not converting to drowned |
| 027–028 | test | [Enderman, 3821135](https://minecraft.wiki/w/Enderman?oldid=3821135) | Block movement rule; boat/minecart confinement |
| 029–030 | test | [Llama, 3820600](https://minecraft.wiki/w/Llama?oldid=3820600) | Breeding; taming |
| 031–032 | test | [Creeper, 3822896](https://minecraft.wiki/w/Creeper?oldid=3822896) | Lightning charging; fear of cats and ocelots |
| 033–034 | test | [Bee Nest, 3818460](https://minecraft.wiki/w/Bee_Nest?oldid=3818460) | Silk Touch relocation; honey bottles |
| 035–036 | test | [Pointed Dripstone, 3820134](https://minecraft.wiki/w/Pointed_Dripstone?oldid=3820134) | Mud conversion; breaking with a trident |
| 037–038 | test | [Fishing Rod, 3820476](https://minecraft.wiki/w/Fishing_Rod?oldid=3820476) | Pulling without damage; anvil repairs |
| 039–040 | test | [Leaves, 3810011](https://minecraft.wiki/w/Leaves?oldid=3810011) | Player-placed leaves; collecting blocks |
| 041–042 | test | [Horse, 3820582](https://minecraft.wiki/w/Horse?oldid=3820582) | Taming; breeding foods |
| 043–044 | test | [Vault, 3818671](https://minecraft.wiki/w/Vault?oldid=3818671) | Trial keys; independent loot rolls |
| 045–046 | test | [Trial Spawner, 3818680](https://minecraft.wiki/w/Trial_Spawner?oldid=3818680) | Light independence; completion condition |
| 047–048 | test | [Nether Portal, 3821687](https://minecraft.wiki/w/Nether_Portal?oldid=3821687) | Optional corners; End activation restriction |
| 049–050 | test | [Cat, 3819873](https://minecraft.wiki/w/Cat?oldid=3819873) | Taming foods; fall immunity |

## Validation and reporting limits

Creation checks verified 60 distinct IDs, the 20/40 split, page disjointness, and exact quotation offsets and hashes. Every answerable excerpt was found before the page's History section and in each stored chunk-size variant. The dataset SHA-256 at creation is `5a9b8743462d255b2babb29b724b5bb70daa6d673fac9333c2875c0442179795`.

Keep negative cases separate from factual-answer correctness and BERTScore: matching the precise wording of a refusal is not the desired behavior. Score whether the assistant clearly declines to invent private state or explains the edition/domain limit. Report both factual quality and refusal behavior, the number of cases, confidence intervals, model versions, and the fact that the references and any automated judging are AI-assisted.

Before submission, team members should review the 50 question/reference/evidence triples against the pinned sources, confirm Java applicability, and mark only the cases they actually checked as human reviewed. A small manually checked subset also helps identify errors in the automated judge. The present annotation does not claim that this human work has happened.
