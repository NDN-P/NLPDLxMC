"""Live demo.   python demo.py                            ask questions until you enter an empty line
                python demo.py "how do I make a hopper?"   one question
Needs Ollama running and the index built (see README.md)."""
import sys
import urllib.error

import mcqa


def show(question, retriever):
    res = mcqa.answer(question, retriever)
    for s in res["sources"]:
        print(f"  [{s['n']}] {s['title']} > {s['section'] or '(intro)'}")
    for c in res["tool_calls"]:
        result = c["result"].get("answer") or c["result"].get("error")
        print(f"  tool: craft({c['args']}) -> {result}")
    print("\n" + res["answer"] + "\n")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # wiki text has symbols a legacy console can't print
    try:
        r = mcqa.Retriever(mcqa.DEFAULT_SIZE)
        if len(sys.argv) > 1:
            show(" ".join(sys.argv[1:]), r)
        else:
            print("Minecraft Java 26.3 assistant. Enter an empty line to finish.")
            while q := input("Ask> ").strip():
                show(q, r)
    except FileNotFoundError as e:
        print(f"Missing project data: {e.filename}. Follow README.md's fetch/index steps.", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Local model service unavailable: {e.reason}. Start Ollama and run scripts/preflight.py.", file=sys.stderr)
        sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print("\nFinished.")
