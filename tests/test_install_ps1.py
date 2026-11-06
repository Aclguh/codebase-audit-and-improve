#!/usr/bin/env python3
"""
Integration tests for install.ps1 argument validation, workspace installation,
and user-configuration safety.

The installer resolves the user profile from USERPROFILE, so every test runs
against an isolated temporary profile and never touches the real home directory.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALL_PS1 = REPO_ROOT / "install.ps1"
POWERSHELL = (
    shutil.which("pwsh") or shutil.which("powershell") or shutil.which("powershell.exe")
)


@unittest.skipUnless(os.name == "nt" and POWERSHELL, "install.ps1 requires Windows PowerShell")
class TestInstallPs1(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.home_dir = os.path.join(self.test_dir, "home")
        self.work_dir = os.path.join(self.test_dir, "work")
        os.makedirs(self.home_dir)
        os.makedirs(self.work_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def run_install(self, *args, user_profile=None):
        env = os.environ.copy()
        env["USERPROFILE"] = user_profile if user_profile is not None else self.home_dir
        env["PYTHONIOENCODING"] = "utf-8"
        return subprocess.run(
            [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(INSTALL_PS1), *args],
            cwd=self.work_dir,
            env=env,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )

    def combined_output(self, result):
        return f"{result.stdout}\n{result.stderr}"

    def test_help_exits_zero(self):
        result = self.run_install("-Help")
        self.assertEqual(result.returncode, 0, self.combined_output(result))
        self.assertIn("Usage: .\\install.ps1", result.stdout)

    def test_invalid_target_is_rejected(self):
        result = self.run_install("-Target", "NotATarget")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("NotATarget", self.combined_output(result))
        self.assertFalse(os.path.exists(os.path.join(self.work_dir, ".claude")))

    def test_workspace_install_copies_skill_files(self):
        result = self.run_install("-Target", "Claude", "-Workspace")
        self.assertEqual(result.returncode, 0, self.combined_output(result))

        for skill_name in ("improve", "improve-all"):
            skill_dir = os.path.join(self.work_dir, ".claude", "skills", skill_name)
            self.assertTrue(os.path.isfile(os.path.join(skill_dir, "SKILL.md")))
            self.assertTrue(os.path.isfile(os.path.join(skill_dir, "scripts", "check_health.py")))
            self.assertTrue(os.path.isfile(os.path.join(skill_dir, "references", "audit-dimensions.md")))

    def test_global_install_uses_isolated_user_profile(self):
        result = self.run_install("-Target", "Claude")
        self.assertEqual(result.returncode, 0, self.combined_output(result))
        self.assertTrue(os.path.isfile(os.path.join(self.home_dir, ".claude", "skills", "improve", "SKILL.md")))

    def test_continue_install_preserves_unparseable_config(self):
        config_dir = os.path.join(self.work_dir, ".continue")
        os.makedirs(config_dir)
        config_file = os.path.join(config_dir, "config.json")
        # An existing configuration we cannot parse (hand-edited, partially
        # written, or JSONC the installed PowerShell rejects) must be left
        # untouched instead of being overwritten by the template.
        original = '{\n  "models": [\n}\n'
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(original)

        result = self.run_install("-Target", "Continue", "-Workspace")
        self.assertEqual(result.returncode, 0, self.combined_output(result))
        self.assertIn("could not be parsed", self.combined_output(result))
        with open(config_file, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), original)

    def test_global_install_rejects_filesystem_root(self):
        drive_root = os.environ.get("SystemDrive", "C:") + os.sep
        result = self.run_install("-Target", "Claude", user_profile=drive_root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing to install into a filesystem root", self.combined_output(result))


if __name__ == "__main__":
    unittest.main()
