---
name: improve-all
description: >-
  Executes the complete, end-to-end codebase audit, atomic implementation, test verification,
  git commit loop, remote push, and CI monitoring in a single autonomous pipeline.
  Triggered by the /improve-all slash command.
---

# Full-Loop Codebase Audit and Improvement (`/improve-all`)

This skill executes the entire **Codebase Audit & Improvement Workflow** end-to-end without requiring intermediate manual steps. It connects baseline discovery, six-dimensional health audit, temporary roadmap generation, atomic implementation with Conventional Commits, cleanup, remote git push, and GitHub Actions CI verification.

---

## Autonomous Execution Pipeline

When invoked via `/improve-all` (or when the user requests a full audit-and-fix pass):

Proceed autonomously through all 5 phases sequentially:

### Phase 1: Baseline Discovery & Git Protection
1. Inspect project tech stack, package manifests, linters, and test runners using [scripts/check_health.py](./scripts/check_health.py).
2. Execute existing linters and test suites to record baseline pass rate and coverage.
3. Verify that `IMPROVEMENTS.md` is present in `.gitignore`. If missing, append `IMPROVEMENTS.md` to `.gitignore` to avoid polluting git history.

### Phase 2: Six-Dimensional Deep Audit
Conduct an exhaustive audit using [references/audit-dimensions.md](./references/audit-dimensions.md) across:
1. **Architecture & Modularity**: Detect god classes/components, layer-skipping, and fragmented state management.
2. **Code Quality & Robustness**: Enforce 0 linter warnings, strict typing, and defensive exception handling.
3. **Performance & Responsiveness**: Mitigate main-thread blocking I/O, unnecessary full rerenders, and streaming/memory overhead.
4. **Maintainability & Engineering Practices**: Ensure localization coverage, update deprecated dependencies, and enforce logging standards.
5. **Security & Sandbox Defense**: Defend against path traversal, command injection, and Zip Slip vulnerabilities.
6. **Testing & Quality Assurance**: Eliminate coverage blind spots in critical logic, add regression assertions, and ensure CI friendliness.

### Phase 3: Generate Structured `IMPROVEMENTS.md`
Generate `IMPROVEMENTS.md` at project root using the standard format in [references/improvements-template.md](./references/improvements-template.md):
- Header marking the document as temporary and git-ignored.
- Quantitative scorecard table and baseline metrics.
- Prioritized issue checklist with unique IDs (`OPT-01`, `OPT-02`...) categorized by severity (P0 Blocker -> P3 Polish).

### Phase 4: Autonomous Atomic Implementation Loop
Immediately begin executing each task in priority order (P0 -> P1 -> P2 -> P3) following [references/execution-loop.md](./references/execution-loop.md):
For each task:
1. Implement minimal, focused code changes (preserve existing comments and formatting).
2. Run static analysis (must report 0 errors, 0 warnings).
3. Run test suites (must achieve 100% pass rate, no regressions).
4. Update task checkbox in `IMPROVEMENTS.md` from `[ ]` to `[x]`.
5. Execute an atomic Git commit adhering to Conventional Commits: `<type>(<scope>): <concise description>`.
Never bundle multiple tasks into a single commit.

### Phase 5: Verification, Cleanup & CI Monitoring
Once all tasks are marked complete:
1. Run final full test suite and linters to verify total project health.
2. Clean up temporary tracking document:
   - Delete `IMPROVEMENTS.md`.
   - Commit the deletion: `chore: 移除已全部落地的临时改进建议文档 IMPROVEMENTS.md` (or `chore: remove completed temporary roadmap IMPROVEMENTS.md`).
3. Push all commits to the remote branch: `git push origin <branch>`.
4. Monitor remote GitHub Actions CI status using [references/ci-monitoring.md](./references/ci-monitoring.md) (`gh run list --limit 1` and `gh run watch`).
   - If CI fails, inspect failure logs, apply targeted fixes, and commit/push until green.
5. Signal completion: output `<!-- GOAL_COMPLETE -->` and summarize all implemented improvements and CI verification status.

---

## Quick Reference Scripts

- **Project Health Inspector**: `python scripts/check_health.py`
- **Progress Tracker & Validator**: `python scripts/track_progress.py IMPROVEMENTS.md`
