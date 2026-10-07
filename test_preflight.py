"""Readiness reports should survive incomplete installs and distinguish demo from evaluation."""
import builtins
import importlib.metadata
import io
import json
import unittest
from unittest import mock

from scripts import preflight


class PreflightTests(unittest.TestCase):
    def test_missing_dependency_has_setup_guidance_without_traceback(self):
        original_import = builtins.__import__

        def missing_project(name, *args, **kwargs):
            if name == "mcqa":
                raise ImportError("No module named numpy")
            return original_import(name, *args, **kwargs)

        output = io.StringIO()
        with mock.patch.object(builtins, "__import__", side_effect=missing_project), \
                mock.patch.object(preflight.importlib.metadata, "version", side_effect=importlib.metadata.PackageNotFoundError), \
                mock.patch.object(preflight.sys, "stdout", output):
            self.assertFalse(preflight.check(demo_only=True))
        result = json.loads(output.getvalue())
        self.assertFalse(result["ready"])
        self.assertTrue(any("install requirements.txt" in problem for problem in result["problems"]))

    def test_demo_does_not_require_the_bertscore_model(self):
        output = io.StringIO()
        response = io.BytesIO(json.dumps({"models": [{"name": "qwen3:4b-instruct"}]}).encode())
        with mock.patch("huggingface_hub.snapshot_download", return_value="cached") as cached, \
                mock.patch.object(preflight.importlib.metadata, "version", return_value="installed"), \
                mock.patch.object(preflight.Path, "is_file", return_value=True), \
                mock.patch.object(preflight.urllib.request, "urlopen", return_value=response), \
                mock.patch.object(preflight.sys, "stdout", output):
            self.assertTrue(preflight.check(demo_only=True))
        self.assertNotIn("distilroberta-base", [call.args[0] for call in cached.call_args_list])
        self.assertNotIn("bert-score", json.loads(output.getvalue())["packages"])


if __name__ == "__main__":
    unittest.main()
