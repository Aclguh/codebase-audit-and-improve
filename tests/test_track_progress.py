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
        self.assertTrue(track_progress.is_status_done("[v]"))
        self.assertTrue(track_progress.is_status_done("[V]"))
        self.assertTrue(track_progress.is_status_done("[✓]"))
        self.assertTrue(track_progress.is_status_done("[✔]"))
        self.assertTrue(track_progress.is_status_done("[✅]"))
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

        # Status with commit hashes, PRs, and notes
        self.assertTrue(track_progress.is_status_done("Done (commit 01fbd06)"))
        self.assertTrue(track_progress.is_status_done("已完成 (PR #2)"))
        self.assertTrue(track_progress.is_status_done("[x] c027ac2"))
        self.assertTrue(track_progress.is_status_done("Passed (CI matrix)"))
        self.assertTrue(track_progress.is_status_done("Completed via refactor"))
        self.assertTrue(track_progress.is_status_done("closed"))

        self.assertFalse(track_progress.is_status_done("[ ]"))
        self.assertFalse(track_progress.is_status_done("待处理"))
        self.assertFalse(track_progress.is_status_done(""))
        self.assertFalse(track_progress.is_status_done(None))

    def test_progress_status_is_not_done(self):
        for val in [
            "完成 80% of refactor",
            "完成度 50%",
            "通过率 50%",
            "已完成 80%",
            "已解决: 99%",
            "Completed 3/5",
            "Done 0/3",
            "done: 99%",
        ]:
            self.assertFalse(track_progress.is_status_done(val), f"Failed for {val}")

        # A genuine completion description that merely mentions a number stays done.
        for val in [
            "Done 100%",
            "完成 100%",
            "Done (PR #2, 50% faster)",
            "完成 (feat: cache)",
            "Completed",
            "已完成 (PR #2)",
        ]:
            self.assertTrue(track_progress.is_status_done(val), f"Failed for {val}")

    def test_bare_ratio_status(self):
        for val in ["100%", "100 %", "100.0%", "1/1", "5/5"]:
            self.assertTrue(track_progress.is_status_done(val), f"Failed for {val}")
        for val in ["99%", "99.9%", "0%", "0/0", "0/5", "3/5"]:
            self.assertFalse(track_progress.is_status_done(val), f"Failed for {val}")

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

    def test_table_priority_with_chinese_and_qualifiers(self):
        content = """# Roadmap with qualifiers
| 优先级 | 任务标识 | 任务名称 | 核心收益 | 状态 |
| :---: | :---: | :--- | :--- | :---: |
| **P0** (Blocker) | **OPT-01** | Fix Critical Crash | Stability | [x] c027ac2 |
| P0 级 | OPT-02 | Patch Traversal | Security | [x] |
| P1 紧急 | OPT-03 | Async Streaming | Performance | [ ] |
| **P2** | OPT-04 | Refactor Class | Modularity | [ ] |
"""
        filepath = os.path.join(self.test_dir, "IMPROVEMENTS.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 4)
        self.assertEqual(tasks[0]["priority"], "P0")
        self.assertTrue(tasks[0]["done"])
        self.assertEqual(tasks[1]["priority"], "P0")
        self.assertTrue(tasks[1]["done"])
        self.assertEqual(tasks[2]["priority"], "P1")
        self.assertFalse(tasks[2]["done"])
        self.assertEqual(tasks[3]["priority"], "P2")

    def test_skip_non_task_tables_like_scorecards(self):
        content = """# Document
## Scorecard
| 评估维度 | 评级 / 得分 (满分 5.0) | 核心现状与风险分析 |
| :--- | :---: | :--- |
| **架构设计 (Architecture)** | 4.6 / 5.0 | 分层清晰。 |
| **性能与响应度 (Performance)** | 4.8 / 5.0 | 探测 Git 状态无延迟。 |

## Tasks
| 优先级 | 任务标识 | 任务名称 | 状态 |
| :---: | :---: | :--- | :---: |
| P0 | OPT-01 | Real task | [ ] |
"""
        filepath = os.path.join(self.test_dir, "IMPROVEMENTS.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], "OPT-01")

    def test_checklist_parsing_variations(self):
        content = """# Checklist
- [x] OPT-01: Fix bug
- [ ] [P0] OPT-02: Fix crash
- [ ] **[P0]** [OPT-03] Memory leak
- [x] **P1** - **OPT-04** Buffer overflow
- [ ] Fix memory leak without id
* [x] ✅ OPT-05: Unicode star bullet
1. [ ] OPT-06: Numbered task one
2. [x] [P0级] OPT-07: Numbered task two
- [Table of Contents Link](#section)
"""
        filepath = os.path.join(self.test_dir, "IMPROVEMENTS.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 8)
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
        self.assertFalse(tasks[6]["done"])
        self.assertEqual(tasks[6]["id"], "OPT-06")
        self.assertTrue(tasks[7]["done"])
        self.assertEqual(tasks[7]["priority"], "P0")

    def test_file_not_found(self):
        non_existent = os.path.join(self.test_dir, "missing.md")
        tasks, err = track_progress.parse_improvements_file(non_existent)
        self.assertIsNone(tasks)
        self.assertIn("File not found", err)

    def test_unreadable_path_returns_clean_error(self):
        # A directory exists but cannot be read as a roadmap file.
        tasks, err = track_progress.parse_improvements_file(self.test_dir)
        self.assertIsNone(tasks)
        self.assertIn("Unable to read file", err)

        # Permission failures during the read must also be reported, not raised.
        filepath = os.path.join(self.test_dir, "LOCKED.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# Locked\n")
        with patch("builtins.open", side_effect=PermissionError("access denied")):
            tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(tasks)
        self.assertIn("Unable to read file", err)

    def test_unreadable_path_cli_exits_two_without_traceback(self):
        with patch("sys.argv", ["track_progress.py", self.test_dir]):
            out_buf = StringIO()
            with patch("sys.stdout", out_buf), self.assertRaises(SystemExit) as cm:
                track_progress.main()
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("Unable to read file", out_buf.getvalue())

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

    def test_extended_status_done_variations(self):
        self.assertTrue(track_progress.is_status_done("Merged (#3)"))
        self.assertTrue(track_progress.is_status_done("merged"))
        self.assertTrue(track_progress.is_status_done("Complete"))
        self.assertTrue(track_progress.is_status_done("complete"))
        self.assertTrue(track_progress.is_status_done("Success"))
        self.assertTrue(track_progress.is_status_done("success"))
        self.assertTrue(track_progress.is_status_done("已解决"))
        self.assertTrue(track_progress.is_status_done("已解决: 修复偶发崩溃"))
        self.assertTrue(track_progress.is_status_done("已修复 (PR #10)"))
        self.assertTrue(track_progress.is_status_done("已实现"))
        self.assertTrue(track_progress.is_status_done("完成 (feat: cache)"))

    def test_checklist_number_words_not_task_id(self):
        content = """# Checklist with Technical Terms
- [ ] Base64 encoding support
- [ ] OAuth2 token verification
- [ ] Win32 API compatibility
- [ ] IPv6 socket binding
- [x] [OPT-05] Real explicit task
"""
        filepath = os.path.join(self.test_dir, "IMPROVEMENTS.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 5)
        self.assertNotEqual(tasks[0]["id"], "BASE64")
        self.assertEqual(tasks[0]["name"], "Base64 encoding support")
        self.assertNotEqual(tasks[1]["id"], "OAUTH2")
        self.assertEqual(tasks[1]["name"], "OAuth2 token verification")
        self.assertNotEqual(tasks[2]["id"], "WIN32")
        self.assertEqual(tasks[2]["name"], "Win32 API compatibility")
        self.assertNotEqual(tasks[3]["id"], "IPV6")
        self.assertEqual(tasks[3]["name"], "IPv6 socket binding")
        self.assertEqual(tasks[4]["id"], "OPT-05")

    def test_checklist_priority_qualifier_keeps_task_id_and_name(self):
        content = """# Priority Qualifiers
- [ ] [P0级] OPT-07: Numbered task two
- [ ] **P1** - **OPT-08** Buffer overflow
- [ ] P2级 OPT-09: Qualifier without brackets
"""
        filepath = os.path.join(self.test_dir, "QUALIFIERS.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0]["priority"], "P0")
        self.assertEqual(tasks[0]["id"], "OPT-07")
        self.assertEqual(tasks[0]["name"], "Numbered task two")
        self.assertEqual(tasks[1]["priority"], "P1")
        self.assertEqual(tasks[1]["id"], "OPT-08")
        self.assertEqual(tasks[1]["name"], "Buffer overflow")
        self.assertEqual(tasks[2]["priority"], "P2")
        self.assertEqual(tasks[2]["id"], "OPT-09")
        self.assertEqual(tasks[2]["name"], "Qualifier without brackets")

    def test_priority_token_does_not_match_identifier_text(self):
        content = """# Identifier Text
- [ ] Implement P2P networking support
- [ ] Add P0P failover mode
"""
        filepath = os.path.join(self.test_dir, "IDENTIFIERS.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["priority"], "GENERAL")
        self.assertEqual(tasks[0]["name"], "Implement P2P networking support")
        self.assertEqual(tasks[1]["priority"], "GENERAL")
        self.assertEqual(tasks[1]["name"], "Add P0P failover mode")

    def test_reordered_table_headers_with_aliases(self):
        content = """# Header Aliases Table
| Severity | Action | Progress | Impact |
| :---: | :--- | :---: | :--- |
| P1 | Modernize logging system | [x] | Observability |
| P2 | Enhance test coverage | [ ] | Quality |
"""
        filepath = os.path.join(self.test_dir, "IMPROVEMENTS.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["priority"], "P1")
        self.assertEqual(tasks[0]["name"], "Modernize logging system")
        self.assertTrue(tasks[0]["done"])
        self.assertEqual(tasks[1]["priority"], "P2")
        self.assertEqual(tasks[1]["name"], "Enhance test coverage")
        self.assertFalse(tasks[1]["done"])

    def test_clean_cell_preserves_identifier_underscores(self):
        self.assertEqual(track_progress.clean_cell("parse_package_json"), "parse_package_json")
        self.assertEqual(track_progress.clean_cell("OPT_01"), "OPT_01")
        self.assertEqual(track_progress.clean_cell("_OPT-01_"), "OPT-01")
        self.assertEqual(track_progress.clean_cell("~~parse_package_json~~"), "parse_package_json")
        self.assertEqual(track_progress.clean_cell("**P0** (Blocker)"), "P0 (Blocker)")
        self.assertEqual(track_progress.clean_cell("Fix `parse_package_json` helper"), "Fix parse_package_json helper")

    def test_table_task_name_and_id_preserve_underscores(self):
        content = """| Priority | ID | Task Name | Status |
| :---: | :---: | :--- | :---: |
| P1 | OPT_01 | Refactor parse_package_json helper | [ ] |
"""
        filepath = os.path.join(self.test_dir, "UNDERSCORES.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], "OPT_01")
        self.assertEqual(tasks[0]["name"], "Refactor parse_package_json helper")

    def test_clean_cell_strikethrough(self):
        self.assertEqual(track_progress.clean_cell("~~OPT-01~~"), "OPT-01")


    def test_unknown_cli_option_and_extra_files_are_rejected(self):
        import io
        from contextlib import redirect_stderr

        for argv in (["track_progress.py", "--chek"], ["track_progress.py", "a.md", "b.md"]):
            with self.subTest(argv=argv):
                with patch("sys.argv", argv):
                    err = io.StringIO()
                    with redirect_stderr(err), self.assertRaises(SystemExit) as cm:
                        track_progress.main()
                self.assertEqual(cm.exception.code, 2)
                self.assertIn("Error:", err.getvalue())

    def test_track_progress_cli_help(self):
        import io
        from contextlib import redirect_stdout
        for help_flag in ["--help", "-h"]:
            with patch("sys.argv", ["track_progress.py", help_flag]):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    with self.assertRaises(SystemExit) as cm:
                        track_progress.main()
                    self.assertEqual(cm.exception.code, 0)
                output = buf.getvalue()
                self.assertIn("Usage: track-progress", output)
                self.assertIn("--check", output)
                self.assertIn("--json", output)

    def test_extended_status_done_implemented_and_yes(self):
        for val in [
            "implemented", "Implemented", "IMPLEMENTED",
            "yes", "Yes", "YES",
            "true", "True", "TRUE",
            "[y]", "[Y]",
            "[y] In progress with PR",
            "Implemented in v2.0"
        ]:
            self.assertTrue(track_progress.is_status_done(val), f"Failed for {val}")

    def test_table_with_done_header(self):
        content = """# Table with Done header
| ID | Priority | Task | Done |
| :---: | :---: | :--- | :---: |
| OPT-01 | P0 | Fix security bug | [x] |
| OPT-02 | P1 | Add telemetry | [ ] |
| OPT-03 | P2 | Write docs | Yes |
"""
        filepath = os.path.join(self.test_dir, "IMPROVEMENTS.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0]["id"], "OPT-01")
        self.assertTrue(tasks[0]["done"])
        self.assertEqual(tasks[1]["id"], "OPT-02")
        self.assertFalse(tasks[1]["done"])
        self.assertEqual(tasks[2]["id"], "OPT-03")
        self.assertTrue(tasks[2]["done"])

    def test_table_without_status_column_defaults_to_pending(self):
        content = """# Task Table Without Status Column
| Priority | ID | Task Name |
| :---: | :---: | :--- |
| P1 | OPT-10 | Modernize error handling |
| P2 | OPT-11 | Streamline build pipeline |
"""
        filepath = os.path.join(self.test_dir, "IMPROVEMENTS.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["id"], "OPT-10")
        self.assertEqual(tasks[0]["name"], "Modernize error handling")
        self.assertFalse(tasks[0]["done"])
        self.assertEqual(tasks[1]["id"], "OPT-11")
        self.assertEqual(tasks[1]["name"], "Streamline build pipeline")
        self.assertFalse(tasks[1]["done"])

    def test_task_status_header_variants(self):
        variants = [
            """| 优先级 | 任务标识 | 任务名称 | 任务状态 |
| :---: | :---: | :--- | :---: |
| P0 | OPT-01 | Done task | [x] |
| P1 | OPT-02 | Pending task | [ ] |
""",
            """| Priority | ID | Task | Task Status |
| :---: | :---: | :--- | :---: |
| P0 | OPT-01 | Done task | [x] |
| P1 | OPT-02 | Pending task | [ ] |
""",
        ]
        filepath = os.path.join(self.test_dir, "STATUS_HEADERS.md")
        for content in variants:
            with self.subTest(content=content.splitlines()[0]):
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)

                tasks, err = track_progress.parse_improvements_file(filepath)
                self.assertIsNone(err)
                self.assertEqual(len(tasks), 2)
                self.assertEqual(tasks[0]["name"], "Done task")
                self.assertTrue(tasks[0]["done"])
                self.assertEqual(tasks[1]["name"], "Pending task")
                self.assertFalse(tasks[1]["done"])

    def test_fenced_code_blocks_are_ignored(self):
        content = """# Roadmap

```markdown
| 优先级 | 任务标识 | 任务名称 | 状态 |
| :---: | :---: | :--- | :---: |
| P0 | OPT-99 | Example inside fence | [ ] |
- [ ] OPT-98: Checklist inside fence
```

| 优先级 | 任务标识 | 任务名称 | 状态 |
| :---: | :---: | :--- | :---: |
| P0 | OPT-01 | Real task | [ ] |
"""
        filepath = os.path.join(self.test_dir, "FENCED.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], "OPT-01")
        self.assertEqual(tasks[0]["name"], "Real task")

    def test_longer_and_tilde_fences_respect_marker_type(self):
        content = """~~~~markdown
```
| 优先级 | 任务标识 | 任务名称 | 状态 |
| :---: | :---: | :--- | :---: |
| P0 | OPT-99 | Nested example | [ ] |
```
~~~~
"""
        filepath = os.path.join(self.test_dir, "TILDE.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(tasks, [])

    def test_header_id_uses_word_boundary(self):
        columns = track_progress.parse_header_columns(["Valid", "Task", "Status"])
        self.assertNotIn("id", columns)
        self.assertEqual(columns.get("name"), 1)
        self.assertEqual(columns.get("status"), 2)

    def test_id_and_name_table_without_status(self):
        content = """| ID | Task |
| :---: | :--- |
| OPT-01 | Fix startup crash |
"""
        filepath = os.path.join(self.test_dir, "COMPACT.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], "OPT-01")
        self.assertEqual(tasks[0]["name"], "Fix startup crash")
        self.assertEqual(tasks[0]["priority"], "P2")
        self.assertFalse(tasks[0]["done"])

    def test_ordered_checklist_with_parenthesis_marker(self):
        # "1)" is a valid CommonMark ordered-list marker and must not make the
        # whole roadmap parse as zero tasks.
        content = """# Ordered Roadmap
1) [ ] OPT-01: First task
2) [x] OPT-02: Second task
3) [ ] Third task
"""
        filepath = os.path.join(self.test_dir, "ORDERED_PAREN.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0]["id"], "OPT-01")
        self.assertEqual(tasks[0]["name"], "First task")
        self.assertFalse(tasks[0]["done"])
        self.assertEqual(tasks[1]["id"], "OPT-02")
        self.assertTrue(tasks[1]["done"])
        self.assertEqual(tasks[2]["name"], "Third task")
        self.assertFalse(tasks[2]["done"])

    def test_compact_table_without_name_column_uses_task_id(self):
        # A recognized task table need not carry a name column. Its status cell
        # must never leak into the reported task name.
        content = """| Priority | ID | Status |
| :---: | :---: | :---: |
| P1 | OPT-01 | [ ] |
"""
        filepath = os.path.join(self.test_dir, "COMPACT_NO_NAME.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], "OPT-01")
        self.assertEqual(tasks[0]["name"], "OPT-01")
        self.assertEqual(tasks[0]["priority"], "P1")
        self.assertFalse(tasks[0]["done"])

    def test_name_falls_back_to_first_unmapped_column(self):
        # The long header is not recognized as a name column; the first column
        # that is not mapped to another field must supply the task name.
        content = """| Priority | ID | Detailed implementation task description | Status |
| :---: | :---: | :--- | :---: |
| P1 | OPT-02 | Refactor parser internals | [x] |
"""
        filepath = os.path.join(self.test_dir, "LONG_NAME_HEADER.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], "OPT-02")
        self.assertEqual(tasks[0]["name"], "Refactor parser internals")
        self.assertTrue(tasks[0]["done"])

    def test_check_json_gate_reports_pending_and_exits_one(self):
        pending_file = os.path.join(self.test_dir, "PENDING.md")
        with open(pending_file, "w", encoding="utf-8") as f:
            f.write("| 优先级 | 任务标识 | 任务名称 | 状态 |\n| :---: | :---: | :--- | :---: |\n| P0 | OPT-01 | Test | [ ] |\n")

        with patch("sys.argv", ["track_progress.py", pending_file, "--json", "--check"]):
            out_buf = StringIO()
            with patch("sys.stdout", out_buf), self.assertRaises(SystemExit) as cm:
                track_progress.main()

        self.assertEqual(cm.exception.code, 1)
        data = json.loads(out_buf.getvalue())
        self.assertEqual(data["pending"], 1)
        self.assertFalse(data["is_all_completed"])

    def test_quiet_suppresses_report_but_keeps_gate_exit(self):
        pending_file = os.path.join(self.test_dir, "PENDING.md")
        with open(pending_file, "w", encoding="utf-8") as f:
            f.write("| 优先级 | 任务标识 | 任务名称 | 状态 |\n| :---: | :---: | :--- | :---: |\n| P0 | OPT-01 | Test | [ ] |\n")

        with patch("sys.argv", ["track_progress.py", pending_file, "--quiet", "--check"]):
            out_buf = StringIO()
            with patch("sys.stdout", out_buf), self.assertRaises(SystemExit) as cm:
                track_progress.main()

        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(out_buf.getvalue(), "")

    def test_non_task_table_resets_in_table_and_is_ignored(self):
        content = """# Document With Non-Task Table
| 评估维度 | 评级 / 得分 | 核心现状 |
| :--- | :---: | :--- |
| 架构设计 | 5.0 | 良好 |
| 性能指标 | 4.8 | 优秀 |

| 优先级 | 任务标识 | 任务名称 | 状态 |
| :---: | :---: | :--- | :---: |
| P0 | OPT-01 | Real task | [ ] |
"""
        filepath = os.path.join(self.test_dir, "NON_TASK_TABLE.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], "OPT-01")
        self.assertEqual(tasks[0]["name"], "Real task")

    def test_table_cells_with_escaped_pipes_keep_column_alignment(self):
        content = (
            "| 优先级 | 任务标识 | 任务名称 | 状态 |\n"
            "| :---: | :---: | :--- | :---: |\n"
            "| **P1** | **OPT-01** | 支持 `a \\| b` 解析 | [x] |\n"
            "| **P2** | **OPT-02** | 未完成任务 | [ ] |\n"
        )
        path = os.path.join(self.test_dir, "IMPROVEMENTS.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(path)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["id"], "OPT-01")
        self.assertEqual(tasks[0]["name"], "支持 a | b 解析")
        self.assertTrue(tasks[0]["done"])
        self.assertEqual(tasks[1]["id"], "OPT-02")
        self.assertFalse(tasks[1]["done"])

    def test_table_rows_without_trailing_pipes_are_parsed(self):
        content = """# Pipe-Optional Table
| 优先级 | 任务标识 | 任务名称 | 状态
| :---: | :---: | :--- | :---:
| P0 | OPT-01 | Fix crash | [x]
| P1 | OPT-02 | Add tests | [ ]
"""
        filepath = os.path.join(self.test_dir, "PIPE_OPTIONAL.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["id"], "OPT-01")
        self.assertTrue(tasks[0]["done"])
        self.assertEqual(tasks[1]["id"], "OPT-02")
        self.assertFalse(tasks[1]["done"])

    def test_single_cell_pipe_line_does_not_create_task(self):
        content = """| 优先级 | 任务标识 | 任务名称 | 状态 |
| :---: | :---: | :--- | :---: |
| P0 | OPT-01 | Real task | [ ] |
| stray line without cells
"""
        filepath = os.path.join(self.test_dir, "STRAY_PIPE.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        tasks, err = track_progress.parse_improvements_file(filepath)
        self.assertIsNone(err)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], "OPT-01")

    def test_clean_cell_markdown_stripping_and_preservation(self):
        self.assertEqual(track_progress.clean_cell(""), "")
        self.assertEqual(track_progress.clean_cell(None), "")
        self.assertEqual(track_progress.clean_cell("**bold**"), "bold")
        self.assertEqual(track_progress.clean_cell("`code`"), "code")
        self.assertEqual(track_progress.clean_cell("~~deleted~~"), "deleted")
        self.assertEqual(track_progress.clean_cell("__italic__"), "italic")
        self.assertEqual(track_progress.clean_cell("`parse_package_json`"), "parse_package_json")
        self.assertEqual(track_progress.clean_cell("**OPT_01**"), "OPT_01")
        self.assertEqual(track_progress.clean_cell("`OPT-02`"), "OPT-02")


if __name__ == "__main__":
    unittest.main()
