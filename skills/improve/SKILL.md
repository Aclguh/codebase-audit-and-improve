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
1. **Automated Baseline & Discovery**: Immediately execute **Phase 1** (tech stack detection and `.gitignore` verification).
2. **Six-Dimensional Health Audit**: Execute **Phase 2** across architecture, code quality, performance, maintainability, security, and test coverage.
3. **Generate Tracking Document**: Output the structured, prioritized `IMPROVEMENTS.md` at the project root (**Phase 3**).
4. **Summary & Next Action**: Present the quantitative scorecards and top-priority checklist (`OPT-01`, `OPT-02`...) to the user, and inform them that they can run `/goal 全部实现` (or `/improve-all`) to begin the atomic implementation loop (**Phase 4**).

### 2. `/improve-all` (Full End-to-End Pipeline)

When invoked via the slash command `/improve-all` (or when asked to fully audit, implement, and verify all improvements):
1. **Autonomous Execution**: Execute all 5 phases sequentially without pausing for manual intervention.
2. **Phases 1-3**: Baseline discovery, 6-dimensional audit, and `IMPROVEMENTS.md` generation.
3. **Phase 4**: Autonomous atomic implementation loop for every task (0 lint warnings, 100% tests pass, individual Conventional Commits).
4. **Phase 5**: Final verification, delete `IMPROVEMENTS.md`, push to remote repository, monitor GitHub CI to green, and output `<!-- GOAL_COMPLETE -->`.

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│               Phase 1: Project Baseline Discovery               │
│  - Detect tech stack, test runners, linters, and git status     │
│  - Run baseline diagnostics (linters, test suites, coverage)    │
│  - Ensure IMPROVEMENTS.md is added to .gitignore                │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│             Phase 2: Six-Dimensional Health Audit               │
│  1. Architecture & Modularity       4. Maintainability          │
│  2. Code Quality & Robustness       5. Security & Sandbox       │
│  3. Performance & Responsiveness    6. Testing & Quality Eng.   │
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
│  2. Run automated static analysis (0 errors, 0 warnings)        │
│  3. Run relevant & global test suites (100% pass)               │
│  4. Update checkbox in IMPROVEMENTS.md ([ ] -> [x])             │
│  5. Atomic Git Commit (Conventional Commits)                    │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│            Phase 5: Cleanup & Remote CI Verification            │
│  - Delete temporary IMPROVEMENTS.md (if requested upon 100%)    │
│  - Git push to remote branch                                    │
│  - Monitor GitHub CI status (gh run watch / gh run list)        │
│  - Output <!-- GOAL_COMPLETE --> when all goals are met         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Step-by-Step Instructions

### Phase 1: Baseline Discovery & Git Protection

1. **Detect Tech Stack and Tooling**:
   - Run [scripts/check_health.py](./scripts/check_health.py) or inspect root configuration files (`pubspec.yaml`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.).
   - Identify existing linter commands and test runners.
2. **Execute Baseline Checks**:
   - Run existing linters (e.g., `flutter analyze`, `npm run lint`, `cargo clippy`, `pytest`).
   - Run existing unit/integration test suites to record baseline pass rate and coverage.
3. **Protect Repository with `.gitignore`**:
   - Verify if `IMPROVEMENTS.md` is listed in `.gitignore`.
   - If missing, append `IMPROVEMENTS.md` to `.gitignore` to prevent temporary tracking documents from polluting version control history during development.
   - Commit the `.gitignore` update if the repository requires clean staging.

---

### Phase 2: Six-Dimensional Deep Audit

Conduct a thorough inspection across the six core dimensions. See [references/audit-dimensions.md](./references/audit-dimensions.md) for full audit criteria and checklists:

1. **Architecture & Modularity**:
   - Identify God classes/widgets (> 800 lines, multiple distinct responsibilities).
   - Check module boundary violations, layer leaking (e.g. UI directly querying raw file systems or unparsed network sockets).
   - Verify state management consistency (avoid mixing manual Prop Drilling with reactive stores).
2. **Code Quality & Robustness**:
   - Review static analysis warnings, dead code, strict null-safety, and type correctness.
   - Ensure explicit error hierarchies and graceful degradation instead of generic empty catches.
