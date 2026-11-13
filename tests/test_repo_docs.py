#!/usr/bin/env python3
"""
Repository documentation consistency tests.

The repository root SKILL.md is the browsable entry point, while
skills/improve/SKILL.md is the artifact copied by the installers. They must
stay identical so installed skills and repository documentation do not drift.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def read_text(path):
    return path.read_text(encoding="utf-8")


def frontmatter_name(text):
    """Return the `name:` value from a YAML frontmatter block, if present."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    for line in text[4:end].splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    return None


class TestRepoDocs(unittest.TestCase):
    def test_root_skill_matches_bundled_improve_skill(self):
        self.assertEqual(
            read_text(REPO_ROOT / "SKILL.md"),
            read_text(REPO_ROOT / "skills" / "improve" / "SKILL.md"),
            "Root SKILL.md and skills/improve/SKILL.md must stay in sync",
        )

    def test_skill_frontmatter_names(self):
        self.assertEqual(frontmatter_name(read_text(REPO_ROOT / "SKILL.md")), "improve")
        self.assertEqual(
            frontmatter_name(read_text(REPO_ROOT / "skills" / "improve-all" / "SKILL.md")),
            "improve-all",
        )

    def test_linked_reference_files_exist(self):
        # Installers copy references/ next to each SKILL.md, so every relative
        # link must resolve to a file in the repository's references/ directory.
        for skill in ("SKILL.md", "skills/improve-all/SKILL.md"):
            text = read_text(REPO_ROOT / skill)
            links = re.findall(r"\]\((\./references/[^)]+)\)", text)
            self.assertTrue(links, f"{skill} should link to reference documents")
            for link in links:
                target = REPO_ROOT / link[2:]
                self.assertTrue(target.is_file(), f"{skill} links to missing file: {link}")

    def test_docs_list_detected_stacks_and_protected_branches(self):
        # Keep the user-facing capability lists aligned with what
        # scripts/check_health.py actually detects and guards.
        for readme in ("README.md", "README_zh.md"):
            text = read_text(REPO_ROOT / readme)
            self.assertIn("Swift", text, f"{readme} should list Swift stack detection")
            self.assertIn("trunk", text, f"{readme} should list trunk as protected")
        for doc in (
            "SKILL.md",
            "skills/improve/SKILL.md",
            "skills/improve-all/SKILL.md",
            "references/ci-monitoring.md",
        ):
            text = " ".join(read_text(REPO_ROOT / doc).split())
            self.assertIn("trunk", text, f"{doc} should list trunk as protected")

    def test_cleanup_mode_does_not_commit_gitignored_roadmap(self):
        # IMPROVEMENTS.md is excluded by .gitignore, so deleting it leaves no
        # tracked change; the docs must not instruct an empty commit.
        for skill in ("SKILL.md", "skills/improve/SKILL.md"):
            text = " ".join(read_text(REPO_ROOT / skill).split())
            self.assertIn("deletion leaves no tracked change and needs no commit", text)
            self.assertNotIn("chore: remove completed temporary roadmap", text)


if __name__ == "__main__":
    unittest.main()
