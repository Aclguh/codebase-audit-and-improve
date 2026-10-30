---
description: Executes the complete, end-to-end codebase audit, atomic implementation, test verification, git commit loop, remote push, and CI monitoring in a single autonomous pipeline.
---

Execute the full-loop codebase audit and improvement pipeline (/improve-all):
1. Pre-flight verification & baseline discovery (`python scripts/check_health.py --json`).
2. Six-dimensional deep audit across architecture, code quality, performance, maintainability, security, and test coverage.
3. Generate structured `IMPROVEMENTS.md`.
4. Autonomous atomic implementation loop following `references/execution-loop.md` (incremental zero-tolerance gate: 0 errors, 0 new warnings, tiered unit tests pass, individual Conventional Commits).
5. Global regression & CI: Run full regression test suite, archive `IMPROVEMENTS.md` to `docs/audits/`, check branch protection, push to remote (open PR if protected branch), and monitor GitHub Actions CI to green.
