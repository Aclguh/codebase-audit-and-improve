#!/usr/bin/env python3
"""
Unit tests for scripts/track_progress.py
"""

import os
import sys
import tempfile
import shutil
import unittest
import json
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import track_progress

class TestTrackProgress(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_clean_cell_and_is_status_done(self):
        self.assertEqual(track_progress.clean_cell("**P0**"), "P0")
        self.assertEqual(track_progress.clean_cell("`OPT-01`"), "OPT-01")

        self.assertTrue(track_progress.is_status_done("[x]"))
        self.assertTrue(track_progress.is_status_done("[X]"))
        self.assertTrue(track_progress.is_status_done("✓"))
        self.assertTrue(track_progress.is_status_done("✔"))
        self.assertTrue(track_progress.is_status_done("✅"))
        self.assertTrue(track_progress.is_status_done("☑"))
        self.assertTrue(track_progress.is_status_done("√"))
        self.assertTrue(track_progress.is_status_done("已完成"))
        self.assertTrue(track_progress.is_status_done("DONE"))
        self.assertTrue(track_progress.is_status_done("pass"))
        self.assertTrue(track_progress.is_status_done("finished"))
        self.assertTrue(track_progress.is_status_done("resolved"))
        self.assertTrue(track_progress.is_status_done("ok"))

        self.assertFalse(track_progress.is_status_done("[ ]"))
        self.assertFalse(track_progress.is_status_done("待处理"))
        self.assertFalse(track_progress.is_status_done(""))
        self.assertFalse(track_progress.is_status_done(None))

    def test_standard_table_parsing(self):
        content = """# Roadmap
| 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P0** | **OPT-01** | Fix Vulnerability | High Security | `sec.py` | [x] |
| **P1** | **OPT-02** | Optimize Cache | Faster I/O | `cache.py` | [ ] |
"""
        filepath = os.path.join(self.test_dir, "IMPROVEMENTS.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["id"], "OPT-01")
        self.assertTrue(tasks[0]["done"])
        self.assertEqual(tasks[1]["id"], "OPT-02")
        self.assertFalse(tasks[1]["done"])

    def test_reordered_table_parsing(self):
        content = """# Reordered Columns
| 状态 | 任务名称 | 优先级 | 任务标识 |
| :---: | :--- | :---: | :---: |
| [x] | Refactor module | P2 | OPT-10 |
| [ ] | Add unit tests | P3 | OPT-11 |
"""
        filepath = os.path.join(self.test_dir, "IMPROVEMENTS.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["id"], "OPT-10")
        self.assertTrue(tasks[0]["done"])
        self.assertEqual(tasks[1]["id"], "OPT-11")
        self.assertFalse(tasks[1]["done"])

    def test_checklist_parsing_variations(self):
        content = """# Checklist
- [x] OPT-01: Fix bug
- [ ] [P0] OPT-02: Fix crash
- [ ] **[P0]** [OPT-03] Memory leak
- [x] **P1** - **OPT-04** Buffer overflow
- [ ] Fix memory leak without id
* [x] ✅ OPT-05: Unicode star bullet
"""
        filepath = os.path.join(self.test_dir, "IMPROVEMENTS.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 6)
        self.assertTrue(tasks[0]["done"])
        self.assertEqual(tasks[0]["id"], "OPT-01")
        self.assertFalse(tasks[1]["done"])
        self.assertEqual(tasks[1]["priority"], "P0")
        self.assertEqual(tasks[2]["id"], "OPT-03")
        self.assertEqual(tasks[2]["priority"], "P0")
        self.assertTrue(tasks[3]["done"])
        self.assertEqual(tasks[3]["id"], "OPT-04")
        self.assertEqual(tasks[3]["priority"], "P1")
        self.assertFalse(tasks[4]["done"])
        self.assertEqual(tasks[4]["name"], "Fix memory leak without id")
        self.assertTrue(tasks[5]["done"])

    def test_file_not_found(self):
        non_existent = os.path.join(self.test_dir, "missing.md")
        tasks, err = track_progress.parse_improvements_file(non_existent)
        self.assertIsNone(tasks)
        self.assertIn("File not found", err)

    def test_main_cli_modes(self):
        # Create completed sample
        filepath = os.path.join(self.test_dir, "DONE.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("| 优先级 | 任务标识 | 任务名称 | 状态 |\n| :---: | :---: | :--- | :---: |\n| P0 | OPT-01 | Test | [x] |\n")

        old_argv = sys.argv
        try:
            # Test JSON mode
            sys.argv = ["track_progress.py", filepath, "--json"]
            out_buf = StringIO()
            with patch("sys.stdout", out_buf):
                with self.assertRaises(SystemExit) as cm:
                    track_progress.main()
                self.assertEqual(cm.exception.code, 0)
            data = json.loads(out_buf.getvalue())
            self.assertEqual(data["percentage"], 100.0)
            self.assertTrue(data["is_all_completed"])

            # Test console output mode for completed tasks
            sys.argv = ["track_progress.py", filepath]
            out_buf_done = StringIO()
            with patch("sys.stdout", out_buf_done):
                with self.assertRaises(SystemExit) as cm:
                    track_progress.main()
                self.assertEqual(cm.exception.code, 0)
            self.assertIn("ALL TASKS COMPLETED (100%)", out_buf_done.getvalue())

            # Test missing file console error
            sys.argv = ["track_progress.py", os.path.join(self.test_dir, "nonexistent.md")]
            out_buf_missing = StringIO()
            with patch("sys.stdout", out_buf_missing):
                with self.assertRaises(SystemExit) as cm:
                    track_progress.main()
                self.assertEqual(cm.exception.code, 2)
            self.assertIn("Error: File not found", out_buf_missing.getvalue())

            # Test empty file without tasks
            empty_file = os.path.join(self.test_dir, "EMPTY.md")
            with open(empty_file, "w") as f:
                f.write("# Empty document\nNo tasks here.\n")
            sys.argv = ["track_progress.py", empty_file]
            out_buf_empty = StringIO()
            with patch("sys.stdout", out_buf_empty):
                with self.assertRaises(SystemExit) as cm:
                    track_progress.main()
                self.assertEqual(cm.exception.code, 2)
            self.assertIn("No tracked tasks found", out_buf_empty.getvalue())

            # Test empty file in JSON mode
            sys.argv = ["track_progress.py", empty_file, "--json"]
            out_buf_empty_json = StringIO()
            with patch("sys.stdout", out_buf_empty_json):
                with self.assertRaises(SystemExit) as cm:
                    track_progress.main()
                self.assertEqual(cm.exception.code, 2)
            self.assertIn("No tracked tasks found", out_buf_empty_json.getvalue())

            # Test --check mode passing
            sys.argv = ["track_progress.py", filepath, "--check", "--quiet"]
            with self.assertRaises(SystemExit) as cm:
                track_progress.main()
            self.assertEqual(cm.exception.code, 0)

            # Test --check mode failing with pending task
            pending_file = os.path.join(self.test_dir, "PENDING.md")
            with open(pending_file, "w", encoding="utf-8") as f:
                f.write("| 优先级 | 任务标识 | 任务名称 | 状态 |\n| :---: | :---: | :--- | :---: |\n| P0 | OPT-01 | Test | [ ] |\n")
            sys.argv = ["track_progress.py", pending_file, "--check"]
            with self.assertRaises(SystemExit) as cm:
                track_progress.main()
            self.assertEqual(cm.exception.code, 1)

            # Test missing file error
            sys.argv = ["track_progress.py", os.path.join(self.test_dir, "none.md"), "--json"]
            out_buf_err = StringIO()
            with patch("sys.stdout", out_buf_err):
                with self.assertRaises(SystemExit) as cm:
                    track_progress.main()
                self.assertEqual(cm.exception.code, 2)
        finally:
            sys.argv = old_argv

if __name__ == "__main__":
    unittest.main()
