"""Check the local installation before a demo. No downloads or model inference."""
import importlib.metadata
import json
import os
import sys
from pathlib import Path
import urllib.request

os.environ["HF_HUB_OFFLINE"] = "1"
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import mcqa


def check():
    failures = []
    for path in (mcqa.DATA / "pages.jsonl", mcqa.DATA / "crafting.json",
                 mcqa.DATA / f"chunks_{mcqa.DEFAULT_SIZE}.jsonl", mcqa.DATA / f"emb_{mcqa.DEFAULT_SIZE}.npy"):
        if not path.is_file():
            failures.append(f"Missing {path.name}: run the fetch/index commands in README.md")
    from huggingface_hub import snapshot_download
    for model in (mcqa.EMBED_MODEL, mcqa.RERANK_MODEL, "distilroberta-base"):
        try:
            snapshot_download(model, local_files_only=True)
        except Exception:
            failures.append(f"Model cache missing: {model}; complete the initial model download described in README.md")
    try:
        models = json.load(urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5))["models"]
        if not any(m["name"] == mcqa.LLM for m in models):
            failures.append(f"Ollama model missing: run ollama pull {mcqa.LLM}")
    except Exception as e:
        failures.append(f"Ollama is not reachable: start Ollama ({type(e).__name__})")
    versions = {}
    for p in ("sentence-transformers", "torch", "bert-score"):
        try:
            versions[p] = importlib.metadata.version(p)
        except importlib.metadata.PackageNotFoundError:
            versions[p] = None
            failures.append(f"Package missing: {p}; install requirements.txt")
    print(json.dumps({"python": sys.version.split()[0], "packages": versions, "ready": not failures,
                      "problems": failures}, indent=2))
    return not failures


if __name__ == "__main__":
    sys.exit(0 if check() else 1)
