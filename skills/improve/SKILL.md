---
name: improve
description: >-
  Systematically audits a project's overall health across code quality, architecture,
  performance, maintainability, security, and test coverage, generating a structured
  IMPROVEMENTS.md tracking document. Then autonomously or interactively implements
  recommendations in an atomic, test-verified, and git-tracked loop until completion.
  Also triggered by the /improve and /improve-all slash commands.
---

# Codebase Audit and Improvement Workflow (`IMPROVEMENTS.md`)

This skill establishes a proven, enterprise-grade engineering workflow for assessing, planning, tracking, and iteratively improving codebases of any tech stack. It bridges high-level architectural health audits with disciplined, atomic test-driven implementations.

---

## Slash Command Entrypoints

### 1. `/improve` (Audit & Planning)

When invoked via the slash command `/improve` (or when asked to assess/audit the codebase):
1. **Pre-flight & Baseline Discovery**: Immediately execute **Phase 1** (working tree cleanliness check, tech stack/monorepo detection, and baseline metrics recording).
2. **Six-Dimensional Health Audit**: Execute **Phase 2** across architecture, code quality, performance, maintainability, security, and test coverage (optionally using `research` subagents for large repos).
3. **Generate Tracking Document**: Output the structured, prioritized `IMPROVEMENTS.md` at the project root (**Phase 3**).
4. **Summary & Next Action**: Present the quantitative scorecards and top-priority checklist (`OPT-01`, `OPT-02`...) to the user, and inform them that they can run `/goal 全部实现` (or `/improve-all`) to begin the atomic implementation loop (**Phase 4**).

### 2. `/improve-all` (Full End-to-End Pipeline)

When invoked via the slash command `/improve-all` (or when asked to fully audit, implement, and verify all improvements):
1. **Autonomous Execution**: Execute all 5 phases sequentially without pausing for manual intervention.
2. **Phases 1-3**: Pre-flight verification, baseline discovery, 6-dimensional audit, and `IMPROVEMENTS.md` roadmap generation.
3. **Phase 4**: Autonomous atomic implementation loop for every task (enforcing incremental zero-tolerance gate: 0 errors, 0 new warnings, tiered tests pass, individual Conventional Commits).
4. **Phase 5**: Full regression test suite, document lifecycle (archive to `docs/audits/` or cleanup), branch protection guard & PR creation, push to remote repository, monitor GitHub CI to green, and output `<!-- GOAL_COMPLETE -->`.

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│               Phase 1: Pre-flight & Baseline Discovery          │
│  - Verify clean working tree (git status --porcelain == 0)      │
│  - Detect tech stack, monorepo, test runners, and linters       │
│  - Run baseline diagnostics and record baseline warning count   │
│  - Ensure IMPROVEMENTS.md is added to .gitignore                │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│             Phase 2: Six-Dimensional Health Audit               │
│  1. Architecture & Modularity       4. Maintainability          │
│  2. Code Quality & Robustness       5. Security & Sandbox       │
│  3. Performance & Responsiveness    6. Testing & Quality Eng.   │
│  (Tip: Delegate to research subagents for repos with >50 files) │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│            Phase 3: Generate Structured IMPROVEMENTS.md         │
│  - Synthesize findings into quantitative scorecards & diagrams  │
│  - Group issues by severity: P0 (Blockers) -> P3 (Hygiene)      │
│  - Create actionable tasks with IDs (OPT-01, OPT-02...)         │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│          Phase 4: Goal-Driven Atomic Implementation Loop        │
│  For each task (OPT-XX):                                        │
│  1. Implement targeted refactoring/fix                          │
│  2. Static analysis: Incremental Zero-Tolerance (0 new warnings)│
│  3. Tiered testing: Run targeted unit & regression tests        │
│  4. Update checkbox in IMPROVEMENTS.md ([ ] -> [x])             │
│  5. Atomic Git Commit (Conventional Commits)                    │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│            Phase 5: Global Regression, PR & CI Verification     │
│  - Run full-repository regression test suite                    │
│  - Document lifecycle: Archive to docs/audits/ or cleanup       │
│  - Check branch protection; create feature branch & PR if main  │
│  - Monitor GitHub CI status (gh run watch / gh pr checks)       │
│  - Output <!-- GOAL_COMPLETE --> when all goals are met         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Step-by-Step Instructions

