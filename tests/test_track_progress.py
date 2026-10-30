#!/usr/bin/env python3
"""
Unit tests for scripts/track_progress.py
"""

import os
import sys
import tempfile
import shutil
import unittest

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
        self.assertTrue(track_progress.is_status_done("已完成"))
        self.assertFalse(track_progress.is_status_done("[ ]"))
        self.assertFalse(track_progress.is_status_done("待处理"))

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
        # Table where Status is column 1, and Priority is column 3
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

    def test_checklist_parsing(self):
        content = """# Checklist
- [x] OPT-01: Fix bug
- [ ] [P0] OPT-02: Fix crash
- [ ] OPT-03: Add docs
"""
        filepath = os.path.join(self.test_dir, "IMPROVEMENTS.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 3)
        self.assertTrue(tasks[0]["done"])
        self.assertFalse(tasks[1]["done"])
        self.assertEqual(tasks[1]["priority"], "P0")

if __name__ == "__main__":
    unittest.main()
