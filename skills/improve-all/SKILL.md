---
name: improve-all
description: >-
  Executes the complete, end-to-end codebase audit, atomic implementation, test verification,
  git commit loop, remote push, and CI monitoring in a single autonomous pipeline.
  Triggered by the /improve-all slash command.
---

# Full-Loop Codebase Audit and Improvement (`/improve-all`)

This skill executes the entire **Codebase Audit & Improvement Workflow** end-to-end without requiring intermediate manual steps. It connects pre-flight cleanliness checks, baseline discovery, six-dimensional health audit, temporary roadmap generation, atomic implementation with Conventional Commits, document lifecycle management (archiving or cleanup), branch protection guard, remote push/PR, and GitHub Actions CI verification.

---

## Autonomous Execution Pipeline

When invoked via `/improve-all` (or when the user requests a full audit-and-fix pass):

Proceed autonomously through all 5 phases sequentially:

### Phase 1: Pre-flight Verification & Baseline Discovery
1. Check `git status --porcelain` to ensure a clean working tree.
2. Inspect project tech stack, package manifests, linters, and test runners using `python scripts/check_health.py --json`.
3. Execute existing linters and test suites to record baseline warning counts and coverage.
4. Verify that `IMPROVEMENTS.md` is present in `.gitignore`. If missing, run `python scripts/check_health.py --fix-gitignore`.

### Phase 2: Six-Dimensional Deep Audit
Conduct an exhaustive audit using [references/audit-dimensions.md](./references/audit-dimensions.md) across:
1. **Architecture & Modularity**: Detect god classes/components, layer-skipping, and Monorepo boundaries.
2. **Code Quality & Robustness**: Enforce incremental zero-tolerance (0 errors, 0 new warnings), strict typing, and defensive exception handling.
3. **Performance & Responsiveness**: Mitigate main-thread blocking I/O, unnecessary full rerenders, and streaming/memory overhead.
4. **Maintainability & Engineering Practices**: Ensure localization coverage, update deprecated dependencies, and enforce logging standards.
5. **Security & Sandbox Defense**: Defend against path traversal, command injection, and Zip Slip vulnerabilities.
6. **Testing & Quality Assurance**: Eliminate coverage blind spots in critical logic, add regression assertions, and ensure CI friendliness.

*(Tip: In large codebases with >50 files, invoke `research` subagents to audit modules in parallel.)*

### Phase 3: Generate Structured `IMPROVEMENTS.md`
Generate `IMPROVEMENTS.md` at project root using the standard format in [references/improvements-template.md](./references/improvements-template.md):
- Header marking the document as temporary and git-ignored.
- Quantitative scorecard table and baseline metrics.
- Prioritized issue checklist with unique IDs (`OPT-01`, `OPT-02`...) categorized by severity (P0 Blocker -> P3 Polish).

### Phase 4: Autonomous Atomic Implementation Loop
Immediately begin executing each task in priority order (P0 -> P1 -> P2 -> P3) following [references/execution-loop.md](./references/execution-loop.md):
For each task:
1. Implement minimal, focused code changes (preserve existing comments and formatting).
2. Run static analysis: enforce **Incremental Zero-Tolerance** (0 errors, 0 new warnings, total <= baseline).
3. Run tiered test suites: run targeted unit & regression tests (must achieve 100% pass rate).
4. Update task checkbox in `IMPROVEMENTS.md` from `[ ]` to `[x]`.
5. Execute an atomic Git commit adhering to Conventional Commits: `<type>(<scope>): <concise description>`.
Never bundle multiple tasks into a single commit.

### Phase 5: Verification, Document Lifecycle, PR & CI Monitoring
Once all tasks are marked complete via `python scripts/track_progress.py --check`:
1. Run final full test suite and linters to verify total project health across all modules.
2. Handle document lifecycle:
   - Archive to `docs/audits/YYYY-MM-DD-codebase-improvements.md` (or delete if clean mode was explicitly requested).
3. Branch protection & Git remote:
   - Check if current branch is protected (`main`, `master`, `release`).
   - If on a protected branch: create a feature branch (`git checkout -b refactor/audit-improvements-$(date +%Y%m%d)`), push, and open PR with `gh pr create`.
   - If on a feature branch: push directly with `git push origin <branch>`.
4. Monitor remote GitHub Actions CI status using [references/ci-monitoring.md](./references/ci-monitoring.md) (`gh run watch` or `gh pr checks --watch`).
   - If CI fails, inspect failure logs, apply targeted fixes, and commit/push until green.
5. Signal completion: output `<!-- GOAL_COMPLETE -->` and summarize all implemented improvements and CI verification status.

---

## Quick Reference Scripts

- **Project Health Inspector & Baseline Tool**: `python scripts/check_health.py --json`
- **Progress Tracker & CI Validator**: `python scripts/track_progress.py --check`
