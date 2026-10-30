# Codebase Audit & Improvement Workflow (`codebase-audit-and-improve`)

[![Skill](https://img.shields.io/badge/Antigravity-Skill-4285F4?logo=google)](https://github.com/Aclguh/codebase-audit-and-improve)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Aclguh/codebase-audit-and-improve/pulls)

[English](README.md) | [简体中文](README_zh.md)

---

An enterprise-grade, desensitized **Antigravity AI Agent Skill** (`/improve` and `/improve-all`) designed for automated project health assessment, structured roadmapping via temporary `IMPROVEMENTS.md` documents, and disciplined, test-verified atomic implementation loops.

## Key Features

- **Multi-Dimensional Audit & Subagent Support**: Thorough assessment across 6 core technical dimensions:
  1. **Architecture Design & Modularity**: Detect god classes/components, layer-skipping, and Monorepo boundaries.
  2. **Code Quality & Robustness**: Enforce incremental zero-tolerance (0 errors, 0 new warnings), strict typing, and defensive exception handling.
  3. **Performance & Responsiveness**: Mitigate main-thread blocking I/O, unnecessary full rerenders, and streaming/memory overhead.
  4. **Maintainability & Engineering Practices**: Ensure localization coverage, update deprecated dependencies, and enforce logging standards.
  5. **Security & Sandbox Defense**: Defend against path traversal, command injection, and Zip Slip vulnerabilities.
  6. **Testing & Quality Assurance**: Eliminate coverage blind spots in critical logic, add regression assertions, and ensure CI friendliness.
  *(Supports delegating parallel sub-audits to read-only `research` subagents for large codebases to preserve main context).*
- **Monorepo & Polyglot Ecosystem**: Out-of-the-box detection for Flutter/Dart, Node.js (npm/pnpm/yarn/bun), Python (uv/poetry/pdm), Rust, Go, Java/Kotlin (Maven/Gradle), .NET/C#, C/C++ (CMake), PHP, and Ruby.
- **Structured Tracking (`IMPROVEMENTS.md`)**:
  - Automatically guarded in `.gitignore` to prevent polluting remote repositories.
  - Standardized task backlog (P0 blocker to P3 polish) with tracked identifiers (`OPT-01`, `OPT-02`, etc.).
  - Flexible document lifecycle: Archive to `docs/audits/` (recommended) or clean up upon completion.
- **Incremental Zero-Tolerance Quality Gate**:
  - One improvement per independent Git commit following Conventional Commits.
  - Pre-commit gate distinguishes pre-existing legacy warnings from new ones: **0 errors, 0 newly introduced warnings, and total warnings <= baseline**.
  - Tiered testing: Fast targeted unit tests in per-task inner loops, full-suite regression at final verification.
- **Protected Branch & PR Workflow**:
  - Automatically detects protected branches (`main`, `master`, `release`).
  - Promotes improvements to dedicated feature branches and opens Pull Requests via GitHub CLI (`gh pr create`).
- **Goal-Driven Autonomy**:
  - Pairs with `/goal` or `/improve-all` for autonomous refactoring, terminating only when all tasks pass verification.

## Quick Start & Installation

### Global Installation (Applies to all Antigravity workspaces)

**PowerShell (Windows):**
```powershell
git clone https://github.com/Aclguh/codebase-audit-and-improve.git
cd codebase-audit-and-improve
.\install.ps1
```

**Bash (Linux / macOS):**
```bash
git clone https://github.com/Aclguh/codebase-audit-and-improve.git
cd codebase-audit-and-improve
chmod +x install.sh && ./install.sh
```

### Workspace-Only Installation (Committed to your project)

```powershell
# Windows
.\install.ps1 -Workspace

# Linux / macOS
./install.sh --workspace
```

## How to Use

### Option 1: Full-Loop Autonomous Pipeline (`/improve-all`)

To run the complete audit, atomic implementation, test verification, git commits, document archiving, PR creation, and CI monitoring in a single autonomous pass:

```text
/improve-all
```

The agent will execute end-to-end:
1. Pre-flight cleanliness & baseline discovery (`check_health.py --json`).
2. Six-dimensional health audit (parallel subagents supported).
3. Generate structured `IMPROVEMENTS.md`.
4. Atomically implement each task in sequence (incremental zero-tolerance lint gate, tiered tests, Conventional Commits).
5. Run full regression suite, archive/clean up `IMPROVEMENTS.md`, create PR if on protected branch, push to remote, and monitor GitHub Actions CI until green.

---

### Option 2: Step-by-Step Interactive Workflow (`/improve`)

If you want to review findings before implementing:

#### 1. Generate Improvement Roadmap
```text
/improve
```
The agent audits the codebase and produces `IMPROVEMENTS.md` with quantitative scorecards and prioritized task lists.

#### 2. Implement Tasks
To autonomously implement all items:
```text
/goal implement all
```
*(or `/goal 全部实现`)*

#### 3. Verification, PR & Remote Push
When all tasks are complete:
```text
push and verify GitHub CI status
```

## Repository Structure

```
codebase-audit-and-improve/
├── SKILL.md                     # Antigravity skill definition (/improve, /improve-all)
├── README.md                    # English documentation
├── README_zh.md                 # Chinese documentation
├── LICENSE                      # MIT License
├── install.ps1                  # Windows installation script (improve & improve-all)
├── install.sh                   # Linux/macOS installation script (improve & improve-all)
├── references/                  # Reference documents (loaded on demand)
│   ├── audit-dimensions.md      # Detailed diagnostic checklists for 6 dimensions
│   ├── improvements-template.md # Universal IMPROVEMENTS.md template
│   ├── execution-loop.md        # Atomic execution, tiered testing & commit specifications
│   └── ci-monitoring.md         # Branch protection, PR creation & CI troubleshooting
├── scripts/                     # Helper utility scripts
│   ├── check_health.py          # Stack detector, monorepo validator & baseline tool
│   └── track_progress.py        # Dynamic task parser, progress calculator & CI checker
├── skills/                      # Bundled skill definitions
│   ├── improve/                 # /improve skill
│   └── improve-all/             # /improve-all skill
├── tests/                       # Automated test suite
│   ├── test_check_health.py     # Unit tests for health inspector
│   └── test_track_progress.py   # Unit tests for progress tracker
└── examples/
    └── sample-improvements.md   # Production-grade sample IMPROVEMENTS.md
```

## Helper Scripts & CLI Reference

```bash
# Check current project tech stack, monorepo, and git guard status
python scripts/check_health.py

# Machine-readable JSON output for Agent ingestion
python scripts/check_health.py --json

# Automatically ensure IMPROVEMENTS.md is in .gitignore
python scripts/check_health.py --fix-gitignore

# Analyze progress and completion rates in IMPROVEMENTS.md
python scripts/track_progress.py IMPROVEMENTS.md

# CI gate mode (exit 0 if 100% complete, exit 1 if pending tasks remain)
python scripts/track_progress.py --check

# Run automated test suite
python -m unittest discover tests
```

## License

This project is open-sourced under the [MIT License](./LICENSE).
