"""Live demo.   python demo.py                            ask questions until you enter an empty line
                python demo.py "how do I make a hopper?"   one question
Needs Ollama installed with the cached model and the index built (see README.md).
Starts the installed local service if needed."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

try:
    import mcqa
except ImportError as e:
    print(f"Project packages are missing: {e}. Install requirements.txt as described in README.md.", file=sys.stderr)
    sys.exit(1)


def ensure_ollama():
    """Use the installed local service; start it if needed, without downloading a model."""
    url = mcqa.OLLAMA.rsplit("/", 1)[0] + "/tags"

    def models():
        with urllib.request.urlopen(url, timeout=3) as response:
            return json.load(response)["models"]

    try:
        available = models()
    except urllib.error.HTTPError:
        raise
    except urllib.error.URLError:
        executable = shutil.which("ollama")
        if not executable:
            raise RuntimeError("Start the Ollama app, then launch the demo again.")
        print("Starting the installed local Ollama service...", flush=True)
        subprocess.Popen([executable, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        deadline = time.monotonic() + 15
        while True:
            try:
                available = models()
                break
            except (urllib.error.URLError, TimeoutError):
                if time.monotonic() >= deadline:
                    raise RuntimeError("Ollama did not start. Open the Ollama app and try again.")
                time.sleep(0.5)
    if not any(model.get("name") == mcqa.LLM for model in available):
        raise RuntimeError(f"The local model is missing. Run: ollama pull {mcqa.LLM}")


def warmup(retriever, variant):
    """Load existing cached models before the first interactive question."""
    started = time.perf_counter()
    print("Preparing local models for the demo. First startup may take a little while...", flush=True)
    retriever.search("What food is used to breed cows?", variant, 1)
    mcqa.chat([{"role": "user", "content": "Reply OK."}], num_predict=1)
    print(f"Ready ({time.perf_counter() - started:.1f} seconds to prepare).\n", flush=True)


def show(question, retriever, use_tool=True, variant="rerank"):
    started = time.perf_counter()
    print("Working...", flush=True)
    res = mcqa.answer(question, retriever, variant=variant, use_tool=use_tool)
    for s in res["sources"]:
        print(f"  [{s['n']}] {s['title']} > {s['section'] or '(intro)'}")
        if s.get("url"):
            print(f"      {s['url']}")
    for c in res["tool_calls"]:
        result = c["result"].get("answer") or c["result"].get("error")
        print(f"  tool: craft({c['args']}) -> {result}")
    print("\n" + res["answer"] + "\n")
    print(f"Finished in {time.perf_counter() - started:.1f} seconds.\n", flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # wiki text has symbols a legacy console can't print
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="*", help="omit for an interactive session")
    parser.add_argument("--no-tool", action="store_true", help="faster gameplay Q&A; disables crafting calculator planning")
    parser.add_argument("--warmup", action="store_true", help="prepare cached models before asking questions")
    parser.add_argument("--variant", choices=("dense", "bm25", "hybrid", "rerank"), default="rerank",
                        help="retrieval method (default: rerank)")
    args = parser.parse_args()
    try:
        # Local-only operation: a missing cache should produce a setup error, never an unexpected download.
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        print("Loading saved index...", flush=True)
        r = mcqa.Retriever(mcqa.DEFAULT_SIZE)
        ensure_ollama()
        if args.no_tool:
            print("Gameplay mode: crafting calculator is disabled.", flush=True)
        if args.warmup:
            warmup(r, args.variant)
        if args.question:
            show(" ".join(args.question), r, use_tool=not args.no_tool, variant=args.variant)
        else:
            print(f"Minecraft Java {mcqa.MC_VERSION} assistant. Enter an empty line to finish.")
            if not args.no_tool:
                print("Try: How many iron ingots do I need to craft 3 hoppers?")
            print("Try: What food is used to breed cows?\n")
            while q := input("Ask> ").strip():
                show(q, r, use_tool=not args.no_tool, variant=args.variant)
    except FileNotFoundError as e:
        print(f"Missing project data: {e.filename}. Follow README.md's fetch/index steps.", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Local model service unavailable: {e.reason}. Start Ollama and run scripts/preflight.py.", file=sys.stderr)
        sys.exit(1)
    except ImportError as e:
        print(f"Project packages are missing: {e}. Install requirements.txt as described in README.md.", file=sys.stderr)
        sys.exit(1)
    except (RuntimeError, OSError, ValueError) as e:
        print(f"Demo could not start: {e}. See README.md for setup.", file=sys.stderr)
        sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print("\nFinished.")
