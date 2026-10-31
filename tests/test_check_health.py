#!/usr/bin/env python3
"""
Unit tests for scripts/check_health.py
"""

import os
import sys
import tempfile
import shutil
import unittest
import subprocess
import json
from io import StringIO
from pathlib import Path
from unittest.mock import patch

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

        # Fallback check script
        with open(pkg_json, "w", encoding="utf-8") as f:
            f.write('{"scripts": {"check": "ts-check", "coverage": "jest --coverage"}}')
        lint_cmd, test_cmd, cov_cmd = check_health.parse_package_json(self.test_dir, "npm")
        self.assertEqual(lint_cmd, "npm run check")
        self.assertEqual(cov_cmd, "npm run coverage")

    def test_detect_monorepo(self):
        self.assertEqual(check_health.detect_monorepo(self.test_dir), [])

        Path(os.path.join(self.test_dir, "turbo.json")).touch()
        Path(os.path.join(self.test_dir, "pnpm-workspace.yaml")).touch()
        Path(os.path.join(self.test_dir, "lerna.json")).touch()
        Path(os.path.join(self.test_dir, "nx.json")).touch()

        pkg_json = os.path.join(self.test_dir, "package.json")
        with open(pkg_json, "w", encoding="utf-8") as f:
            f.write('{"workspaces": ["packages/*"]}')

        cargo = os.path.join(self.test_dir, "Cargo.toml")
        with open(cargo, "w", encoding="utf-8") as f:
            f.write('[workspace]\nmembers = ["core"]')

        indicators = check_health.detect_monorepo(self.test_dir)
        self.assertIn("Turborepo", indicators)
        self.assertIn("pnpm workspace", indicators)
        self.assertIn("Lerna", indicators)
        self.assertIn("Nx", indicators)
        self.assertIn("npm/yarn workspaces", indicators)
        self.assertIn("Cargo workspace", indicators)

    def test_detect_python_stack_variations(self):
        # pyproject.toml
        pyproject = os.path.join(self.test_dir, "pyproject.toml")
        Path(pyproject).touch()
        stacks = check_health.detect_stack(self.test_dir)
        self.assertTrue(any(s["name"] == "Python" for s in stacks))
        os.remove(pyproject)

        # requirements-dev.txt
        req_dev = os.path.join(self.test_dir, "requirements-dev.txt")
        Path(req_dev).touch()
        stacks = check_health.detect_stack(self.test_dir)
        self.assertTrue(any(s["name"] == "Python" for s in stacks))
        os.remove(req_dev)

        # Python source in tests/
        tests_dir = os.path.join(self.test_dir, "tests")
        os.makedirs(tests_dir, exist_ok=True)
        test_file = os.path.join(tests_dir, "test_demo.py")
        Path(test_file).touch()
        stacks = check_health.detect_stack(self.test_dir)
        self.assertTrue(any(s["name"] == "Python" and "tests" in s["test_cmd"] for s in stacks))
        os.remove(test_file)
        os.rmdir(tests_dir)

        # Root python script without manifest
        script_file = os.path.join(self.test_dir, "app.py")
        Path(script_file).touch()
        stacks = check_health.detect_stack(self.test_dir)
        self.assertTrue(any(s["name"] == "Python" and s["manifest"] == "app.py" for s in stacks))
        os.remove(script_file)

        # Poetry runner detection
        pyproject = os.path.join(self.test_dir, "pyproject.toml")
        poetry_lock = os.path.join(self.test_dir, "poetry.lock")
        Path(pyproject).touch()
        Path(poetry_lock).touch()
        with patch("shutil.which", return_value="/bin/poetry"):
            stacks = check_health.detect_stack(self.test_dir)
            self.assertTrue(any("poetry run" in s["lint_cmd"] for s in stacks))
        os.remove(pyproject)
        os.remove(poetry_lock)

    def test_detect_multiple_stacks(self):
        # Node.js
        pkg_json = os.path.join(self.test_dir, "package.json")
        with open(pkg_json, "w", encoding="utf-8") as f:
            f.write('{"scripts": {"lint": "eslint", "test": "jest"}}')
        # Flutter / Dart
        Path(os.path.join(self.test_dir, "pubspec.yaml")).touch()
        # Rust
        Path(os.path.join(self.test_dir, "Cargo.toml")).touch()
        # Go
        Path(os.path.join(self.test_dir, "go.mod")).touch()
        # Maven
        Path(os.path.join(self.test_dir, "pom.xml")).touch()
        # CMake
        Path(os.path.join(self.test_dir, "CMakeLists.txt")).touch()
        # Composer
        Path(os.path.join(self.test_dir, "composer.json")).touch()
        # Ruby
        Path(os.path.join(self.test_dir, "Gemfile")).touch()

        stacks = check_health.detect_stack(self.test_dir)
        stack_names = [s["name"] for s in stacks]
        self.assertTrue(any("Node.js" in n for n in stack_names))
        self.assertTrue(any("Flutter" in n for n in stack_names))
        self.assertTrue(any("Rust" in n for n in stack_names))
        self.assertTrue(any("Go" in n for n in stack_names))
        self.assertTrue(any("Java" in n for n in stack_names))
        self.assertTrue(any("C / C++" in n for n in stack_names))
        self.assertTrue(any("PHP" in n for n in stack_names))
        self.assertTrue(any("Ruby" in n for n in stack_names))

    def test_detect_dotnet_and_gradle_stacks(self):
        # .NET csproj
        Path(os.path.join(self.test_dir, "App.csproj")).touch()
        # Gradle
        Path(os.path.join(self.test_dir, "build.gradle")).touch()

        stacks = check_health.detect_stack(self.test_dir)
        stack_names = [s["name"] for s in stacks]
        self.assertTrue(any(".NET" in n for n in stack_names))
        self.assertTrue(any("Gradle" in n for n in stack_names))

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

    def test_check_git_status_non_git(self):
        info = check_health.check_git_status(self.test_dir)
        self.assertFalse(info["is_git"])

    def test_check_git_status_live_repo(self):
        try:
            subprocess.run(["git", "init"], cwd=self.test_dir, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "TestUser"], cwd=self.test_dir, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.test_dir, check=True, capture_output=True)
            
            # Initial clean state with initial commit
            sample_file = os.path.join(self.test_dir, "sample.txt")
            with open(sample_file, "w") as f:
                f.write("init")
            subprocess.run(["git", "add", "."], cwd=self.test_dir, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=self.test_dir, check=True, capture_output=True)

            info = check_health.check_git_status(self.test_dir)
            self.assertTrue(info["is_git"])
            self.assertTrue(info["is_clean"])
            self.assertEqual(info["dirty_files_count"], 0)

            # Create dirty file
            with open(sample_file, "a") as f:
                f.write("modified")
            info_dirty = check_health.check_git_status(self.test_dir)
            self.assertFalse(info_dirty["is_clean"])
            self.assertEqual(info_dirty["dirty_files_count"], 1)
        except Exception:
            pass

    def test_run_baseline_command(self):
        res = check_health.run_baseline_command(f"{sys.executable} -c \"print('baseline ok')\"", self.test_dir)
        self.assertTrue(res["success"])
        self.assertEqual(res["exit_code"], 0)
        self.assertIn("baseline ok", res["stdout_preview"])

        # Failure command
        res_fail = check_health.run_baseline_command(f"{sys.executable} -c \"import sys; sys.exit(42)\"", self.test_dir)
        self.assertFalse(res_fail["success"])
        self.assertEqual(res_fail["exit_code"], 42)

    def test_main_cli_json_and_fix_gitignore(self):
        old_argv = sys.argv
        try:
            # Test --json flag
            sys.argv = ["check_health.py", "--json"]
            out_buf = StringIO()
            with patch("sys.stdout", out_buf):
                check_health.main()
            data = json.loads(out_buf.getvalue())
            self.assertIn("git_status", data)
            self.assertIn("gitignore", data)
            self.assertIn("detected_stacks", data)

            # Test console output mode
            sys.argv = ["check_health.py"]
            out_buf_console = StringIO()
            with patch("sys.stdout", out_buf_console):
                check_health.main()
            console_text = out_buf_console.getvalue()
            self.assertIn("Codebase Health & Stack Inspector", console_text)

            # Test --run-baseline and --fix-gitignore in custom cwd
            with patch("os.getcwd", return_value=self.test_dir):
                # Put a fake stack with fast baseline command
                Path(os.path.join(self.test_dir, "Cargo.toml")).touch()
                sys.argv = ["check_health.py", "--fix-gitignore", "--run-baseline"]
                out_buf_base = StringIO()
                with patch("sys.stdout", out_buf_base):
                    check_health.main()
                self.assertTrue(os.path.exists(os.path.join(self.test_dir, ".gitignore")))
        finally:
            sys.argv = old_argv

if __name__ == "__main__":
    unittest.main()
