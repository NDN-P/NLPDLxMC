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

    def test_startup_read_timeout_retries_within_the_deadline(self):
        for expired in (False, True):
            with self.subTest(expired=expired), \
                    mock.patch.object(demo.urllib.request, "urlopen", side_effect=[
                        urllib.error.URLError("not running"), TimeoutError("starting"), self.response()]), \
                    mock.patch.object(demo.shutil, "which", return_value="ollama.exe"), \
                    mock.patch.object(demo.subprocess, "Popen") as start, \
                    mock.patch.object(demo.time, "sleep"), \
                    mock.patch.object(demo.time, "monotonic", side_effect=[0, 16 if expired else 1]):
                if expired:
                    with self.assertRaisesRegex(RuntimeError, "Ollama did not start"):
                        demo.ensure_ollama()
                else:
                    demo.ensure_ollama()
                start.assert_called_once()


if __name__ == "__main__":
    unittest.main()
