#!/usr/bin/env python3
"""
Unit tests for scripts/check_health.py
"""

import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

# Add scripts directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import check_health

class TestCheckHealth(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_detect_package_manager(self):
        # Default npm
        self.assertEqual(check_health.detect_package_manager(self.test_dir), "npm")

        # pnpm
        Path(os.path.join(self.test_dir, "pnpm-lock.yaml")).touch()
        self.assertEqual(check_health.detect_package_manager(self.test_dir), "pnpm")
        os.remove(os.path.join(self.test_dir, "pnpm-lock.yaml"))

        # yarn
        Path(os.path.join(self.test_dir, "yarn.lock")).touch()
        self.assertEqual(check_health.detect_package_manager(self.test_dir), "yarn")
        os.remove(os.path.join(self.test_dir, "yarn.lock"))

        # bun
        Path(os.path.join(self.test_dir, "bun.lockb")).touch()
        self.assertEqual(check_health.detect_package_manager(self.test_dir), "bun")

    def test_parse_package_json_scripts(self):
        pkg_json = os.path.join(self.test_dir, "package.json")
        with open(pkg_json, "w", encoding="utf-8") as f:
            f.write('{"scripts": {"lint": "eslint src/", "test": "vitest run", "test:coverage": "vitest run --coverage"}}')

        lint_cmd, test_cmd, cov_cmd = check_health.parse_package_json(self.test_dir, "pnpm")
        self.assertEqual(lint_cmd, "pnpm run lint")
        self.assertEqual(test_cmd, "pnpm test")
        self.assertEqual(cov_cmd, "pnpm run test:coverage")

    def test_detect_monorepo(self):
        self.assertEqual(check_health.detect_monorepo(self.test_dir), [])

        Path(os.path.join(self.test_dir, "turbo.json")).touch()
        Path(os.path.join(self.test_dir, "pnpm-workspace.yaml")).touch()
        indicators = check_health.detect_monorepo(self.test_dir)
        self.assertIn("Turborepo", indicators)
        self.assertIn("pnpm workspace", indicators)

    def test_detect_python_stack(self):
        Path(os.path.join(self.test_dir, "pyproject.toml")).touch()
        stacks = check_health.detect_stack(self.test_dir)
        self.assertTrue(any(s["name"] == "Python" for s in stacks))

    def test_detect_rust_stack(self):
        Path(os.path.join(self.test_dir, "Cargo.toml")).touch()
        stacks = check_health.detect_stack(self.test_dir)
        self.assertTrue(any(s["name"] == "Rust" for s in stacks))

    def test_detect_go_stack(self):
        Path(os.path.join(self.test_dir, "go.mod")).touch()
        stacks = check_health.detect_stack(self.test_dir)
        self.assertTrue(any(s["name"] == "Go" for s in stacks))

    def test_check_gitignore(self):
        # Missing
        is_ignored, msg, _ = check_health.check_gitignore(self.test_dir)
        self.assertFalse(is_ignored)

        # Commented only
        gitignore = os.path.join(self.test_dir, ".gitignore")
        with open(gitignore, "w", encoding="utf-8") as f:
            f.write("# IMPROVEMENTS.md\n")
        is_ignored, _, _ = check_health.check_gitignore(self.test_dir)
        self.assertFalse(is_ignored)

        # Negated only
        with open(gitignore, "w", encoding="utf-8") as f:
            f.write("!IMPROVEMENTS.md\n")
        is_ignored, _, _ = check_health.check_gitignore(self.test_dir)
        self.assertFalse(is_ignored)

        # Valid ignore
        check_health.add_to_gitignore(self.test_dir)
        is_ignored, _, _ = check_health.check_gitignore(self.test_dir)
        self.assertTrue(is_ignored)

if __name__ == "__main__":
    unittest.main()
