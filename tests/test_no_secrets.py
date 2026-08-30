"""Fail if this repo contains credentials, HA storage, or secret-echoing workflows."""

from __future__ import annotations

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".storage",
}

# Real-looking secrets only — unit-test placeholders like sk-unit-test-token are allowed.
SK_REAL = re.compile(r"sk-[A-Za-z0-9]{20,}")
GH_TOKEN = re.compile(r"ghp_[A-Za-z0-9]{20,}")
OPENAI = re.compile(r"sk-proj-[A-Za-z0-9_-]{10,}")


def iter_text_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, ROOT)
            if name.endswith((".png", ".jpg", ".jpeg", ".avif", ".gif", ".ico", ".woff", ".woff2")):
                continue
            yield rel, path


class SecretScanTests(unittest.TestCase):
    def test_gitignore_covers_ha_secrets(self):
        gitignore = open(os.path.join(ROOT, ".gitignore"), encoding="utf-8").read()
        for needle in (".storage", "secrets.yaml", "*.sk", ".env"):
            self.assertIn(needle, gitignore)

    def test_hacs_json_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(ROOT, "hacs.json")))

    def test_no_ha_storage_or_logs_committed(self):
        forbidden_names = {"secrets.yaml", "home-assistant.log", "core.config_entries"}
        for rel, path in iter_text_files():
            base = os.path.basename(path)
            self.assertNotIn(base, forbidden_names, rel)
            self.assertFalse("/.storage/" in rel.replace("\\", "/"), rel)

    def test_no_real_looking_tokens_in_tree(self):
        hits = []
        for rel, path in iter_text_files():
            try:
                text = open(path, encoding="utf-8").read()
            except UnicodeDecodeError:
                continue
            for match in SK_REAL.finditer(text):
                token = match.group(0)
                if token.startswith("sk-unit-test") or token.startswith("sk-[REDACTED]"):
                    continue
                if "xxxxxxxx" in token or "example" in token.lower():
                    continue
                hits.append(f"{rel}: {token[:12]}...")
            if GH_TOKEN.search(text) or OPENAI.search(text):
                hits.append(rel)
        self.assertEqual(hits, [], "possible secrets in tree")

    def test_no_workflows_that_echo_secrets(self):
        workflows = os.path.join(ROOT, ".github", "workflows")
        if not os.path.isdir(workflows):
            return
        for name in os.listdir(workflows):
            text = open(os.path.join(workflows, name), encoding="utf-8").read()
            self.assertNotIn("echo ${{ secrets", text)
            self.assertNotIn("SIFELY", text.upper())


if __name__ == "__main__":
    unittest.main()
