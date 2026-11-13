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

`codebase-audit-and-improve` 是面向多家 AI 编程助手的跨平台代码库审计与改进工作流框架。核心自动化仅由两个零依赖标准库脚本承担，安装器负责分发技能与命令模板。

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
| **架构设计 (Architecture)** | 4.8 / 5.0 | 双脚本职责清晰、无循环依赖；Cargo 工作区判定基于字符串包含，注释中的 `[workspace]` 会误报。 |
| **性能与响应度 (Performance)** | 4.9 / 5.0 | 线性单遍扫描、正则全部预编译；Python 根目录清单选取存在重复 glob 与非确定性。 |
| **安全性与沙箱防御 (Security)** | 4.9 / 5.0 | 凭据脱敏、安装路径白名单、git 状态失败关闭均就位；本轮未发现新的安全缺口。 |
| **代码质量 (Code Quality)** | 4.6 / 5.0 | 静态分析 0 告警；带 BOM 的 `package.json` 被静默忽略，带连字符的技术名词被误判为任务 ID。 |
| **可维护性 (Maintainability)** | 4.6 / 5.0 | 脚本与文档高度一致；Swift 检测未写入 README，受保护分支清单在四处文档中与实现不一致。 |
| **测试覆盖 (Testing)** | 4.8 / 5.0 | `scripts/` 行覆盖率 97.3%，需为上述边界补齐回归断言。 |

- **静态代码分析基线**：`0 errors`, `0 warnings` (`ruff check .` 全绿)
- **单元测试通过率**：`100% Pass` (119 tests, 7 skipped on non-Windows hosts)
- **代码行覆盖率**：`97.3%` (Hits: 679 / Total: 698, CI gate `--source=scripts`, threshold 90%)

### 3. 优势与工程亮点

1. **纯标准库零外部依赖**：两个脚本在任意干净 Python 3.10+ 环境中即装即用。
2. **Fail-closed 安全护栏**：git 状态无法核实时按脏树处理，安装路径限定在工作区与 HOME 之内，remote URL 自动脱敏。
3. **成熟的 Markdown 解析**：表格/清单双通道解析、代码围栏跳过、转义竖线、进度百分比与中英文状态词均已覆盖并有回归测试。

---

## 二、全维度问题清单与根因分析

### 1. 架构设计 (Architecture Design)
- **问题 A1 (Cargo 工作区误报)**：`detect_monorepo()` 仅检查 `"[workspace]" in Cargo.toml 内容`，注释或字符串中出现的该片段（如 `# [workspace]`）会被误判为 Cargo 工作区；同时未把 `[workspace.package]` / `[workspace.dependencies]` 等合法工作区子表纳入判定。

### 2. 性能与响应度 (Performance)
- **问题 P1 (重复且非确定性的 glob)**：`detect_stack()` 对根目录 `*.py` 连续调用两次 `glob.glob`，且直接取首个结果作为清单名，结果依赖文件系统枚举顺序，不同机器上 JSON 输出可能不一致。

### 3. 安全性与沙箱防御 (Security)
- 无新增问题：凭据脱敏、路径白名单、失败关闭策略均保持有效。

### 4. 代码质量与稳健性 (Code Quality)
- **问题 Q1 (带 BOM 的清单文件被静默忽略)**：`package.json` 以 `encoding="utf-8"` 读取，Windows 编辑器常写入 UTF-8 BOM，`json.load` 直接抛错并被吞掉，导致 Node 脚本与 workspace 检测双双失效且无任何提示。
- **问题 Q2 (连字符技术名词被误判为任务 ID)**：清单解析的 ID 启发式 `[A-Za-z]+[-_]\d+` 会把 `utf-8 support`、`sha-256 hashing` 之类任务名开头的技术名词当作任务 ID 剥离，导致任务名被截断、进度报告失真。
- **问题 Q3 (优先级分组排序错误)**：进度报告使用 `sorted(set(priorities))` 字母序，`GENERAL` 会排在 `P0` 之前，未标优先级的任务出现在阻断项上方，弱化了 P0 的警示作用。

