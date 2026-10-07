"""Live demo.   python demo.py                            ask questions until you enter an empty line
                python demo.py "how do I make a hopper?"   one question
Needs Ollama running and the index built (see README.md)."""
import argparse
import sys
import time
import urllib.error

import mcqa


def show(question, retriever, use_tool=True):
    started = time.perf_counter()
    print("Working...", flush=True)
    res = mcqa.answer(question, retriever, use_tool=use_tool)
    for s in res["sources"]:
        print(f"  [{s['n']}] {s['title']} > {s['section'] or '(intro)'}")
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
    args = parser.parse_args()
    try:
        print("Loading saved index...", flush=True)
        r = mcqa.Retriever(mcqa.DEFAULT_SIZE)
        if args.no_tool:
            print("Gameplay mode: crafting calculator is disabled.", flush=True)
        if args.question:
            show(" ".join(args.question), r, use_tool=not args.no_tool)
        else:
            print("Minecraft Java 26.3 assistant. Enter an empty line to finish.")
            while q := input("Ask> ").strip():
                show(q, r, use_tool=not args.no_tool)
    except FileNotFoundError as e:
        print(f"Missing project data: {e.filename}. Follow README.md's fetch/index steps.", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Local model service unavailable: {e.reason}. Start Ollama and run scripts/preflight.py.", file=sys.stderr)
        sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print("\nFinished.")
