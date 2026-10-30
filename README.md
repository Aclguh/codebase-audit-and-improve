# Codebase Audit & Improvement Workflow (`codebase-audit-and-improve`)

[![Skill](https://img.shields.io/badge/Antigravity-Skill-4285F4?logo=google)](https://github.com/Aclguh/codebase-audit-and-improve)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Aclguh/codebase-audit-and-improve/pulls)

[English](README.md) | [简体中文](README_zh.md)

---

An enterprise-grade, desensitized **Antigravity AI Agent Skill** (`improve`) designed for automated project health assessment, structured roadmapping via temporary `IMPROVEMENTS.md` documents, and disciplined, test-verified atomic implementation loops.

## Key Features

- **Multi-Dimensional Audit**: Thorough assessment across 6 core technical dimensions:
  1. **Architecture Design & Modularity**: Detect god classes/components, layer-skipping, and fragmented state management.
  2. **Code Quality & Robustness**: Enforce 0 linter warnings, strict typing, and defensive exception handling.
  3. **Performance & Responsiveness**: Mitigate main-thread blocking I/O, unnecessary full rerenders, and streaming/memory overhead.
  4. **Maintainability & Engineering Practices**: Ensure localization coverage, update deprecated dependencies, and enforce logging standards.
  5. **Security & Sandbox Defense**: Defend against path traversal, command injection, and Zip Slip vulnerabilities.
  6. **Testing & Quality Assurance**: Eliminate coverage blind spots in critical logic, add regression assertions, and ensure CI friendliness.
- **Structured Tracking (`IMPROVEMENTS.md`)**:
  - Automatically maintained in `.gitignore` to prevent polluting remote repositories.
  - Standardized task backlog (P0 blocker to P3 polish) with tracked identifiers (`OPT-01`, `OPT-02`, etc.).
- **Atomic Execution Loop**:
  - One improvement per independent Git commit following Conventional Commits.
  - Pre-commit gate: 0 linter errors, 0 linter warnings, and 100% test pass rate.
- **Goal-Driven Autonomy**:
  - Seamlessly integrates with `/goal` for overnight autonomous refactoring, terminating only when all tasks pass verification.
- **CI/CD Closure**:
  - Automatically cleans up the temporary roadmap upon full completion, pushes to remote repository, and monitors GitHub Actions CI runs via GitHub CLI (`gh`).

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

### 1. Generate Improvement Roadmap

In your Antigravity conversation, simply type the slash command:

```text
/improve
```

The agent will automatically:
- Inspect project tech stack, tooling, and ensure `IMPROVEMENTS.md` is added to `.gitignore`.
- Run baseline linters and test suites.
- Perform a thorough 6-dimensional health audit.
- Output the quantitative scorecards and prioritized task backlog (`OPT-01`, `OPT-02`...) in `IMPROVEMENTS.md`.

*(Optional natural language prompt is also supported: `Please evaluate the overall health of the current project across code quality, architecture design, performance, maintainability, security, and test coverage...`)*

### 2. Autonomous Implementation

To autonomously implement all items in sequence:
```text
/goal implement all
```
*(or `/goal 全部实现`)*

### 3. Verification & Push

When all tasks are complete:
```text
push and verify GitHub CI status
```

## Repository Structure

```
codebase-audit-and-improve/
├── SKILL.md                     # Antigravity skill definition and metadata (/improve)
├── README.md                    # English documentation
├── README_zh.md                 # Chinese documentation
├── LICENSE                      # MIT License
├── install.ps1                  # Windows installation script
├── install.sh                   # Linux/macOS installation script
├── references/                  # Reference documents (loaded on demand)
│   ├── audit-dimensions.md      # Detailed diagnostic checklists for 6 dimensions
│   ├── improvements-template.md # Sanitized IMPROVEMENTS.md standard template
│   ├── execution-loop.md        # Atomic execution, linting, and commit specifications
│   └── ci-monitoring.md         # GitHub CLI monitoring and CI troubleshooting guide
├── scripts/                     # Helper utility scripts
│   ├── check_health.py          # Tech stack detector and .gitignore validator
│   └── track_progress.py        # IMPROVEMENTS.md parser and completion tracker
└── examples/
    └── sample-improvements.md   # Production-grade sample IMPROVEMENTS.md
```

## Helper Scripts

```bash
# Check current project tech stack and verify .gitignore ignores IMPROVEMENTS.md
python scripts/check_health.py

# Analyze progress and completion rates in IMPROVEMENTS.md
python scripts/track_progress.py IMPROVEMENTS.md
```

## License

This project is open-sourced under the [MIT License](./LICENSE).