### Phase 1: Pre-flight Verification & Baseline Discovery

1. **Working Tree Safety Check**:
   - Check `git status --porcelain`.
   - If uncommitted changes exist, pause or stash them to avoid corrupting user in-flight work.
2. **Detect Tech Stack, Monorepo and Tooling**:
   - Run `python scripts/check_health.py --json` or inspect root manifests (`pubspec.yaml`, `package.json`, `Cargo.toml`, `pyproject.toml`, `pom.xml`, `build.gradle`, etc.).
   - Identify existing linter commands and test runners.
3. **Execute Baseline Checks**:
   - Run existing linters to record the baseline warning count (`baseline_warnings`).
   - Run existing unit test suites to record baseline pass rate and coverage.
4. **Protect Repository with `.gitignore`**:
   - Verify if `IMPROVEMENTS.md` is listed in `.gitignore`.
   - If missing, run `python scripts/check_health.py --fix-gitignore` to prevent temporary tracking documents from polluting version control.

---

### Phase 2: Six-Dimensional Deep Audit

Conduct a thorough inspection across the six core dimensions. See [references/audit-dimensions.md](./references/audit-dimensions.md) for full audit criteria and subagent delegation strategies:

1. **Architecture & Modularity**:
   - Identify God classes/widgets (> 800 lines, multiple distinct responsibilities).
   - Check module boundary violations, layer leaking, and Monorepo package isolation.
   - Verify state management consistency.
2. **Code Quality & Robustness**:
   - Review static analysis warnings, dead code, strict null-safety, and type correctness.
   - Ensure explicit error hierarchies and graceful degradation instead of empty catches.
3. **Performance & Responsiveness**:
   - Identify synchronous I/O blocking UI or event loops.
   - Check for unnecessary whole-screen rebuilds or re-renders.
   - Ensure streaming vs batch memory buffering (e.g. SSE for AI/long operations).
4. **Maintainability & Engineering Practices**:
   - Check localization (i18n) vs hardcoded user-facing strings.
   - Audit outdated dependencies and lockfile hygiene.
   - Check unified logging abstraction vs raw print statements.
5. **Security & Sandbox Defense**:
   - Audit path traversal vulnerabilities (e.g. `../../` escaping sandbox paths).
   - Check shell command injection in subprocess spawning.
   - Verify safe extraction of archives (prevent Zip Slip).
6. **Testing & Quality Assurance**:
   - Identify critical business logic with 0% test coverage.
   - Verify edge-case tests for parsers, serializers, and protocol adapters.

*(Tip: In large repositories, invoke `research` subagents to audit different modules in parallel, preserving the primary conversation context.)*

---

### Phase 3: Generating `IMPROVEMENTS.md`

Output a structured markdown file named `IMPROVEMENTS.md` at the project root using the standard format detailed in [references/improvements-template.md](./references/improvements-template.md).

#### Required Document Sections:
1. **Header & Document Nature Callout**:
   - Mark explicitly as a temporary local planning document excluded by `.gitignore`.
2. **Current State Overview (现状综合分析)**:
   - Architecture topology diagram (ASCII or Mermaid).
   - Quantitative scorecard table (Dimension | Rating / Score | Key Findings).
   - Baseline metrics (recorded baseline warnings count, test count, line coverage %).
3. **Problem List & Root Causes (核心问题清单与根因分析)**:
   - Categorized by priority:
     - **P0**: Critical blockers, security vulnerabilities, process hangs, data corruption, memory crashes.
     - **P1**: Core architecture decoupling, major performance bottlenecks, UI responsiveness.
     - **P2**: Maintainability refactors, dependency modernization, i18n, structured error handling.
     - **P3**: Code style polish, secondary test coverage expansion, documentation.
