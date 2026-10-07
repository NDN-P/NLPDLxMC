"""Check local service startup without actually starting a server or downloading anything."""
import io
import json
import unittest
import urllib.error
from unittest import mock

import demo


class TestDemo(unittest.TestCase):
    def response(self, name=demo.mcqa.LLM):
        return io.BytesIO(json.dumps({"models": [{"name": name}]}).encode())

    def test_existing_service_is_reused(self):
        with mock.patch.object(demo.urllib.request, "urlopen", return_value=self.response()), \
                mock.patch.object(demo.subprocess, "Popen") as start:
            demo.ensure_ollama()
        start.assert_not_called()

    def test_missing_model_does_not_download_or_start_another_server(self):
        with mock.patch.object(demo.urllib.request, "urlopen", return_value=self.response("different-model")), \
                mock.patch.object(demo.subprocess, "Popen") as start:
            with self.assertRaisesRegex(RuntimeError, "local model is missing"):
                demo.ensure_ollama()
        start.assert_not_called()

    def test_unreachable_service_starts_installed_ollama_once(self):
        with mock.patch.object(demo.urllib.request, "urlopen",
                               side_effect=[urllib.error.URLError("not running"), self.response()]), \
                mock.patch.object(demo.shutil, "which", return_value="ollama.exe"), \
                mock.patch.object(demo.subprocess, "Popen") as start:
            demo.ensure_ollama()
        self.assertEqual(start.call_count, 1)
        self.assertEqual(start.call_args.args[0], ["ollama.exe", "serve"])


if __name__ == "__main__":
    unittest.main()
