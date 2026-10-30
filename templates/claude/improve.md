---
description: Systematically audits a project's overall health across code quality, architecture, performance, maintainability, security, and test coverage, generating a structured IMPROVEMENTS.md tracking document.
---

Please execute the codebase health audit and planning workflow (/improve):
1. Pre-flight verification & baseline discovery: Run `python scripts/check_health.py --json` to detect stacks, test runners, git status, and baseline warnings.
2. Six-dimensional health audit: Follow `references/audit-dimensions.md` to inspect architecture, code quality, performance, maintainability, security, and test coverage.
3. Generate tracking document: Create the structured `IMPROVEMENTS.md` tracking document following `references/improvements-template.md`.
4. Summary & Next steps: Present the quantitative scorecards and top-priority checklist (OPT-01, OPT-02...) to the user.
