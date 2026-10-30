---
description: Systematically audits a project's overall health across code quality, architecture, performance, maintainability, security, and test coverage, generating a structured IMPROVEMENTS.md tracking document.
---

Execute codebase health audit and planning workflow (/improve):
1. Run `python scripts/check_health.py --json` to detect stacks, test runners, git status, and baseline warnings.
2. Conduct the 6-dimensional health audit following `references/audit-dimensions.md`.
3. Generate the structured `IMPROVEMENTS.md` tracking document following `references/improvements-template.md`.
4. Present the quantitative scorecards and top-priority checklist (OPT-01, OPT-02...) to the user.
