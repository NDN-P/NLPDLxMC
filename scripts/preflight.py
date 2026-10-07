"""Check the local installation before a demo. No downloads or model inference."""
import argparse
import importlib.metadata
import json
import os
import sys
from pathlib import Path
import urllib.request

os.environ["HF_HUB_OFFLINE"] = "1"
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
def check(demo_only=False):
    failures = []
    versions = {}
    packages = ("numpy", "rank-bm25", "huggingface-hub", "sentence-transformers", "torch")
    for package in packages + (() if demo_only else ("bert-score",)):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
            failures.append(f"Package missing: {package}; install requirements.txt")
    try:
        import mcqa
        from huggingface_hub import snapshot_download
    except ImportError as e:
        failures.append(f"Cannot load project dependencies: {e}; install requirements.txt")
        print(json.dumps({"python": sys.version.split()[0], "packages": versions, "ready": False,
                          "mode": "demo" if demo_only else "evaluation", "problems": failures}, indent=2))
        return False
    for path in (mcqa.DATA / "pages.jsonl", mcqa.DATA / "crafting.json",
                 mcqa.DATA / f"chunks_{mcqa.DEFAULT_SIZE}.jsonl", mcqa.DATA / f"emb_{mcqa.DEFAULT_SIZE}.npy"):
        if not path.is_file():
            failures.append(f"Missing {path.name}: run the fetch/index commands in README.md")
    models_to_check = (mcqa.EMBED_MODEL, mcqa.RERANK_MODEL) + (() if demo_only else ("distilroberta-base",))
    for model in models_to_check:
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
    print(json.dumps({"python": sys.version.split()[0], "packages": versions, "ready": not failures,
                      "mode": "demo" if demo_only else "evaluation", "problems": failures}, indent=2))
    return not failures


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="check demo requirements without evaluation-only models")
    args = parser.parse_args()
    sys.exit(0 if check(args.demo) else 1)