### 5. 可维护性与工程化 (Maintainability)
- **问题 M1 (文档与实现漂移)**：`detect_stack()` 支持 Swift (SPM)，但 README / README_zh 的能力清单未提及；受保护分支实现包含 `trunk`、`prod`、`production` 及 `release/` 等前缀，而 README、两份 SKILL.md 与 ci-monitoring.md 各自给出的清单互不相同；README 测试目录树缺少 `test_python_sources.py`。

### 6. 测试覆盖与质量工程 (Testing & QA)
- **问题 T1 (新增边界的回归断言缺失)**：BOM 清单、注释中的 Cargo 工作区、连字符技术名词、优先级排序、确定性清单选取均缺少专门的回归测试。

---

## 三、改进方案与落地路径

### P0 级：严重阻断、安全提权与崩溃隐患
- 无 P0 级阻断项。

### P1 级：架构核心解耦与高收益性能优化
- **OPT-01: 容错读取带 BOM 的 JSON 清单**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：`package.json` 的读取统一改为 `encoding="utf-8-sig"`，并在解析后显式校验顶层为对象，避免依赖宽泛异常吞没真实错误。
  - **预期收益**：Windows 环境下保存的清单不再被静默跳过，Node 脚本与 workspace 检测恢复可用。

### P2 级：功能完备性、模块重构与容错降级
- **OPT-02: 精确识别 Cargo 工作区子表**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：逐行剥离 TOML 注释后匹配 `[workspace]` 或 `[workspace.*]` 表头，替代子串包含判断。
  - **预期收益**：消除注释与字符串导致的误报，同时覆盖 `[workspace.package]` 等合法写法。

- **OPT-03: 修正清单任务 ID 的连字符误判**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：通用 `word-123` 形式仅在字母段全大写（或属于标准前缀 / 方括号 / `#123` 形式）时才视为任务 ID。
  - **预期收益**：`utf-8`、`sha-256` 等技术名词不再吞掉任务名，进度统计恢复准确。

- **OPT-04: 同步 Swift 支持与受保护分支文档**
  - **涉及文件**：`README.md`, `README_zh.md`, `SKILL.md`, `skills/improve/SKILL.md`, `skills/improve-all/SKILL.md`, `references/ci-monitoring.md`, `tests/test_repo_docs.py`
  - **方案**：能力清单补充 Swift (SPM)；受保护分支统一表述为 `main` / `master` / `trunk` / `release*` / `prod*`；README 目录树补充 `test_python_sources.py`；新增文档一致性断言。
  - **预期收益**：文档与实现一致，避免贡献者依据过时清单做分支决策。

### P3 级：工程规范、状态重构与测试加固
- **OPT-05: 修复优先级分组排序**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：按 `P0 < P1 < … < Pn` 数值排序，`GENERAL` 等无优先级分组置于末尾。
  - **预期收益**：阻断项始终出现在报告首位，CI 输出可读性提升。

- **OPT-06: 确定性选取 Python 根目录清单**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：单次 `sorted(glob.glob(...))` 复用结果，按字典序选取首个根级 `.py` 文件。
  - **预期收益**：跨机器、跨文件系统的 JSON 输出稳定可复现。

---

## 四、实施优先级与推进清单

| 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P1** | **OPT-01** | 容错读取带 BOM 的 JSON 清单 | 恢复 Windows 清单检测 | `scripts/check_health.py` | [x] |
| **P2** | **OPT-02** | 精确识别 Cargo 工作区子表 | 消除注释误报并覆盖子表 | `scripts/check_health.py` | [x] |
| **P2** | **OPT-03** | 修正任务 ID 的连字符误判 | 保留完整任务名 | `scripts/track_progress.py` | [x] |
| **P2** | **OPT-04** | 同步 Swift 与受保护分支文档 | 文档与实现一致 | `README.md`, `README_zh.md`, `SKILL.md`, `skills/`, `references/ci-monitoring.md` | [x] |
| **P3** | **OPT-05** | 修复优先级分组排序 | P0 始终置顶 | `scripts/track_progress.py` | [x] |
| **P3** | **OPT-06** | 确定性选取 Python 根清单 | JSON 输出可复现 | `scripts/check_health.py` | [x] |
