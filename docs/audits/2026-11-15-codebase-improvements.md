# Codebase Audit & Improve: Architecture & Code Quality Assessment (IMPROVEMENTS.md)

> **Document Nature**: Temporary project health audit and technical improvement tracking document (excluded in `.gitignore`).
> This document coordinates step-by-step refactoring and quality hardening. Complete each task with an atomic Git commit.
> Upon full completion, this document can be archived to `docs/audits/YYYY-MM-DD-codebase-improvements.md` (recommended) or deleted.

---

## 目录

- [一、项目现状与整体架构评估](#一项目现状与整体架构评估)
  - [1. 架构定位与模块拓扑](#1-架构定位与模块拓扑)
  - [2. 核心技术指标与现状概览](#2-核心技术指标与现状概览)
  - [3. 优势与工程亮点](#3-优势与工程亮点)
- [二、全维度问题清单与根因分析](#二全维度问题清单与根因分析)
- [三、改进方案与落地路径](#三改进方案与落地路径)
- [四、实施优先级与推进清单](#四实施优先级与推进清单)

---

## 一、项目现状与整体架构评估

### 1. 架构定位与模块拓扑

`codebase-audit-and-improve` 是面向多家 AI 编程助手的跨平台审计工作流框架。核心自动化由 `scripts/check_health.py`（栈/单仓探测、Git 护栏、基线执行）与 `scripts/track_progress.py`（路线图解析、进度统计、CI 门禁）两个零依赖标准库脚本承担；安装器负责把技能与模板分发到各代理。

```
┌─────────────────────────────────────────────────────────────┐
│        Agent Frontends (Antigravity / Claude / Cursor /     │
│              Continue / DeepSeek / Codex)                   │
└──────────────────────────────┬──────────────────────────────┘
                               │ (SKILL.md + templates)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  Core Automation (scripts/check_health.py, track_progress.py)│
│   · stack & monorepo detection   · git guard & gitignore     │
│   · IMPROVEMENTS.md table/checklist parser & progress gate   │
└──────────────────────────────┬──────────────────────────────┘
                               │ (subprocess / filesystem)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Target Repository (manifests, git, docs)        │
└─────────────────────────────────────────────────────────────┘
```

### 2. 核心技术指标与现状概览

| 评估维度 | 评级 / 得分 (满分 5.0) | 核心现状与风险分析 |
| :--- | :---: | :--- |
| **架构设计 (Architecture)** | 4.9 / 5.0 | 双脚本职责清晰、无循环依赖；安装器与模板职责单一。 |
| **性能与响应度 (Performance)** | 5.0 / 5.0 | 线性单遍扫描、正则预编译，无可感知热点。 |
| **安全性与沙箱防御 (Security)** | 5.0 / 5.0 | 凭据脱敏、安装路径白名单、git 状态失败关闭均有效；基线命令由内部清单生成，不接受外部拼接输入。 |
| **代码质量 (Code Quality)** | 4.3 / 5.0 | 带状态标签的中文进度（如"完成情况: 80%"）被误判为已完成；带变体选择符的 emoji 复选框任务行被整行丢弃。 |
| **可维护性 (Maintainability)** | 4.5 / 5.0 | Git 探测失败的真正原因（dubious ownership / 缺少 git）被降级为"不是 Git 仓库"；ruff 未启用空白规则；CI 版本矩阵停留在 3.12。 |
| **测试覆盖 (Testing)** | 4.8 / 5.0 | `scripts/` 行覆盖率 97.3%，若干异常/转义分支仍无回归断言。 |

- **静态代码分析基线**：`0 errors`, `0 warnings` (`python -m ruff check .`，规则集 E4/E7/E9/F)
- **单元测试通过率**：`100% Pass` (130 / 130 tests，本机 Windows；Linux 会跳过 PowerShell 安装器用例)
- **代码行覆盖率**：`97.3%` (Hits: 690 / Total: 709, CI gate `--source=scripts`, threshold 90%)
- **跨版本验证**：Python 3.10 / 3.13.5 / 3.14.5 本机均 130 tests OK；CI 矩阵仅声明 3.10–3.12。

### 3. 优势与工程亮点

1. **纯标准库零外部依赖**：两个脚本在任意干净 Python 3.10+ 环境中即装即用。
2. **Fail-closed 安全护栏**：git 状态无法核实时按脏树处理，安装路径限定在工作区与 HOME 之内，remote URL 自动脱敏。
3. **成熟的 Markdown 解析**：表格/清单双通道解析、代码围栏跳过、转义竖线、进度百分比与中英文状态词均已覆盖并有回归测试。

---

## 二、全维度问题清单与根因分析

### 1. 架构设计 (Architecture Design)

- 本轮未发现分层或耦合问题：两个脚本均保持单一职责，安装器仅做文件分发。

### 2. 性能与响应度 (Performance)

- 未发现热点：解析为单遍线性扫描，正则全部预编译，Git 子进程数量固定且超时受控。

### 3. 安全性与沙箱防御 (Security)

- 复核路径校验、凭据脱敏与命令执行路径后未发现新缺口。`run_baseline_command` 使用 `shell=True`，但命令字符串完全由内部分支常量与清单文件名生成，不含用户可控文本。

### 4. 代码质量与稳健性 (Code Quality)

- **问题 Q1 (带标签的进度被误判为完成)**：`is_status_done()` 在关键字前缀兜底前没有剥离状态标签。`完成情况: 80%` 因以"完成"开头被判为已完成，可能让 `--check` 门禁在仍有 20% 工作时通过；反向地，`Status: Done`、`进度: 100%`、`状态: 已完成` 这类带标签的单元被漏判为未完成。
- **问题 Q2 (emoji 变体选择符导致任务行消失)**：清单正则的方括号内容只允许单个字符。`- [✅️] ...`（✅ + U+FE0F）无法匹配，整行被静默丢弃，进度分母随之缩小。

### 5. 可维护性与工程化 (Maintainability)

- **问题 M1 (Git 错误原因丢失)**：`rev-parse --is-inside-work-tree` 失败时直接返回 `is_git=False` 且不记录 stderr；控制台统一输出"不是 Git 仓库"。在 `detected dubious ownership`、缺少 git 可执行文件等场景下，用户会被误导排查错误的方向。
- **问题 M2 (空白规则未纳入门禁)**：ruff 仅启用 E4/E7/E9/F，仓库中已存在 36 处 W293（空行尾随空白），CI 无法阻止继续增长。
- **问题 M3 (CI 版本矩阵陈旧)**：`pyproject.toml` 分类器与 CI 矩阵止步于 Python 3.12；本机 3.13.5 / 3.14.5 实测 130 tests 全通过，说明兼容性声明落后于实际能力。

### 6. 测试覆盖与质量工程 (Testing & QA)

- **问题 T1 (边界分支缺少断言)**：`git_reports_ignored` 的 git 缺失/探测异常、`.gitignore` 仅含 `!` 的否定行、表格行转义非竖线字符与行尾反斜杠、链接解包后二次剥离标记、`yes/true` 状态、仅含优先级的清单项等分支均无回归测试。

---

## 三、改进方案与落地路径

### P0 级：严重阻断、安全提权与崩溃隐患

- 无 P0 级阻断项。

### P1 级：架构核心解耦与高收益性能优化

- **OPT-01: 修正带状态标签的进度判定**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：新增 `STATUS_LABEL_RE`，在判定前剥离 `Status/State/Progress/Completion/状态/进度/完成度/完成情况` 及其后的中英文冒号，只用剩余内容判定；标签本身不构成完成声明。
  - **预期收益**：`完成情况: 80%` 不再被误勾选，`Status: Done` / `进度: 100%` 可被正确统计，CI 门禁与进度百分比恢复可信。

### P2 级：功能完备性、模块重构与容错降级

- **OPT-02: 保留带 emoji 变体选择符的清单任务**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：清单正则的方括号内容后允许可选的 U+FE0F（VS16），使 `✅️` / `✔️` / `☑️` 复选框与普通 `[x]` 等价。
  - **预期收益**：从 emoji 选择器粘贴的已完成任务不再从统计中消失。

- **OPT-03: 控制台暴露 Git 不可用原因**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：`rev-parse` 失败时捕获 stderr；除 "not a git repository" 这一正常答复外写入 `git_error`。人类可读报告在 `is_git=False` 且有 `git_error` 时输出 `Git status unavailable: <detail>`。
  - **预期收益**：dubious ownership、git 缺失等真实故障可直接定位，不再伪装成普通非仓库目录。

### P3 级：工程规范、状态重构与测试加固

- **OPT-04: 启用 ruff W 规则并清理尾随空白**
  - **涉及文件**：`pyproject.toml`, `scripts/check_health.py`, `scripts/track_progress.py`, `README.md`
  - **方案**：`ruff check --select W293 --fix` 清理 36 处空行尾随空白；`[tool.ruff.lint] select` 增加 `W`；同步 README 中的规则集说明。
  - **预期收益**：空白噪声不再进入 diff，门禁可阻止其回归。

- **OPT-05: 补齐未覆盖分支的回归断言**
  - **涉及文件**：`tests/test_check_health.py`, `tests/test_track_progress.py`
  - **方案**：为 `git_reports_ignored` 无 git / 探测异常、仅 `!` 的 .gitignore 行、转义非竖线与行尾反斜杠、链接解包后的二次剥离、`yes/true` 状态、仅含优先级的清单项补充针对性用例。
  - **预期收益**：`scripts/` 覆盖率提升，异常与转义路径获得回归保护。

- **OPT-06: CI 与分类器扩展到 Python 3.13 / 3.14**
  - **涉及文件**：`.github/workflows/ci.yml`, `pyproject.toml`
  - **方案**：矩阵追加 `3.13`、`3.14`，分类器同步声明；本机已用 3.13.5 / 3.14.5 各跑通 130 tests。
  - **预期收益**：兼容性声明与当前 CPython 发行版一致，提前捕获未来版本回归。

---

## 四、实施优先级与推进清单

| 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P1** | **OPT-01** | 修正带状态标签的进度判定 | 80% 不再被判完成，门禁可信 | `scripts/track_progress.py` | [x] |
| **P2** | **OPT-02** | 保留带 emoji 变体选择符的清单任务 | 已完成任务不再消失 | `scripts/track_progress.py` | [x] |
| **P2** | **OPT-03** | 控制台暴露 Git 不可用原因 | 真实故障可直接定位 | `scripts/check_health.py` | [x] |
| **P3** | **OPT-04** | 启用 ruff W 规则并清理尾随空白 | 空白噪声不再回归 | `pyproject.toml`, `scripts/`, `README.md`, `README_zh.md` | [x] |
| **P3** | **OPT-05** | 补齐未覆盖分支的回归断言 | 异常/转义路径受保护 | `tests/` | [x] |
| **P3** | **OPT-06** | CI 与分类器扩展到 Python 3.13 / 3.14 | 版本声明与能力一致 | `.github/workflows/ci.yml`, `pyproject.toml` | [x] |
