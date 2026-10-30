# Codebase Audit & Improvement Workflow (`codebase-audit-and-improve`)

[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Universal%20Standard-6366F1)](https://github.com/Aclguh/codebase-audit-and-improve)
[![Supported Agents](https://img.shields.io/badge/Agents-Claude%20%7C%20Codex%20%7C%20Cursor%20%7C%20DeepSeek%20%7C%20Antigravity-10B981)](https://github.com/Aclguh/codebase-audit-and-improve)
[![CI](https://github.com/Aclguh/codebase-audit-and-improve/actions/workflows/ci.yml/badge.svg)](https://github.com/Aclguh/codebase-audit-and-improve/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Aclguh/codebase-audit-and-improve/pulls)

[English](README.md) | [简体中文](README_zh.md)

---

A universal, production-grade **AI Coding Agent Skill & Workflow** (`/improve` and `/improve-all`) built for automated codebase health audits, structured roadmapping via temporary `IMPROVEMENTS.md` documents, and disciplined, test-verified atomic implementation loops across modern AI programming assistants.

## Multi-Agent Compatibility Matrix

This project complies with the **Agent Skills Specification** and provides native autocompletion (`/` preview) and command invocation across leading AI coding tools:

| AI Agent / Tool | Invocation Syntax | Autocomplete (`/` preview) | Configuration Scope |
| :--- | :--- | :--- | :--- |
| **Anthropic Claude Code** | `/improve`, `/improve-all` | Native CLI dropdown | `~/.claude/skills/` |
| **Cursor IDE** | `/improve`, `/improve-all` | Composer / Agent chat dropdown | `~/.cursor/rules/` or `.cursor/commands/` |
| **OpenAI Codex (Desktop)** | `/imp` -> `Improve`, `Improve All` | Native Composer dropdown | `~/.agents/skills/` |
| **OpenAI Codex (CLI)** | `$improve`, `$improve-all`, or `/skills` | `$` mentions & interactive `/skills` menu | `~/.agents/skills/` |
| **DeepSeek Harness (dsh)** | `/improve`, `/improve-all` | Web UI / TUI / Desktop popup | `~/.agents/skills/` |
| **Google Antigravity** | `/improve`, `/improve-all` | Native Skill Palette | `~/.gemini/config/skills/` |
| **Continue.dev** | `/improve`, `/improve-all` | VS Code / JetBrains palette | `~/.continue/config.json` |

## Key Features

- **Multi-Dimensional Audit & Parallel Delegation**: Thorough assessment across 6 core technical dimensions:
  1. **Architecture Design & Modularity**: Detect god classes/components, layer-skipping, and Monorepo boundaries.
  2. **Code Quality & Robustness**: Enforce incremental zero-tolerance (0 errors, 0 new warnings), strict typing, and defensive exception handling.
  3. **Performance & Responsiveness**: Mitigate main-thread blocking I/O, unnecessary full rerenders, and streaming/memory overhead.
  4. **Maintainability & Engineering Practices**: Ensure localization coverage, update deprecated dependencies, and enforce logging standards.
  5. **Security & Sandbox Defense**: Defend against path traversal, command injection, and Zip Slip vulnerabilities.
  6. **Testing & Quality Assurance**: Eliminate coverage blind spots in critical logic, add regression assertions, and ensure CI friendliness.
  *(Supports delegating parallel sub-audits to read-only background subagents or child threads in large codebases to preserve main context).*
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
  - Pairs with autonomous execution modes (`/improve-all`, `/goal implement all`, or background agent loops), terminating only when all tasks pass verification.

## Quick Start & Installation

### 1. Global Installation (All Agents)

Install for all detected agent environments in a single command:

**PowerShell (Windows):**
```powershell
git clone https://github.com/Aclguh/codebase-audit-and-improve.git
cd codebase-audit-and-improve
.\install.ps1 -Target All
```

**Bash (Linux / macOS):**
```bash
git clone https://github.com/Aclguh/codebase-audit-and-improve.git
cd codebase-audit-and-improve
chmod +x install.sh && ./install.sh all
```

*Tip: You can also specify an individual agent target: `-Target Claude`, `-Target Codex`, `-Target Cursor`, `-Target DeepSeek`, `-Target Antigravity`, or `-Target Continue`.*

### 2. Workspace-Only Installation (Committed to your project repository)

Generate the commands and skills directly in your current repository workspace so any team member using Claude Code, Codex, Cursor, DeepSeek Harness, Antigravity, or Continue gets immediate `/` autocompletion:

```powershell
# Windows
.\install.ps1 -Target All -Workspace

# Linux / macOS
./install.sh all --workspace
```

## How to Use

### Option 1: Full-Loop Autonomous Pipeline (`/improve-all`)

To run the complete audit, atomic implementation, test verification, git commits, document archiving, PR creation, and CI monitoring in a single autonomous pass:

```text
/improve-all
```
*(Or in agents without slash commands: `Execute improve-all to audit and refactor this codebase`)*

The agent will execute end-to-end:
1. Pre-flight cleanliness & baseline discovery (`check_health.py --json`).
2. Six-dimensional health audit (parallel subagents/threads supported).
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
*(Or in Codex CLI: `$improve`; or in prompt: `Run codebase audit with improve skill`)*

The agent audits the codebase and produces `IMPROVEMENTS.md` with quantitative scorecards and prioritized task lists.

#### 2. Implement Tasks
Instruct the agent to autonomously implement all items:
```text
Implement all tasks in IMPROVEMENTS.md atomically
```
*(or `/goal implement all` in tools supporting `/goal`)*

#### 3. Verification, PR & Remote Push
When all tasks are complete:
```text
Run full test suite, push changes, and verify CI status
```

## Repository Structure

```
codebase-audit-and-improve/
├── SKILL.md                     # Universal Agent Skill entrypoint (/improve, /improve-all)
├── README.md                    # English documentation
├── README_zh.md                 # Chinese documentation
├── LICENSE                      # MIT License
├── install.ps1                  # Windows multi-agent installation script
├── install.sh                   # Linux/macOS multi-agent installation script
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
├── templates/                   # Integration templates for non-standard agents
│   ├── continue/                # Continue.dev custom commands configuration
│   └── cursor/                  # Cursor IDE command templates
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
