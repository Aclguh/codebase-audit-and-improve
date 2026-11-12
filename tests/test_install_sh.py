#!/usr/bin/env python3
"""
Integration tests for install.sh argument validation and workspace installation.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALL_SH = REPO_ROOT / "install.sh"
def resolve_compatible_bash():
    r"""Locate a bash interpreter that can execute posix scripts with local paths.

    On Windows, `shutil.which('bash')` frequently points to WSL bash in
    System32 (e.g. C:\Windows\System32\bash.exe), which fails to resolve
    DOS drive letters (such as D:/...). We therefore search for Git Bash or
    MSYS bash first. If only WSL bash is present on Windows, we return None
    so the integration test safely skips. On non-Windows platforms, we use
    the standard system bash.
    """
    if os.name == "nt":
        prog_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        prog_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        local_app_data = os.environ.get("LocalAppData", "")
        candidates = [
            os.path.join(prog_files, "Git", "bin", "bash.exe"),
            os.path.join(prog_files, "Git", "usr", "bin", "bash.exe"),
            os.path.join(prog_files_x86, "Git", "bin", "bash.exe"),
            os.path.join(prog_files_x86, "Git", "usr", "bin", "bash.exe"),
        ]
        if local_app_data:
            candidates.append(os.path.join(local_app_data, "Programs", "Git", "bin", "bash.exe"))

        for candidate in candidates:
            if os.path.isfile(candidate):
                return candidate

        which_bash = shutil.which("bash")
        if which_bash:
            wb_lower = which_bash.lower()
            if "system32" not in wb_lower and "syswow64" not in wb_lower:
                return which_bash
        return None

    return shutil.which("bash")

BASH = resolve_compatible_bash()


@unittest.skipUnless(BASH, "bash is not available on this platform")
class TestInstallSh(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.env = os.environ.copy()
        # Keep every global install target inside the temporary directory.
        self.env["HOME"] = self.test_dir
        self.env["USERPROFILE"] = self.test_dir
        self.env["PYTHONIOENCODING"] = "utf-8"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def run_install(self, *args):
        return subprocess.run(
            [BASH, INSTALL_SH.as_posix(), *args],
            cwd=self.test_dir,
            env=self.env,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def assert_no_workspace_output(self):
        for name in (".claude", ".agents", ".cursor", ".continue"):
            self.assertFalse(os.path.exists(os.path.join(self.test_dir, name)), name)

    def test_help_exits_zero(self):
        result = self.run_install("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage: ./install.sh", result.stdout)
        self.assertIn("--workspace", result.stdout)

    def test_invalid_target_is_rejected(self):
        result = self.run_install("--workspace", "notatarget")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown target", result.stderr)
        self.assert_no_workspace_output()

    def test_unknown_option_is_rejected(self):
        result = self.run_install("--workspace", "--bogus")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown option", result.stderr)
        self.assert_no_workspace_output()

    def test_missing_target_value_is_rejected(self):
        for args in (["--workspace", "--target"], ["--workspace", "-t"], ["--workspace", "--target="]):
            with self.subTest(args=args):
                result = self.run_install(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("requires a value", result.stderr)
        self.assert_no_workspace_output()

    def test_global_install_rejects_empty_home(self):
        env = self.env.copy()
        env["HOME"] = ""
        env["USERPROFILE"] = ""
        result = subprocess.run(
            [BASH, INSTALL_SH.as_posix(), "claude"],
            cwd=self.test_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertNotEqual(result.returncode, 0)
        # Git Bash may replace an empty HOME with a synthetic path; both the
        # missing-HOME and non-existent-HOME guards are acceptable.
        self.assertRegex(result.stderr, r"HOME (is not set|directory)")
        self.assert_no_workspace_output()

    def test_global_install_rejects_root_home(self):
        env = self.env.copy()
        env["HOME"] = "/"
        result = subprocess.run(
            [BASH, INSTALL_SH.as_posix(), "claude"],
            cwd=self.test_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("root HOME", result.stderr)

    def test_workspace_claude_install_copies_skill_files(self):
        result = self.run_install("--workspace", "claude")
        self.assertEqual(result.returncode, 0, result.stderr)

        for skill_name in ("improve", "improve-all"):
            skill_dir = os.path.join(self.test_dir, ".claude", "skills", skill_name)
            self.assertTrue(os.path.isfile(os.path.join(skill_dir, "SKILL.md")))
            self.assertTrue(os.path.isfile(os.path.join(skill_dir, "scripts", "check_health.py")))
            self.assertTrue(os.path.isfile(os.path.join(skill_dir, "references", "audit-dimensions.md")))

    def test_global_claude_install_uses_home(self):
        result = self.run_install("claude")
        self.assertEqual(result.returncode, 0, result.stderr)

        skill_dir = os.path.join(self.test_dir, ".claude", "skills", "improve")
        self.assertTrue(os.path.isfile(os.path.join(skill_dir, "SKILL.md")))
        self.assertTrue(os.path.isfile(os.path.join(skill_dir, "scripts", "check_health.py")))

    def test_workspace_reinstall_removes_stale_files(self):
        first = self.run_install("--workspace", "claude")
        self.assertEqual(first.returncode, 0, first.stderr)

        skill_dir = os.path.join(self.test_dir, ".claude", "skills", "improve")
        for name in ("STALE.md", ".hidden-stale"):
            Path(os.path.join(skill_dir, name)).write_text("stale", encoding="utf-8")
        Path(os.path.join(skill_dir, "scripts", "stale.pyc")).write_bytes(b"\x00\x00")

        second = self.run_install("--workspace", "claude")
        self.assertEqual(second.returncode, 0, second.stderr)
        for name in ("STALE.md", ".hidden-stale"):
            self.assertFalse(os.path.exists(os.path.join(skill_dir, name)), name)
        self.assertFalse(os.path.exists(os.path.join(skill_dir, "scripts", "stale.pyc")))
        self.assertTrue(os.path.isfile(os.path.join(skill_dir, "SKILL.md")))


class TestBashResolution(unittest.TestCase):
    def test_windows_rejects_system32_wsl_bash(self):
        with patch("os.name", "nt"), \
             patch("os.path.isfile", return_value=False), \
             patch("shutil.which", return_value=r"C:\Windows\System32\bash.exe"):
            self.assertIsNone(resolve_compatible_bash())

    def test_windows_accepts_git_bash_candidate(self):
        with patch("os.name", "nt"), \
             patch("os.path.isfile", side_effect=lambda p: "Git" in str(p)):
            resolved = resolve_compatible_bash()
            self.assertIsNotNone(resolved)
            self.assertIn("Git", resolved)

    def test_posix_uses_shutil_which(self):
        with patch("os.name", "posix"), \
             patch("shutil.which", return_value="/usr/local/bin/bash"):
            self.assertEqual(resolve_compatible_bash(), "/usr/local/bin/bash")


if __name__ == "__main__":
    unittest.main()
