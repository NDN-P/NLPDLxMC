"""MCQA: Minecraft Wiki Q&A — token-aware chunks, dense + BM25 retrieval, cross-encoder reranker,
answers from a local Ollama model, and a crafting-calculator tool the model can call.

    python mcqa.py fetch          # download wiki pages, crafting data and the question pool into data/ (once)
    python mcqa.py index 256      # chunk the pages (chunk size in tokens) and embed the chunks
    python mcqa.py sources        # docs/corpus_inventory.csv: each page with the exact revision used
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from functools import lru_cache
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parent / "data"
# chunk size (tokens) of the final system: 128/256/512 tied on retrieval (results/RESULTS.md), and 256 gives the
# generator more context per passage than 128 at a lower reranking and prompt cost than 512
DEFAULT_SIZE = 256
EMBED_MODEL = "BAAI/bge-small-en-v1.5"          # 33M parameters, runs on CPU, 512-token limit
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "  # bge v1.5 query instruction
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"
LLM = "qwen3:4b-instruct"
OLLAMA = "http://localhost:11434/api/chat"
WIKI = "https://minecraft.wiki/api.php"
UA = {"User-Agent": "MCQA-course-project/0.1 (KMITL NLP with Deep Learning term project; non-commercial)"}
QA_URL = ("https://huggingface.co/datasets/minhaozhang/minecraft-question-answer-630k"
          "/resolve/main/data/train-00000-of-00001.parquet")
MC_VERSION = "26.3"  # pinned Java release; Wiki pages can also include other editions and history
MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
SKIP_SECTIONS = {"Gallery", "Renders", "Screenshots", "References", "External links", "Navigation", "Videos"}


# ---------- data -----------------------------------------------------------------------------------------------------

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


def qa_frame():
    """The question pool: 630k synthetic Q&A pairs, each with the wiki page it was generated from."""
    import pandas as pd
    path = DATA / "qa_630k.parquet"
    if not path.exists():
        path.write_bytes(get(QA_URL))
    return pd.read_parquet(path)


def wiki_page(title, lookup=True):
    """Plain text of one wiki page (TextExtracts) plus its revision id, so the corpus is pinned and reproducible."""
    q = {"action": "query", "prop": "extracts|revisions", "rvprop": "ids|timestamp", "titles": title,
         "explaintext": 1, "exsectionformat": "wiki", "redirects": 1, "format": "json", "formatversion": 2}
    page = json.loads(get(WIKI + "?" + urllib.parse.urlencode(q)))["query"]["pages"][0]
    if page.get("missing") or not page.get("extract"):
        # wiki titles are case-sensitive after the first letter; the question pool often capitalizes every word
        found = case_insensitive_title(title) if lookup else None
        page = wiki_page(found, lookup=False) if found else None
        return {**page, "source": title} if page else None
    rev = page["revisions"][0]
    return {"source": title, "title": page["title"], "revid": rev["revid"], "timestamp": rev["timestamp"],
            "text": page["extract"]}


def case_insensitive_title(title):
    """The wiki title that equals `title` apart from letter case and _/space, or None."""
    # the pool also has %-escaped titles and the old "Tutorials/" pages, which now live in the "Tutorial:" namespace
    title = urllib.parse.unquote(title).replace("Tutorials/", "Tutorial:", 1).replace("_", " ")
    want = title.lower()
    q = {"action": "opensearch", "search": title, "limit": 10, "format": "json"}  # redirects listed as-is
    time.sleep(1)
    return next((t for t in json.loads(get(WIKI + "?" + urllib.parse.urlencode(q)))[1] if t.lower() == want), None)


def fetch(n_pages=400):
    """The n most-asked-about pages of the question pool, the crafting data, all into data/. Safe to rerun."""
    DATA.mkdir(exist_ok=True)
    if not (DATA / "crafting.json").exists():
        fetch_crafting()
    titles = qa_frame()["source"].value_counts().index[:n_pages]
    out = DATA / "pages.jsonl"
    saved = [json.loads(line) for line in out.open(encoding="utf-8")] if out.exists() else []
    saved = [p for p in saved if not p.get("missing")]  # titles not found last time are tried again
    out.write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in saved), encoding="utf-8")
    done = {p["source"] for p in saved}
    with out.open("a", encoding="utf-8") as f:
        for i, title in enumerate(t for t in titles if t not in done):
            page = wiki_page(title)
            f.write(json.dumps(page or {"source": title, "missing": True}, ensure_ascii=False) + "\n")
            f.flush()
            print(f"{len(done) + i + 1}/{n_pages} {title}", flush=True)
            time.sleep(1)  # polite: one request per second


def load_pages():
    """Fetched pages, one per wiki title (several question-pool titles can redirect to the same page)."""
    pages = {}
    with (DATA / "pages.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            p = json.loads(line)
            if not p.get("missing"):
                pages.setdefault(p["title"], p)
    return list(pages.values())


def inventory():
    """docs/corpus_inventory.csv: every page in the corpus with the exact revision used."""
    import csv
    path = DATA.parent / "docs" / "corpus_inventory.csv"
    pages = sorted(load_pages(), key=lambda p: p["title"])
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["title", "revid", "timestamp", "words", "url"])
        for p in pages:
            w.writerow([p["title"], p["revid"], p["timestamp"], len(p["text"].split()),
                        f"https://minecraft.wiki/?oldid={p['revid']}"])
    print(f"{len(pages)} pages, {sum(len(p['text'].split()) for p in pages)} words -> {path}")


def source_to_title():
    """Question-pool source title -> canonical wiki title (follows redirects)."""
    m = {}
    for line in (DATA / "pages.jsonl").open(encoding="utf-8"):
        p = json.loads(line)
        if not p.get("missing"):
            m[p["source"]] = p["title"]
    return m


# ---------- chunking -------------------------------------------------------------------------------------------------

def chunk_page(page, size, count):
    """Split a page into chunks of at most `size` tokens (`count` = the embedding model's token counter).
    Chunks follow paragraph boundaries inside one section and start with "Title > Section" so every chunk
    says where it comes from; a paragraph longer than the budget is cut into token windows."""
    chunks, section, paras = [], [], []

    def flush():
        head = page["title"] + (" > " + " > ".join(section) if section else "") + "\n"
        budget = size - count(head) - 2  # 2 = the model's [CLS] and [SEP]
        cur = []
        for p in paras:
            for piece in split_long(p, budget, count):
                if cur and count("\n".join(cur + [piece])) > budget:
                    chunks.append({"title": page["title"], "section": " > ".join(section), "text": head + "\n".join(cur)})
                    cur = []
                cur.append(piece)
        if cur:
            chunks.append({"title": page["title"], "section": " > ".join(section), "text": head + "\n".join(cur)})
        paras.clear()

    for line in page["text"].splitlines():
        m = re.fullmatch(r"(={2,6})\s*(.*?)\s*\1", line.strip())
        if m:
            flush()
            level = len(m.group(1)) - 1          # "== X ==" is level 1
            section = section[:level - 1] + [m.group(2)]
        elif line.strip() and not (section and section[0] in SKIP_SECTIONS):
            paras.append(line.strip())
    flush()
    return chunks


def split_long(text, budget, count):
    if count(text) <= budget:
        return [text]
    words, out, cur = [p for w in text.split() for p in split_word(w, budget, count)], [], []
    for w in words:  # word windows keep the code tokenizer-agnostic; each window is re-checked with `count`
        if cur and count(" ".join(cur + [w])) > budget:
            out.append(" ".join(cur))
            cur = []
        cur.append(w)
    return out + [" ".join(cur)] if cur else out


def split_word(w, budget, count):
    """A "word" over the budget (e.g. a long command with no spaces) is halved until every piece fits."""
    if count(w) <= budget or len(w) < 2:
        return [w]
    return split_word(w[:len(w) // 2], budget, count) + split_word(w[len(w) // 2:], budget, count)


@lru_cache(maxsize=1)
def embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBED_MODEL, device="cpu")


def build_index(size=256):
    model = embedder()
    count = lambda s: len(model.tokenizer.encode(s, add_special_tokens=False))
    chunks = [c for page in load_pages() for c in chunk_page(page, size, count)]
    emb = model.encode([c["text"] for c in chunks], batch_size=64, normalize_embeddings=True, show_progress_bar=True)
    np.save(DATA / f"emb_{size}.npy", emb.astype(np.float32))
    with (DATA / f"chunks_{size}.jsonl").open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"{len(chunks)} chunks of at most {size} tokens from {len(load_pages())} pages")


# ---------- retrieval ------------------------------------------------------------------------------------------------

def words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def rrf(rankings, k=60):
    """Reciprocal rank fusion: each list adds 1 / (k + rank); k=60 as in Cormack et al. (2009)."""
    score = Counter()
    for ranking in rankings:
        for rank, doc in enumerate(ranking, 1):
            score[doc] += 1 / (k + rank)
    return [doc for doc, _ in score.most_common()]


OTHER_EDITION_TEXT = re.compile(r"\b(?:bedrock|pocket|legacy console|education) edition\b|"
                               r"\bMinecraft(?:Edu| Education)\b|\[\s*BE\s+only\s*\]", re.I)


def current_text(chunk):
    """A conservative Java passage view; original files and embedding rows remain untouched."""
    header, newline, body = chunk["text"].partition("\n")
    if not newline:
        header, body = "", header
    lines = []
    for line in body.splitlines():
        kept, other_context = [], False
        for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z])", line):
            if OTHER_EDITION_TEXT.search(sentence):
                other_context = True
                continue
            if re.search(r"\bJava Edition\b|\[\s*JE\s+only\s*\]", sentence, re.I):
                other_context = False
            if not other_context:
                kept.append(sentence)
        if kept:
            lines.append(" ".join(kept))
    return (header + newline if lines and newline else "") + "\n".join(lines)


def scope_reason(chunk, view=None):
    """Why a stored passage cannot establish current Java behavior, or None when eligible.

    This is a conservative metadata/text filter, not verification that every surviving claim applies to 26.3.
    Mixed-edition chunks are excluded only when their filtered passage view contains no eligible body text.
    """
    title, section = chunk["title"], chunk.get("section", "")
    heading = title + " > " + section
    if OTHER_EDITION_TEXT.search(heading):
        return "other_edition"
    if (re.search(r"\b(?:version history|removed features|unused features|pre-flattening|before \d|"
                  r"development versions|April Fools|Indev|mentioned features|unused textures)\b|\(old\)",
                  title, re.I) or
            re.search(r"(?:^| > )(?:History\b|Legacy\b|Removed\b|Temporary features\b|Old\b|Before \d|April Fools\b)",
                      section, re.I)):
        return "historical"
    version = re.search(r"\bJava Edition (\d[\w.]*)", heading, re.I)
    if version and version[1].rstrip(".") != MC_VERSION:
        return "other_version"
    if not (current_text(chunk) if view is None else view).strip():
        return "mixed_edition"
    return None


class Retriever:
    def __init__(self, size=256):
        from rank_bm25 import BM25Okapi
        with (DATA / f"chunks_{size}.jsonl").open(encoding="utf-8") as stream:
            stored = [json.loads(line) for line in stream]
        self.chunks = []
        for c in stored:
            view = current_text(c)
            self.chunks.append({**c, "text": view, "text_filtered": view != c["text"]})
        self.emb = np.load(DATA / f"emb_{size}.npy")
        self.bm25 = BM25Okapi([words(c["text"]) for c in self.chunks])
        reasons = [scope_reason(c, view["text"]) for c, view in zip(stored, self.chunks)]
        self.eligible = np.array([i for i, reason in enumerate(reasons) if reason is None], dtype=int)
        self.scope_exclusions = dict(Counter(reason for reason in reasons if reason))
        self.scope_trimmed = sum(c["text"] != view["text"] for c, view in zip(stored, self.chunks))
        # ponytail: existing dense rows include removed edition clauses; rebuild only if measured retrieval suffers.

    def dense(self, q, k=10):
        v = embedder().encode(QUERY_PREFIX + q, normalize_embeddings=True)
        scores = self.emb @ v  # cosine similarity: vectors are normalized
        return self.eligible[np.argsort(-scores[self.eligible])[:k]].tolist()

    def sparse(self, q, k=10):
        scores = self.bm25.get_scores(words(q))
        return self.eligible[np.argsort(-scores[self.eligible])[:k]].tolist()

    def hybrid(self, q, k=10, pool=50):
        return rrf([self.dense(q, pool), self.sparse(q, pool)])[:k]

    def rerank(self, q, k=10, pool=20):
        ids = self.hybrid(q, pool)
        if not ids:
            return []
        scores = reranker().predict([(q, self.chunks[i]["text"]) for i in ids])
        return [ids[j] for j in np.argsort(-scores)[:k]]

    def search(self, q, variant="rerank", k=5):
        return {"dense": self.dense, "bm25": self.sparse, "hybrid": self.hybrid, "rerank": self.rerank}[variant](q, k)


@lru_cache(maxsize=1)
def reranker():
    from sentence_transformers import CrossEncoder
    return CrossEncoder(RERANK_MODEL, device="cpu")


# ---------- crafting tool --------------------------------------------------------------------------------------------

def fetch_crafting():
    """Crafting recipes, item tags and English names from Mojang's official client jar for MC_VERSION.
    Only the extracted data is kept (data/crafting.json); the jar itself is not saved or redistributed."""
    import hashlib
    import io
    import zipfile
    version = next(v for v in json.loads(get(MANIFEST))["versions"] if v["id"] == MC_VERSION)
    client = json.loads(get(version["url"]))["downloads"]["client"]
    jar = get(client["url"])
    if hashlib.sha1(jar).hexdigest() != client["sha1"]:
        raise SystemExit("client.jar checksum mismatch")
    z = zipfile.ZipFile(io.BytesIO(jar))
    recipes, tags = {}, {}
    for f in z.namelist():
        if f.startswith("data/minecraft/tags/item/") and f.endswith(".json"):
            tags["#minecraft:" + f[25:-5]] = [v["id"] if isinstance(v, dict) else v for v in json.loads(z.read(f))["values"]]
        elif f.startswith("data/minecraft/recipe/") and f.endswith(".json"):
            r = json.loads(z.read(f))
            if r.get("type") == "minecraft:crafting_shaped":
                slots = [r["key"][c] for row in r["pattern"] for c in row if c != " "]
            elif r.get("type") == "minecraft:crafting_shapeless":
                slots = r["ingredients"]
            else:
                continue  # smelting, stonecutting, smithing and special recipes are not crafting-table recipes
            res = r["result"]
            recipes.setdefault(res["id"], []).append(
                {"file": f[22:-5], "slots": [ingredient(x) for x in slots], "makes": res.get("count", 1)})
    lang = json.loads(z.read("assets/minecraft/lang/en_us.json"))
    names = {}
    for key, text in lang.items():  # the item name wins over the block name ("Wheat", not the crop block "Wheat Crops")
        m = re.fullmatch(r"(item|block)\.minecraft\.([a-z0-9_]+)", key)
        if m and (m.group(1) == "item" or "minecraft:" + m.group(2) not in names):
            names["minecraft:" + m.group(2)] = text
    for rid, opts in recipes.items():  # the recipe file named after the item first ("hopper" before "hopper_from_x")
        opts.sort(key=lambda o: (o["file"] != rid.split(":")[1], o["file"]))
    (DATA / "crafting.json").write_text(json.dumps(
        {"version": MC_VERSION, "client_sha1": client["sha1"], "names": names, "tags": tags, "recipes": recipes},
        ensure_ascii=False), encoding="utf-8")


def ingredient(x):
    """A recipe ingredient as "minecraft:id" or "#minecraft:tag"; for a list of alternatives the first is used."""
    if isinstance(x, list):
        x = x[0]
    if isinstance(x, dict):
        x = "#" + x["tag"] if "tag" in x else x["item"]
    if ":" not in x.lstrip("#"):  # add the namespace if a file leaves it out
        x = "#minecraft:" + x[1:] if x.startswith("#") else "minecraft:" + x
    return x


@lru_cache(maxsize=1)
def crafting_data():
    data = json.loads((DATA / "crafting.json").read_text(encoding="utf-8"))
    # Some English names are shared by many items: every armor trim template is "Smithing Template", every disc
    # "Music Disc", every banner pattern "Banner Pattern". Those items get a name built from their id instead
    # ("Wild Armor Trim Smithing Template"), and the shared name is kept only to report it as ambiguous.
    by_name = {}
    for iid, n in data["names"].items():
        by_name.setdefault(n.lower(), []).append(iid)
    data["ambiguous"] = {n: sorted(ids) for n, ids in by_name.items() if len(ids) > 1}
    for ids in data["ambiguous"].values():
        for iid in ids:
            data["names"][iid] = iid.split(":")[1].replace("_", " ").title()
    return data


def label(x, data):
    """Display name; a tag is shown as its only item, or as "any X (e.g. first item)"."""
    names, tags = data["names"], data.get("tags", {})
    if not x.startswith("#"):
        return names.get(x, x.split(":")[1].replace("_", " ").title())
    members = tags.get(x, [])
    if len(members) == 1:
        return label(members[0], data)
    first = members[0] if members else None
    while first and first.startswith("#"):
        first = (tags.get(first) or [None])[0]
    pretty = "any " + x.split(":")[1].split("/")[-1].replace("_", " ").title()
    return f"{pretty} (e.g. {label(first, data)})" if first else pretty


def item_keys(name):
    """Case-insensitive display names, item IDs and ordinary singular/plural spellings."""
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(name).strip())
    key = name.lower().removeprefix("minecraft:").replace("_", " ")
    return (key, key[:-1] if key.endswith("s") else key,
            key[:-2] if key.endswith("es") else key, key + "s")


def find_item(name, names):
    # Item IDs win collisions such as map (empty map) versus the filled map's display name "Map".
    lookup = {**{n.lower(): i for i, n in names.items()}, **{i.split(":")[1].replace("_", " "): i for i in names}}
    for k in item_keys(name):
        if k in lookup:
            return lookup[k]
    return None


def craft(item, count=1):
    """Ingredients needed to craft `count` of `item` with its main crafting-table recipe."""
    data = crafting_data()
    names = data["names"]
    if isinstance(count, bool) or not (isinstance(count, int) or
                                    isinstance(count, str) and re.fullmatch(r"\+?[0-9]+", count.strip())):
        return {"error": "count must be a positive integer", "error_code": "invalid_count"}
    count = int(count)
    if count < 1:
        return {"error": "count must be a positive integer", "error_code": "invalid_count"}
    iid = find_item(str(item), names)
    shared = next((data.get("ambiguous", {})[key] for key in item_keys(item)
                   if key in data.get("ambiguous", {})), None)
    if shared:  # a name shared by several items: never guess which one was meant
        options = [names[i] for i in shared]
        return {"error": f"'{item}' is ambiguous: please specify which item you mean.",
                "error_code": "ambiguous_item", "options": options}
    if iid is None:
        return {"error": f"unknown item: {item}"}
    options = data["recipes"].get(iid)
    if not options:
        return {"error": f"{label(iid, data)} has no crafting-table recipe (it is mined, smelted, traded or found)"}
    r = options[0]
    crafts = (count + r["makes"] - 1) // r["makes"]
    ingredients = {label(x, data): n * crafts for x, n in Counter(r["slots"]).items()}
    # a plain sentence too: a small model copies it more reliably than it reads the numbers out of the JSON
    summary = (f"To craft {count} {label(iid, data)} you need " + ", ".join(f"{n} {x}" for x, n in ingredients.items())
               + f" in total ({crafts} craft{'s' if crafts > 1 else ''}, each makes {r['makes']}).")
    return {"answer": summary, "item": label(iid, data), "item_id": iid,
            "ingredient_ids": {x: n * crafts for x, n in Counter(r["slots"]).items()},
            "count": count, "crafts": crafts, "makes_per_craft": r["makes"],
            "ingredients": ingredients, "recipe_variants": len(options), "game_version": data["version"]}


CRAFT_TOOL = {"type": "function", "function": {
    "name": "craft",
    "description": "Crafting calculator (Java Edition 26.3): the ingredients needed to craft a number of a Minecraft item. "
                   "Call it again for an ingredient to go one level deeper.",
    "parameters": {"type": "object", "required": ["item", "count"], "properties": {
        "item": {"type": "string", "description": "the item to be crafted (the product, not an ingredient), "
                                                  "e.g. hopper, iron pickaxe"},
        "count": {"type": "integer", "minimum": 1,
                  "description": "how many of the product are wanted; use 1 if unspecified"}},
        "additionalProperties": False}}}


# ---------- answering ------------------------------------------------------------------------------------------------

# Every variant gets the same length rule, so answer length does not differ between the variants being compared
# (without it the closed-book answers were 4x longer, which lowers BERTScore and sways an LLM judge).
BRIEF = " Answer in at most three sentences."
SYSTEM = ("You answer questions about Minecraft (Java Edition 26.3) using only the numbered wiki passages. "
          "For questions specifically about Bedrock, Education, Pocket or Console Edition, reply \"I do not know.\" "
          "Other editions and explicitly historical or removed mechanics do not establish current Java behavior. "
          "Cite the passages you use like [1]. If the passages do not contain the answer, reply \"I do not know.\""
          + BRIEF)
CLOSED_BOOK = ("You answer questions about current Minecraft Java Edition 26.3 from your own knowledge. "
               "For questions specifically about Bedrock, Education, Pocket or Console Edition, reply "
               "\"I do not know.\"" + BRIEF)  # no retrieval
# The tool is used in two steps. Offered the tool together with the passages, the 4B model mostly answered "I do not
# know" from the passages instead of calling it (results/tool_run1_before_fix.json: 14 calls in 40 crafting questions).
# Offered the tool with the bare question, it calls it reliably and leaves other questions alone. So: (1) plan: the
# model sees only the question and may call the tool; (2) answer: it sees the passages and the tool results, no tools.
PLAN = ("You are a Minecraft Java Edition 26.3 crafting assistant. Your task is to use tools, not answer the question. "
        "If the question specifically asks about another game edition, do not call a tool; reply NO_TOOL. "
        "Call craft for questions about a crafting-table recipe, its ingredients/materials, or the quantity of an "
        "ingredient needed for a product. The user need not say 'craft': asking what a product needs, costs or "
        "takes to make is a recipe question. Choose the PRODUCT as item, not the ingredient being counted. "
        "Use the requested product quantity; use 1 when no quantity is given. Do not invent a specific variant of "
        "a generic item name. If a result requests clarification, stop and ask the user. Call again for an ingredient "
        "only when the user explicitly asks for its raw materials or another crafting level. "
        "Do not call craft for mob drops, mining yields, spawning, trading, breeding or game mechanics. "
        "For any other question, reply NO_TOOL.")
# Fallback when the model made no tool call: a forced decision, as JSON constrained by a schema (Ollama structured
# output). On the dev questions the model skipped the tool in 13 of 40 crafting questions with native tool calling.
ROUTE = ("Classify the Minecraft question. A crafting-table recipe, ingredients/materials, or an ingredient quantity "
         "needed to make a product means craft=true, even if the word 'craft' is absent. 'What does PRODUCT need?' "
         "and 'How much INGREDIENT does PRODUCT take?' are recipe questions. Give the PRODUCT as item, not the "
         "ingredient; count is the product quantity (1 if unspecified). Preserve generic item names: do not invent "
         "a color, wood type, pattern or template variant. Mob drops, mining yields, spawning, breeding, trading "
         "and other mechanics mean craft=false, item='', count=0. Questions specifically about another Minecraft "
         "edition also mean craft=false. Return only the schema's JSON object.\nExamples: "
         "How much leather does a book take? -> {\"craft\":true,\"item\":\"book\",\"count\":1}. "
         "How many eggs for four pumpkin pies? -> {\"craft\":true,\"item\":\"pumpkin pie\",\"count\":4}. "
         "What does an observer cost? -> {\"craft\":true,\"item\":\"observer\",\"count\":1}. "
         "How many feathers does a chicken drop? -> {\"craft\":false,\"item\":\"\",\"count\":0}.")
ROUTE_SCHEMA = {"type": "object", "required": ["craft", "item", "count"], "properties": {
    "craft": {"type": "boolean"}, "item": {"type": "string"}, "count": {"type": "integer"}}}
SYSTEM_TOOL = ("You answer questions about Minecraft (Java Edition 26.3) using the numbered wiki passages and the craft "
               "tool results. For questions specifically about Bedrock, Education, Pocket or Console Edition, reply "
               "\"I do not know.\" Use only current Java facts from the "
               "evidence. The tool results come from Mojang's official recipe files and their numbers are already "
               "totals for the amount asked; for crafting amounts, trust them over the passages. A successful tool "
               "result IS sufficient evidence: answer from it even if the passages omit the recipe. Do not multiply "
               "the totals again. Other editions and historical or removed mechanics do not establish current "
               "Java behavior. Cite each fact's "
               "source: a passage like [1], the tool results as [tool]; never cite a passage for a fact that came "
               "from the tool. If neither the passages nor the tool results contain the answer, reply "
               "\"I do not know.\"" + BRIEF)
CLOSED_BOOK_TOOL = ("You answer questions about Minecraft (Java Edition 26.3) from your own knowledge and the craft tool "
                    "results, which come from Mojang's official recipe files; their numbers are already totals for the "
                    "amount asked. For questions specifically about Bedrock, Education, Pocket or Console Edition, "
                    "reply \"I do not know.\"" + BRIEF)


def chat(messages, tools=None, fmt=None, model=None, think=None, num_predict=512):
    """One Ollama chat call (temperature 0, fixed seed). `fmt` is "json" or a JSON schema for structured output;
    `think` switches a thinking model's reasoning on or off (its reasoning is returned separately, not in content)."""
    body = {"model": model or LLM, "messages": messages, "stream": False,
            "options": {"temperature": 0, "seed": 0, "num_predict": num_predict}}
    if tools:
        body["tools"] = tools
    if fmt:
        body["format"] = fmt
    if think is not None:
        body["think"] = think
    req = urllib.request.Request(OLLAMA, json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read())["message"]


def run_tool(name, args):
    """Run a tool call from the model; bad names or arguments become an error message the model can read."""
    if name != "craft":
        return {"error": f"unknown tool: {name}"}
    if not isinstance(args, dict):
        return {"error": "tool arguments must be an object"}
    try:
        return craft(args.get("item", ""), args.get("count", 1))
    except (TypeError, ValueError, AttributeError) as e:
        return {"error": f"bad arguments {args}: {e}"}


def recipe_context(question):
    """Ground the planner's recipe knowledge without choosing the product or calculating the requested quantity."""
    data = crafting_data()
    matches = []
    for iid, recipes in data["recipes"].items():
        aliases = (data["names"].get(iid, ""), iid.split(":")[1].replace("_", " "))
        if any(alias and re.search(r"(?<!\w)" + re.escape(alias.lower()) + r"(?:s|es)?(?!\w)",
                                   question.lower()) for alias in aliases):
            recipe = recipes[0]
            ingredients = ", ".join(f"{n} {label(x, data)}" for x, n in Counter(recipe["slots"]).items())
            matches.append(f"{label(iid, data)}: one craft uses {ingredients}; produces {recipe['makes']}.")
    return "\n".join(matches[:12])


def other_edition(question):
    """Explicit edition requests are outside this Java-only assistant; 'mine bedrock' is still a Java question."""
    return bool(re.search(r"\b(?:bedrock|education|pocket|console)\s+edition\b|"
                          r"\bminecraft\s+bedrock\b|\b(?:minecraft|in|on|for)\s+(?:education|pocket|console)\b",
                          question, re.I))


def other_version(question):
    """An explicitly requested different Java release is outside the pinned assistant's scope."""
    versions = re.findall(r"\b(?:Java(?: Edition)?|Minecraft(?: Java(?: Edition)?)?|version)\s+"
                          r"(\d+(?:\.\d+)+(?:[-_][\w-]+)?|\d{2}w\d{2}[a-z])\b", question, re.I)
    return any(version != MC_VERSION for version in versions)


def recipe_request(question, standalone=True):
    """Parse a few explicit recipe forms; unresolved wording stays with the model's planner.

    Return raw names so ambiguous products are clarified rather than arbitrarily resolved.
    Compound questions may constrain an explicit first quantity, but never take the direct-answer shortcut.
    """
    first, mark, rest = question.strip().partition("?")
    if standalone and mark and not re.fullmatch(r"\s*(?:Reply with the number only\.?\s*)?", rest, re.I):
        return None
    first = first.rstrip(". ")
    patterns = (
        r"i (?:want|need) (?P<product>.+?)\.\s*how (?:many|much) (?P<ingredient>.+?) "
        r"(?:do i need|does the (?:crafting )?recipe (?:require|need|take))",
        r"how (?:many|much) (?P<ingredient>.+?) do i need to (?:craft|make) (?P<product>.+)",
        r"how (?:many|much) (?P<ingredient>.+?) (?:do|does) (?P<product>.+?) (?:need|require|take)(?: to (?:craft|make))?",
        r"how (?:many|much) (?P<ingredient>.+?) (?:for|to (?:craft|make)) (?P<product>.+)",
        r"what (?:ingredients|materials) do i need (?:to (?:craft|make)|for) (?P<product>.+)",
        r"what do i need (?:to (?:craft|make)|for) (?P<product>.+)",
        r"(?:how do i |how to )?(?:craft|make) (?P<product>.+)",
    )
    match = next((m for pattern in patterns if (m := re.fullmatch(pattern, first, re.I))), None)
    if not match:
        return None
    product = match["product"]
    quantity = re.fullmatch(r"([+-]?\d+(?:\.\d+)?)\s+(.+)", product)
    count = quantity[1] if quantity else "1"
    product = quantity[2] if quantity else re.sub(r"^(?:a|an)\s+", "", product, flags=re.I)
    names = crafting_data()["names"]
    shared = crafting_data().get("ambiguous", {})
    if not find_item(product, names) and not any(key in shared for key in item_keys(product)):
        return None  # includes raw-material chains and extra requests joined with "and"
    count = int(count) if re.fullmatch(r"[+-]?\d+", count) else count
    return {"item": product, "count": count, "ingredient": match.groupdict().get("ingredient")}


def quantity_request(question):
    """Explicit quantity requests are input constraints, not amounts the model may silently change."""
    request = recipe_request(question, standalone=False)
    if not request or not request["ingredient"]:
        return None
    names = crafting_data()["names"]
    ingredient, product = find_item(request["ingredient"], names), find_item(request["item"], names)
    return (ingredient, product, request["count"]) if ingredient and product else None


def constrained_args(question, args):
    request = recipe_request(question, standalone=False)
    names = crafting_data()["names"]
    product = find_item(request["item"], names) if request else None
    if product and isinstance(args, dict) and find_item(str(args.get("item", "")), names) == product:
        return {**args, "count": request["count"]}
    return args


def exact_quantity(question, calls):
    """A validated direct ingredient amount fully answers a standalone explicit quantity request."""
    request = quantity_request(question)
    if not request or not recipe_request(question):
        return None
    return next((c["result"]["ingredient_ids"][request[0]] for c in calls
                 if c["result"].get("item_id") == request[1] and c["result"].get("count") == request[2]
                 and request[0] in c["result"].get("ingredient_ids", {})), None)


def plan_tools(question, rounds=3):
    """Explicit standalone recipe forms route deterministically to the validated calculator.
    Otherwise the model sees matching one-craft recipes and may call the tool up to `rounds` times;
    a second round can look up an ingredient's recipe, and ROUTE retries if there were no native calls.
    Returns calls/results with deterministic/structured routes labelled honestly."""
    if other_edition(question) or other_version(question):
        return []
    direct = recipe_request(question)
    if direct:
        args = {"item": direct["item"], "count": direct["count"]}
        result = run_tool("craft", args)
        ingredient = find_item(direct["ingredient"], crafting_data()["names"]) if direct["ingredient"] else None
        if "error" in result or not direct["ingredient"] or ingredient in result.get("ingredient_ids", {}):
            return [{"args": args, "result": result, "via": "deterministic"}]
    context = recipe_context(question)
    request = question + ("\n\nOfficial recipes mentioning items in the question (one craft only; call the tool for "
                          "the requested totals):\n" + context if context else "")
    messages = [{"role": "system", "content": PLAN}, {"role": "user", "content": request}]
    calls = []
    for _ in range(rounds):
        msg = chat(messages, [CRAFT_TOOL])
        if not msg.get("tool_calls"):
            break
        messages.append(msg)
        for tc in msg["tool_calls"]:
            function = tc.get("function", {}) if isinstance(tc, dict) else {}
            if not isinstance(function, dict):
                function = {}
            model_args = function.get("arguments", {})
            args = constrained_args(question, model_args)
            result = run_tool(function.get("name", ""), args)
            calls.append({"args": args, "model_args": model_args, "result": result})
            messages.append({"role": "tool", "content": json.dumps(result)})
            if result.get("error_code") == "ambiguous_item":
                return calls  # only the user can choose a variant; the planner must not invent one
            if exact_quantity(question, calls) is not None:
                return calls  # the standalone request is satisfied; another planning round cannot improve the amount
    if not calls:  # no native tool call: ask for a forced yes/no decision with the arguments
        try:
            j = json.loads(chat([{"role": "system", "content": ROUTE}, {"role": "user", "content": request}],
                                fmt=ROUTE_SCHEMA)["content"])
        except (ValueError, KeyError, TypeError):
            j = {}
        if isinstance(j, dict) and j.get("craft") is True and j.get("item"):
            model_args = {"item": j["item"], "count": j.get("count", 1)}
            args = constrained_args(question, model_args)
            calls.append({"args": args, "model_args": model_args, "result": run_tool("craft", args), "via": "route"})
    return calls


def answer(question, retriever=None, variant="rerank", k=5, use_tool=True):
    """Use direct recipe arithmetic when fully parsed; otherwise plan tools, retrieve k passages and generate."""
    if other_edition(question) or other_version(question):
        return {"answer": "I do not know.", "answer_mode": "scope_refusal", "tool_calls": [],
                "passages": "", "sources": []}
    request = recipe_request(question, standalone=False) if use_tool else None
    if request and (not isinstance(request["count"], int) or request["count"] < 1):
        return {"answer": "Please request a positive whole number of crafted items.",
                "answer_mode": "clarification", "tool_calls": [], "passages": "", "sources": []}
    calls = plan_tools(question) if use_tool else []
    ambiguous = next((c["result"] for c in calls if c["result"].get("error_code") == "ambiguous_item"), None)
    amount = exact_quantity(question, calls) if use_tool else None
    if ambiguous or amount is not None:
        text = ("Which specific item do you mean? Choices include " + ", ".join(ambiguous["options"][:5])
                + ". Please give its full name or Minecraft item ID. [tool]") if ambiguous else f"{amount} [tool]"
        return {"answer": text, "answer_mode": "clarification" if ambiguous else "calculator_exact",
                "tool_calls": calls, "passages": "", "sources": []}
    if calls and calls[0].get("via") == "deterministic":
        result = calls[0]["result"]
        return {"answer": result.get("answer", result.get("error", "I do not know.")) + " [tool]",
                "answer_mode": "calculator_recipe" if "answer" in result else "calculator_error",
                "tool_calls": calls, "passages": "", "sources": []}
    ids = retriever.search(question, variant, k) if retriever else []
    passages = "\n\n".join(f"[{n}] {retriever.chunks[i]['text']}" for n, i in enumerate(ids, 1)) or "(none)"
    tools = "\n".join(json.dumps(c["result"], ensure_ascii=False) for c in calls) or "(no tool was called)"
    if retriever:
        system = SYSTEM_TOOL if use_tool else SYSTEM
        user = f"Passages:\n{passages}\n\n" + (f"Craft tool results:\n{tools}\n\n" if use_tool else "")
    else:
        system = CLOSED_BOOK_TOOL if use_tool else CLOSED_BOOK
        user = f"Craft tool results:\n{tools}\n\n" if use_tool else ""
    prompt = user + f"Question: {question}" if user else question  # closed book, no tool: the bare question
    answer_mode = "llm"
    msg = chat([{"role": "system", "content": system}, {"role": "user", "content": prompt}])
    text = msg.get("content", "").strip()
    summaries = [c["result"]["answer"] for c in calls if "answer" in c["result"]]
    if summaries and re.fullmatch(r"\s*I (?:do not|don't) know[.!]?\s*", text, re.I):
        # Present the validated full recipe when generation refuses despite a successful calculator result.
        text = " ".join(summary + " [tool]" for summary in summaries)
        answer_mode = "calculator_fallback"
    return {"answer": text, "answer_mode": answer_mode, "tool_calls": calls, "passages": passages if ids else "",
            "sources": [{"n": n, "title": retriever.chunks[i]["title"], "section": retriever.chunks[i]["section"],
                         "chunk_id": i, "source_scope": "current-Java heuristic passage view",
                         "passage_filtered": retriever.chunks[i].get("text_filtered", False),
                         **source_metadata().get(retriever.chunks[i]["title"], {})}
                        for n, i in enumerate(ids, 1)]}


@lru_cache(maxsize=1)
def source_metadata():
    """Citation links point at the stored revision, not today's changing Wiki page."""
    return {p["title"]: {"revid": p["revid"], "timestamp": p["timestamp"],
                         "url": f"https://minecraft.wiki/?oldid={p['revid']}"}
            for p in load_pages()} if (DATA / "pages.jsonl").exists() else {}


if __name__ == "__main__":
    if sys.argv[1:2] == ["fetch"]:
        fetch(int(sys.argv[2]) if len(sys.argv) > 2 else 400)
    elif sys.argv[1:2] == ["index"]:
        build_index(int(sys.argv[2]) if len(sys.argv) > 2 else 256)
    elif sys.argv[1:2] == ["sources"]:
        inventory()
    else:
        print(__doc__)
