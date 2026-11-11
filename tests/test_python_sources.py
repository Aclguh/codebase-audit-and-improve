#!/usr/bin/env python3
"""
Repository-wide Python source hygiene tests.

Python 3.12 reports invalid escape sequences as SyntaxWarning, and a future
release turns them into errors. Compiling every source file with warnings
captured keeps that class of regression (and similar parser warnings) out of
the tree even when `compileall -q` and the focused ruff rule set stay silent.
"""

import unittest
import warnings
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestPythonSources(unittest.TestCase):
    def test_sources_compile_without_syntax_warnings(self):
        source_files = [
            path
            for path in sorted(REPO_ROOT.rglob("*.py"))
            if "__pycache__" not in path.parts and ".git" not in path.parts
        ]
        self.assertTrue(source_files, "No Python sources found to compile")
        for path in source_files:
            with self.subTest(path=str(path.relative_to(REPO_ROOT))):
                source = path.read_text(encoding="utf-8")
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    compile(source, str(path), "exec")
                messages = [
                    f"{item.lineno}: {item.message}"
                    for item in caught
                    if issubclass(item.category, SyntaxWarning)
                ]
                self.assertEqual(messages, [], f"{path} emits syntax warnings: {messages}")


if __name__ == "__main__":
    unittest.main()
