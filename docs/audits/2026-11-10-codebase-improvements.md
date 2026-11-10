# Codebase Audit & Improve: Architecture & Code Quality Assessment (IMPROVEMENTS.md)

> **Document Nature**: Temporary project health audit and technical improvement tracking document (excluded in `.gitignore`).
> This document coordinates step-by-step refactoring and quality hardening. Complete each task with an atomic Git commit.
> Upon full completion, this document can be archived to `docs/audits/YYYY-MM-DD-codebase-improvements.md` (recommended) or deleted.

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
| **架构设计 (Architecture)** | 4.8 / 5.0 | 双脚本职责清晰、无循环依赖；文档与安装器分层合理。 |
| **性能与响应度 (Performance)** | 4.9 / 5.0 | 正则已预编译，全仓扫描与 100 项单测均在秒级完成。 |
| **安全性与防御 (Security)** | 4.7 / 5.0 | 路径沙箱与 Git 失败关闭已就位；安装器根目录拒绝已对齐。 |
| **代码质量 (Code Quality)** | 4.4 / 5.0 | 静态分析零告警，但进度解析器存在未捕获的读取异常与表格识别盲区。 |
| **可维护性 (Maintainability)** | 4.5 / 5.0 | 文档完备，但 `SKILL.md` 清理模式仍指示提交一个被 `.gitignore` 排除的文件。 |
| **测试覆盖 (Testing)** | 4.7 / 5.0 | 行覆盖率 97%，但上述边界（无尾管表格、不可读路线图）尚无回归断言。 |

- **静态代码分析基线**：`0 errors`, `0 warnings` (`ruff check .` 全绿)
- **单元测试通过率**：`100% Pass` (107 / 107 tests)
- **代码行覆盖率**：`97.0%` (Hits: 641 / Total: 661)

### 3. 优势与工程亮点

1. **纯标准库零依赖**：检测与解析脚本仅使用 Python 标准库，跨平台即装即用。
2. **闭环安全门禁**：临时路线图自动忽略、Git 工作树洁净校验、进度门禁退出码完整。
3. **跨平台 CI 矩阵**：Ubuntu + Windows × Python 3.10–3.12，覆盖安装器与命令行端到端行为。

---

## 二、全维度问题清单与根因分析

### 1. 架构设计 (Architecture Design)
- 未发现新的架构分层问题：两个脚本保持独立可执行，安装器复制后无需包依赖。

### 2. 性能与响应度 (Performance)
- 未发现新的性能瓶颈：路线图解析为单次线性扫描，正则均为模块级预编译。

### 3. 安全性与沙箱防御 (Security)
- 未发现新的 P0/P1 安全问题：路径沙箱、根目录拒绝、Git 状态失败关闭均已落地。
- **问题 S1 (忽略规则回退判定偏离 Git 语义)**：在非 Git 工作树中，`.gitignore` 回退匹配强制小写化，导致 POSIX 大小写敏感文件系统上 `improvements.md` 被误判为可忽略 `IMPROVEMENTS.md`。

### 4. 代码质量与稳健性 (Code Quality)
- **问题 Q1 (路线图读取异常未捕获)**：`parse_improvements_file` 仅检查 `os.path.exists`，对目录、权限受限或读取失败的文件直接抛出 `PermissionError`/`IsADirectoryError` 回溯。
- **问题 Q2 (合法 Markdown 表格被静默忽略)**：解析器要求表格行同时以 `|` 开头和结尾，省略尾管的合法 Markdown 任务表会返回 0 个任务，导致 `--check` 门禁误报失败。
- **问题 Q3 (Bun 回退 lint 命令不可执行)**：无 `lint`/`check` 脚本时生成 `bun exec eslint .`，而 Bun 并未提供 `exec` 子命令，应使用其包二进制运行器 `bunx`。

### 5. 可维护性与工程化 (Maintainability)
- **问题 M1 (文档生命周期指令自相矛盾)**：`references/ci-monitoring.md` 已说明删除被忽略的路线图无需提交，但 `SKILL.md` 及其打包副本仍要求执行空的 `chore:` 提交。

### 6. 测试覆盖与质量工程 (Testing & QA)
- **问题 T1 (边界回归缺失)**：无尾管表格、目录路径路线图、Bun lint 回退与忽略规则大小写语义均无断言。

---

## 三、改进方案与落地路径

### P0 级：严重阻断、安全提权与崩溃隐患
- 无 P0 阻断项。

### P1 级：架构核心解耦与高收益性能优化
- **OPT-01: 支持省略尾管的合法 Markdown 任务表**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：以首管识别表格行，尾管改为可选；分隔行探测同步放宽，并要求至少两个单元格以避免把单管道文本误判为任务。
  - **预期收益**：合法路线图不再被静默解析为 0 个任务，CI 进度门禁结果可信。

- **OPT-02: 路线图不可读时返回结构化错误**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：将文件读取包裹在 `except OSError` 中，返回 `Unable to read file` 错误；CLI 保持退出码 2，不再输出回溯。
  - **预期收益**：目录、权限或并发删除等异常路径给出可操作提示，而非崩溃。

### P2 级：功能完备性、模块重构与容错降级
- **OPT-03: 修正 Bun 回退 lint 命令**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：Bun 项目无 lint 脚本时使用 `bunx eslint .`（Bun 未安装时回退 `npx eslint .`）。
  - **预期收益**：Bun 项目的基线 lint 命令可直接执行。

- **OPT-04: 忽略规则回退匹配遵循平台大小写语义**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：改用 `fnmatch.fnmatch`（内部按 `os.path.normcase` 归一化），不再无条件小写化；Windows 继续保持大小写不敏感，POSIX 恢复大小写敏感。
  - **预期收益**：非 Git 目录下的预检结论与 Git 在对应平台上的真实行为一致。

### P3 级：工程规范、状态重构与测试加固
- **OPT-05: 修正清理模式文档中的无效提交指令**
  - **涉及文件**：`SKILL.md`, `skills/improve/SKILL.md`, `tests/test_repo_docs.py`
  - **方案**：删除“删除并提交”的误导性指令，明确被 `.gitignore` 排除的文件删除后无需提交；保持两份技能文档字节一致。
  - **预期收益**：文档生命周期说明与 `references/ci-monitoring.md` 及实际 Git 行为一致。

---

## 四、实施优先级与推进清单

| 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P1** | **OPT-01** | 支持省略尾管的合法 Markdown 任务表 | 消除 0 任务误报 | `scripts/track_progress.py`, `tests/test_track_progress.py` | [x] |
| **P1** | **OPT-02** | 路线图不可读时返回结构化错误 | 异常路径不再回溯崩溃 | `scripts/track_progress.py`, `tests/test_track_progress.py` | [x] |
| **P2** | **OPT-03** | 修正 Bun 回退 lint 命令 | 基线命令可直接执行 | `scripts/check_health.py`, `tests/test_check_health.py` | [x] |
| **P2** | **OPT-04** | 忽略规则回退匹配遵循平台大小写语义 | 预检结论与 Git 行为一致 | `scripts/check_health.py`, `tests/test_check_health.py` | [x] |
| **P3** | **OPT-05** | 修正清理模式文档中的无效提交指令 | 文档生命周期说明自洽 | `SKILL.md`, `skills/improve/SKILL.md`, `tests/test_repo_docs.py` | [x] |
