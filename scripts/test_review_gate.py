import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POST_DIR = ROOT / "content" / "posts"


def load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class ReviewGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.quality = load_module("validate_article_quality", "scripts/validate_article_quality.py")
        cls.generator = load_module("generate_blog", "scripts/generate_blog.py")
        cls.phase_path = next(
            path
            for path in POST_DIR.glob("*phase6ak*.json")
            if "rewrite_evidence" not in json.loads(path.read_text(encoding="utf-8-sig"))
        )
        cls.phase_post = json.loads(cls.phase_path.read_text(encoding="utf-8-sig"))

    def test_phase6ak_is_held_without_an_explicit_approval(self):
        self.assertFalse(self.quality.is_approved(self.phase_post))
        self.assertFalse(self.generator.is_publishable(self.phase_post))

    def test_approved_baseline_corpus_passes_while_phase6ak_remains_held(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_article_quality.py"], cwd=ROOT, capture_output=True, text=True
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["posts"], 100)
        self.assertEqual(result["held_posts"], 115)

    def test_failed_single_record_cannot_be_approved_or_mutate_source(self):
        before = self.phase_path.read_bytes()
        completed = subprocess.run(
            [sys.executable, "scripts/requalify_article.py", "--slug", self.phase_post["slug"], "--reviewer", "test-reviewer"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(hashlib.sha256(self.phase_path.read_bytes()).hexdigest(), hashlib.sha256(before).hexdigest())

    def test_human_confirmation_is_required_before_any_approval_attempt(self):
        completed = subprocess.run(
            [sys.executable, "scripts/requalify_article.py", "--slug", self.phase_post["slug"], "--reviewer", "test-reviewer"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--confirm-human-review", completed.stderr)


if __name__ == "__main__":
    unittest.main()
