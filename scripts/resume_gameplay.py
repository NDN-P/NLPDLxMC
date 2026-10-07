"""Resume the interrupted v1 gameplay experiment with its exact saved source and UTF-8 output.

The final tool-only corrections did not change no-tool answers. This launcher nevertheless loads the original
module and verifies the original hashes rather than mixing code configurations in the old experiment.
"""
import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
snapshot = ROOT / "results" / "verified" / "source_v1"


def saved_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, snapshot / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--split", choices=("dev", "test"), default="test")
args = parser.parse_args()
mcqa = saved_module("mcqa", "mcqa.py")
mcqa.DATA = ROOT / "data"
ev = saved_module("eval", "eval.py")
ev.OUT = ROOT / "results"
bench = saved_module("saved_benchmark_eval", "benchmark_eval.py")
bench.ROOT, bench.DATASET = ROOT, ROOT / "data" / "java_benchmark.jsonl"
original_digest = bench.digest
sources = {ROOT / filename: snapshot / filename for filename in ("mcqa.py", "eval.py")}
bench.digest = lambda p: original_digest(sources.get(Path(p).resolve(), p))
# Use the current safe report generator: it preserves human grades and enforces zero credit for factual refusals.
bench.report = lambda split: None
bench.run(args.split)
subprocess.run([sys.executable, str(ROOT / "scripts" / "benchmark_eval.py"), "report", "--split", args.split], check=True)
