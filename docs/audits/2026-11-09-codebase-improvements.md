# Codebase Audit & Improve: Architecture & Code Quality Assessment (IMPROVEMENTS.md)

> **Document Nature**: Temporary project health audit and technical improvement tracking document (excluded in `.gitignore`).
> This document coordinates step-by-step refactoring and quality hardening. Complete each task with an atomic Git commit.
> Upon full completion, this document can be archived to `docs/audits/YYYY-MM-DD-codebase-improvements.md` (recommended) or deleted.

---

## Table of Contents

- [一、项目现状与整体架构评估](#一项目现状与整体架构评估)
  - [1. 架构定位与模块拓扑](#1-架构定位与模块拓扑)
  - [2. 核心技术指标与现状概览](#2-核心技术指标与现状概览)
  - [3. 优势与工程亮点](#3-优势与工程亮点)
- [二、全维度问题清单与根因分析](#二全维度问题清单与根因分析)
  - [1. 架构设计 (Architecture Design)](#1-架构设计-architecture-design)
  - [2. 性能与响应度 (Performance)](#2-性能与响应度-performance)
  - [3. 安全性与沙箱防御 (Security)](#3-安全性与沙箱防御-security)
  - [4. 代码质量与稳健性 (Code Quality)](#4-代码质量与稳健性-code-quality)
  - [5. 可维护性与工程化 (Maintainability)](#5-可维护性与工程化-maintainability)
  - [6. 测试覆盖与质量工程 (Testing & QA)](#6-测试覆盖与质量工程-testing--qa)
- [三、改进方案与落地路径](#三改进方案与落地路径)
  - [P0 级：严重阻断、安全提权与崩溃隐患](#p0-级严重阻断安全提权与崩溃隐患)
  - [P1 级：架构核心解耦与高收益性能优化](#p1-级架构核心解耦与高收益性能优化)
  - [P2 级：功能完备性、模块重构与容错降级](#p2-级功能完备性模块重构与容错降级)
  - [P3 级：工程规范、状态重构与测试加固](#p3-级工程规范状态重构与测试加固)
- [四、实施优先级与推进清单](#四实施优先级与推进清单)

---

## 一、项目现状与整体架构评估

### 1. 架构定位与模块拓扑

`codebase-audit-and-improve` 是一个跨平台的通用多智能体代码库审计与改进工作流框架，为 Antigravity、Claude Code、Cursor、Continue.dev、DeepSeek Harness (dsh) 与 OpenAI Codex 提供统一的六维健康审计与原子化落地标准。

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Agent Interfaces                   │
│   (Antigravity / Claude Code / Cursor / Codex / Continue)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Slash Commands (/improve, /improve-all)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     Skills & Templates                      │
│      (skills/improve, skills/improve-all, templates/*)      │
└──────────────────────────────┬──────────────────────────────┘
                               │ Invokes Diagnostics & Parsers
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Core Automation Scripts                   │
│        (scripts/check_health.py, scripts/track_progress.py) │
└──────────────────────────────┬──────────────────────────────┘
                               │ File System / Git / Manifest Checks
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Target Repository Codebase                  │
│       (Linters, Test Runners, Git Status, IMPROVEMENTS.md)  │
└─────────────────────────────────────────────────────────────┘
```

### 2. 核心技术指标与现状概览

| 评估维度 | 评级 / 得分 (满分 5.0) | 核心现状与风险分析 |
| :--- | :---: | :--- |
| **架构设计 (Architecture)** | 4.8 / 5.0 | 双脚本职责清晰、无循环依赖；安装器与技能文档分层合理。 |
| **性能与响应度 (Performance)** | 4.9 / 5.0 | 正则已预编译，全仓扫描与 94 项单测均在秒级完成。 |
| **安全性与防御 (Security)** | 4.6 / 5.0 | 路径沙箱校验完善，但 `install.ps1` 缺少与 `install.sh` 对等的文件系统根目录拒绝逻辑。 |
| **代码质量 (Code Quality)** | 4.5 / 5.0 | 静态分析零告警，但 Maven Wrapper 与 Bun 的基线命令生成存在跨平台/语义偏差。 |
| **可维护性 (Maintainability)** | 4.6 / 5.0 | 文档完备，但 README 目录树遗漏部分测试与模板，清理流程文档含无效提交命令。 |
| **测试覆盖 (Testing)** | 4.7 / 5.0 | 行覆盖率 97%，新增边界（否定规则、转义竖线、Maven Windows、Bun）尚未覆盖。 |

- **静态代码分析基线**：`0 errors`, `0 warnings` (`ruff check .` 全绿)
- **单元测试通过率**：`100% Pass` (94 / 94 tests)
- **代码行覆盖率**：`97.0%` (Hits: 595 / Total: 612)

### 3. 优势与工程亮点

1. **纯标准库零依赖**：检测与解析脚本仅使用 Python 标准库，跨平台即装即用。
2. **闭环安全门禁**：临时路线图自动忽略、Git 工作树洁净校验、进度门禁退出码完整。
3. **多智能体唯一性安装**：自动清理历史重复命令，避免各 Agent 出现重复斜杠命令。

---

## 二、全维度问题清单与根因分析

### 1. 架构设计 (Architecture Design)
- **问题 A1 (`install.ps1` 与 `install.sh` 的根目录防御不对称)**：`install.sh` 在 workspace 模式下拒绝 `/`，而 `install.ps1` 未拒绝 `C:\`，从盘符根目录执行 `-Workspace` 会把技能写入并重建 `C:\.claude\skills`。

### 2. 性能与响应度 (Performance)
- 未发现新的性能瓶颈：`clean_cell` 与优先级正则均已模块级预编译。

### 3. 安全性与沙箱防御 (Security)
- **问题 S1 (工作区安装根目录逃逸)**：同 A1。安装器会对目标目录执行 `Remove-Item -Recurse -Force`，缺少根目录拒绝意味着一次误操作即可改写盘符根下的同名配置目录。

### 4. 代码质量与稳健性 (Code Quality)
- **问题 Q1 (Maven Wrapper 在 Windows 上不可执行)**：`detect_stack` 固定生成 `./mvnw ...`，而 Windows `cmd.exe` 无法解析 POSIX 相对路径，即使 `mvnw.cmd` 存在也会导致基线命令失败。
- **问题 Q2 (Bun 测试命令指向错误运行器)**：`parse_package_json` 对 Bun 生成 `bun test`（Bun 内置测试运行器），而非 `bun run test`（`package.json` 的 `test` 脚本），基线结果与实际项目测试不一致。
- **问题 Q3 (`.gitignore` 否定规则被忽略)**：无 Git 时的回退匹配直接跳过 `!` 行，`*.md` + `!IMPROVEMENTS.md` 会被误判为“已忽略”，导致路线图文件可能被提交。
- **问题 Q4 (Git 状态探测超时后失败开放)**：`check_git_status` 仅在 `git status` 返回非零码时 fail-closed；若调用抛出 `TimeoutExpired`，外层 `except` 不会重置 `is_clean`，预检会把未知状态当作洁净树。

### 5. 可维护性与工程化 (Maintainability)
- **问题 M1 (文档结构漂移)**：`README.md` / `README_zh.md` 的目录树未列出 `test_install_ps1.py`、`test_repo_docs.py`、`templates/claude/` 与 `.github/`。
- **问题 M2 (`ci-monitoring.md` 清理模式含无效提交)**：`IMPROVEMENTS.md` 被 `.gitignore` 排除，`git commit -am` 无内容可提交，会误导执行者。

### 6. 测试覆盖与质量工程 (Testing & QA)
- **问题 T1 (边界回归缺失)**：上述修复点（Windows Maven、Bun 命令、否定规则、Git 超时、转义竖线表格、根目录安装拒绝）均无对应断言。

---

## 三、改进方案与落地路径

### P0 级：严重阻断、安全提权与崩溃隐患
- 无 P0 阻断项。

### P1 级：架构核心解耦与高收益性能优化
- **OPT-01: 修正 Windows 下 Maven Wrapper 命令解析**
  - **涉及文件**：`scripts/check_health.py`
  - **方案**：Windows 优先使用 `mvnw.cmd`；仅有 POSIX `mvnw` 时回退到 `mvn`，避免生成无法执行的 `./mvnw`。
  - **预期收益**：Maven 项目在 Windows 上的 lint/test 基线不再因路径方言失败。

- **OPT-02: 修正 Bun 测试脚本命令解析**
  - **涉及文件**：`scripts/check_health.py`
  - **方案**：存在 `test` 脚本时生成 `bun run test`，无脚本时保留 `bun test`；覆盖率回退使用 `--coverage` 而非 `-- --coverage`。
  - **预期收益**：Bun 项目基线执行真实的项目测试脚本，统计结果可信。

### P2 级：功能完备性、模块重构与容错降级
- **OPT-03: 按顺序处理 `.gitignore` 否定规则**
  - **涉及文件**：`scripts/check_health.py`
  - **方案**：回退匹配记录最后一条命中规则，`!` 前缀取反，使 `*.md` + `!IMPROVEMENTS.md` 判定为未忽略。
  - **预期收益**：无 Git 或非工作树目录下预检不再误报“已保护”。

- **OPT-04: Git 状态探测异常时失败关闭**
  - **涉及文件**：`scripts/check_health.py`
  - **方案**：记录状态是否成功校验；外层异常时若尚未校验则置 `is_clean = False` 并写入 `status_error`。
  - **预期收益**：超时/异常不再伪装成洁净工作树，保护原子提交循环。

- **OPT-05: `install.ps1` 拒绝文件系统根目录工作区安装**
  - **涉及文件**：`install.ps1`, `tests/test_install_ps1.py`
  - **方案**：workspace 模式下与 `install.sh` 对齐，检测当前目录是否为盘符根并退出码 2。
  - **预期收益**：消除从 `C:\` 误安装导致的根目录配置重建风险。

### P3 级：工程规范、状态重构与测试加固
- **OPT-06: 表格解析支持转义竖线**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：新增 `split_table_row`，仅在未转义的 `|` 处切分并还原 `\|`。
  - **预期收益**：包含 `\|` 的任务名不再错位，状态统计保持准确。

- **OPT-07: 同步文档结构清单与清理流程说明**
  - **涉及文件**：`README.md`, `README_zh.md`, `references/ci-monitoring.md`
  - **方案**：补齐遗漏的测试/模板/CI 条目；删除被 `.gitignore` 排除文件的无效 `git commit` 步骤。
  - **预期收益**：文档与实际仓库结构、文档生命周期行为一致。

---

## 四、实施优先级与推进清单

| 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P1** | **OPT-01** | 修正 Windows 下 Maven Wrapper 命令解析 | 恢复 Windows Maven 基线可执行性 | `scripts/check_health.py` | [x] |
| **P1** | **OPT-02** | 修正 Bun 测试脚本命令解析 | 基线与项目真实测试脚本一致 | `scripts/check_health.py` | [x] |
| **P2** | **OPT-03** | 按顺序处理 `.gitignore` 否定规则 | 消除无 Git 环境的忽略误判 | `scripts/check_health.py` | [x] |
| **P2** | **OPT-04** | Git 状态探测异常时失败关闭 | 超时不再伪装成洁净工作树 | `scripts/check_health.py` | [x] |
| **P2** | **OPT-05** | `install.ps1` 拒绝文件系统根目录工作区安装 | 与 install.sh 对齐，防止根目录重建 | `install.ps1`, `tests/test_install_ps1.py` | [x] |
| **P3** | **OPT-06** | 表格解析支持转义竖线 | 修复含 `\|` 任务名的列错位 | `scripts/track_progress.py`, `tests/test_track_progress.py` | [x] |
| **P3** | **OPT-07** | 同步文档结构清单与清理流程说明 | 文档与仓库结构/行为一致 | `README.md`, `README_zh.md`, `references/ci-monitoring.md` | [x] |