4. **Actionable Solutions & Expected Gains (落地改进方案与预期收益)**:
   - Concrete file paths, proposed structural refactorings, and measurable benefits.
5. **Task Checklist (实施优先级与推进清单)**:
   - Clear markdown checklist table with unique identifiers (`OPT-01`, `OPT-02`, etc.):
     ```markdown
     | 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
     | :---: | :---: | :--- | :--- | :--- | :---: |
     | **P0** | **OPT-01** | ... | ... | `path/to/file` | [ ] |
     | **P1** | **OPT-02** | ... | ... | `path/to/file` | [ ] |
     ```

---

### Phase 4: Goal-Driven Atomic Implementation Loop

When the user triggers implementation (e.g. `/goal 全部实现`, `/improve-all`, or requesting specific tasks):

Follow the strict **Atomic Execution Loop** detailed in [references/execution-loop.md](./references/execution-loop.md):

```
For each task in IMPROVEMENTS.md:
  1. Inspect affected files and design minimal, focused changes.
  2. Implement code changes (preserve existing comments and formatting).
  3. Run static analysis: Enforce Incremental Zero-Tolerance
     - 0 errors
     - 0 new warnings in modified files
     - Total warnings <= baseline warnings
  4. Run tiered tests: Execute targeted unit & regression tests (100% pass).
  5. If adding tests: verify new test assertions actually cover the updated logic.
  6. Edit IMPROVEMENTS.md: mark task as complete (e.g. change [ ] to [x]).
  7. Execute Git commit for this single task using Conventional Commits.
     Format: <type>(<scope>): <concise description>
```

#### Commit Discipline Rules:
- **One task per commit**: Never bundle unrelated tasks together.
- **Incremental Zero-Tolerance**: Never introduce new lint warnings or broken tests.
- **Rollback protocol**: If an implementation reaches an impasse, run `git restore .` before re-designing.

---

### Phase 5: Verification, Document Lifecycle, PR & CI Check

1. **Verify Full Task Completion**:
   - Run `python scripts/track_progress.py --check` to ensure all tasks are marked complete (exit code 0).
   - Run the full project test suite and linters across the entire repository.
2. **Handle Document Lifecycle**:
   - **Archive Mode (Recommended)**: Move `IMPROVEMENTS.md` to `docs/audits/YYYY-MM-DD-codebase-improvements.md` and commit:
     `docs(audit): archive completed improvements roadmap`.
   - **Cleanup Mode**: If specified by user or running `/improve-all` with deletion requested:
     Delete `IMPROVEMENTS.md` and commit:
     `chore: remove completed temporary roadmap IMPROVEMENTS.md`.
3. **Branch Protection & Pull Request Protocol**:
   - Inspect current branch using `python scripts/check_health.py --json`.
   - If on a protected branch (`main` / `master`):
     - Create a feature branch: `git checkout -b refactor/audit-improvements-$(date +%Y%m%d)`.
     - Push feature branch: `git push -u origin <feature-branch>`.
     - Create PR via GitHub CLI: `gh pr create --title "refactor: codebase health audit and improvements"`.
   - If on an existing feature branch, push directly: `git push origin <branch>`.
4. **Monitor CI & Goal Completion**:
   - Inspect GitHub CI workflow status using [references/ci-monitoring.md](./references/ci-monitoring.md):
     ```bash
     gh run list --limit 1
     gh run watch
     ```
   - If running under `/goal` or `/improve-all`, output `<!-- GOAL_COMPLETE -->` when all items are verified and CI is green.

---

## Quick Reference Scripts

- **Project Health Inspector & Baseline Tool**:
  ```bash
  python scripts/check_health.py
  python scripts/check_health.py --json
  python scripts/check_health.py --fix-gitignore
  ```
- **Progress Tracker & CI Validator**:
  ```bash
  python scripts/track_progress.py IMPROVEMENTS.md
  python scripts/track_progress.py --check
  python scripts/track_progress.py --json
  ```