3. **Performance & Responsiveness**:
   - Identify synchronous I/O blocking UI or event loops.
   - Look for unnecessary whole-screen rebuilds or re-renders triggered on minor state changes.
   - Check streaming vs batch processing (e.g. SSE for AI/long operations instead of full buffering).
   - Detect memory leaks, unclosed streams/controllers, and unbounded cache sizes.
4. **Maintainability & Engineering Practices**:
   - Check localization (i18n) vs hardcoded user-facing strings.
   - Audit outdated or discontinued dependencies.
   - Check unified logging abstraction vs raw print statements.
5. **Security & Sandbox Defense**:
   - Audit path traversal vulnerabilities (e.g. `../../` escaping sandbox paths).
   - Check shell command injection in subprocess spawning.
   - Verify safe extraction of archives (prevent Zip Slip).
   - Ensure external hyperlinks use `rel="noopener noreferrer"`.
6. **Testing & Quality Assurance**:
   - Identify critical business logic with 0% test coverage.
   - Verify edge-case tests for parsers, serializers, and protocol adapters.

---

### Phase 3: Generating `IMPROVEMENTS.md`

Output a structured markdown file named `IMPROVEMENTS.md` at the project root using the standard format detailed in [references/improvements-template.md](./references/improvements-template.md).

#### Required Document Sections:
1. **Header & Document Nature Callout**:
   - Mark explicitly as a temporary local planning document excluded by `.gitignore`.
2. **Current State Overview (现状综合分析)**:
   - Architecture topology diagram (ASCII or Mermaid).
   - Quantitative scorecard table (Dimension | Rating / Score | Key Findings).
   - Baseline metrics (linter warnings count, test count, line coverage %).
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
  3. Run static analysis (must report 0 errors, 0 warnings).
  4. Run test suites (100% pass, no regression).
  5. If adding tests: verify new test assertions actually cover the updated logic.
  6. Edit IMPROVEMENTS.md: mark task as complete (e.g. change [ ] to [x]).
  7. Execute Git commit for this single task using Conventional Commits.
     Format: <type>(<scope>): <concise description>
```

#### Commit Discipline Rules:
- **One task per commit**: Never bundle unrelated tasks together.
- **Always verify before commit**: Never commit broken builds, failed tests, or lint warnings.
- **Commit message conventions**:
  - `feat`: New capability or completed user-facing feature.
  - `refactor`: Structural changes without altering runtime behavior.
  - `perf`: Performance optimizations, caching, asynchronous I/O.
  - `fix`: Bug fixes, security vulnerability patching.
  - `test`: Adding or expanding test coverage.

---

### Phase 5: Verification, Cleanup & CI Check

1. **Verify Full Task Completion**:
   - Run [scripts/track_progress.py](./scripts/track_progress.py) to ensure all tasks are marked `[x]`.
   - Run the full project test suite and linter one final time.
2. **Handle Document Lifecycle**:
   - If the user prompt specified: *"当改进建议文档被全部完成时可以删除"* (can be deleted upon completion) or running via `/improve-all`:
     - Delete `IMPROVEMENTS.md`.
     - Commit the deletion: `chore: 移除已全部落地的临时改进建议文档 IMPROVEMENTS.md`.
   - If the user specified to keep the document:
     - Keep `IMPROVEMENTS.md` with all items marked completed.
3. **Goal Termination Signal**:
   - If running under `/goal` or `/improve-all`, include `<!-- GOAL_COMPLETE -->` in your final response once all items are verified.
4. **Push & Monitor CI**:
   - Execute `git push origin <branch>`.
   - Inspect GitHub CI workflow status using [references/ci-monitoring.md](./references/ci-monitoring.md):
     ```bash
     gh run list --limit 1
     gh run watch
     ```
   - If any CI job fails, inspect failure logs immediately, apply targeted fixes, and commit.

---

## Quick Reference Scripts

- **Project Health Inspector**: `python scripts/check_health.py`
- **Progress Tracker & Validator**: `python scripts/track_progress.py IMPROVEMENTS.md`
