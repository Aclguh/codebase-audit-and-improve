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
- [三、改进方案与落地路径](#三改进方案与落地路径)
- [四、实施优先级与推进清单](#四实施优先级与推进清单)

---

## 一、项目现状与整体架构评估

### 1. 架构定位与模块拓扑

```
┌─────────────────────────────────────────────────────────────┐
│                   Agent Skill Layer (SKILL.md)              │
│        /improve (audit)  ·  /improve-all (full loop)        │
└──────────────────────────────┬──────────────────────────────┘
                               │ references/ (rules, templates)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLI Helper Layer (scripts/)              │
│   check_health.py (stack/git/gitignore)                     │
│   track_progress.py (IMPROVEMENTS.md parser + CI gate)      │
└──────────────────────────────┬──────────────────────────────┘
                               │ shell / PowerShell installers
                               ▼
┌─────────────────────────────────────────────────────────────┐
│           Integration Layer (install.sh / install.ps1)      │
│     Claude · Codex · Cursor · Continue · DeepSeek · Gemini  │
└─────────────────────────────────────────────────────────────┘
```

### 2. 核心技术指标与现状概览

| 评估维度 | 评级 / 得分 (满分 5.0) | 核心现状与风险分析 |
| :--- | :---: | :--- |
| **架构设计 (Architecture)** | 4.3 / 5.0 | 三层职责清晰，脚本内聚；`detect_stack` 较长但分支独立、易读。 |
| **性能与响应度 (Performance)** | 4.8 / 5.0 | 纯 CLI 场景，子进程均设超时；无主线程/流式瓶颈。 |
| **安全性与防御 (Security)** | 4.0 / 5.0 | `.gitignore` 已用 `git check-ignore` 权威判定；但 `git status` 探测失败时会回退为“干净”，存在误放行风险。 |
| **代码质量 (Code Quality)** | 4.0 / 5.0 | 主要流程稳健，但清单优先级解析会误伤标识符，进度型状态会被误判为完成。 |
| **可维护性 (Maintainability)** | 4.5 / 5.0 | 双语文档、CI 门禁、安装脚本校验齐备；CLI 对未知参数仍静默忽略。 |
| **测试覆盖 (Testing)** | 4.5 / 5.0 | 行覆盖率 98%，但上述解析边界与失败路径缺少回归断言。 |

- **静态代码分析基线**：`python -m ruff check .` → `0 errors`, `0 warnings`。
- **单元测试通过率**：`100% Pass` (62 / 62 tests, `python -m unittest discover -s tests`)。
- **代码行覆盖率**：`98%` (Hits: 1333 / Total: 1362，`coverage report -m`)。
- **本地环境**：Python 3.10.2；CI 矩阵 Ubuntu/Windows × Python 3.10/3.11/3.12。

### 3. 优势与工程亮点

- 两套 CLI 工具均具备 `--help`、结构化 JSON 输出与明确退出码，便于 Agent 集成。
- 安装脚本参数校验、根目录防护、路径穿越防护与安装冒烟测试均已落地。
- 解析器已支持围栏代码块跳过、列重排、别名表头与多种完成状态表达。
- 文档体系完整（README 双语、SKILL、references、templates、历史 audits）。

---

## 二、全维度问题清单与根因分析

### 1. 架构设计 (Architecture Design)
- 未发现职责失衡或跨层调用；两个脚本各自独立，无循环依赖。

### 2. 性能与响应度 (Performance)
- 未发现阻断性问题；`run_baseline_command` 已设置 120s 超时并捕获超时异常。

### 3. 安全性与沙箱防御 (Security)
- **问题 S1 (git 状态失败即放行)**：`check_git_status` 的 `is_clean` 默认 `True`，且 `git status` 子命令使用 `check=True`；一旦命令失败（索引锁、权限、损坏仓库），异常被统一捕获后仍返回“干净”，前置安全检查会误放行。

### 4. 代码质量与稳健性 (Code Quality)
- **问题 Q1 (清单优先级误伤标识符)**：优先级正则 `\b(P\d+)(?=[^\d]|$)` 会把 `P2P`、`P3 processor` 中的 `P2/P3` 当作优先级并删除；`[P0级]` 只移除 `P0`，残留 `级]` 导致任务 ID 丢失、名称被污染。
- **问题 Q2 (进度型状态被误判完成)**：`is_status_done` 以“完成/通过”开头即判定完成，`完成 80%`、`完成度 50%`、`通过率 50%`、`Completed 3/5` 都会被计为已完成，`--check` 门禁会提前放行。
- **问题 Q3 (托管运行器命令拼接错误)**：poetry/uv/pdm 环境下 `runner="poetry run"`，但 `unittest`/`compileall` 被拼成 `poetry run unittest`、`poetry run compileall`，控制台并不存在这些可执行文件；应经 `python -m` 调用。
- **问题 Q4 (下划线被误删)**：`clean_cell` 无条件删除所有 `*`、`` ` ``、`_`、`~`，任务名 `parse_package_json` 会变成 `parsepackagejson`。

### 5. 可维护性与工程化 (Maintainability)
- **问题 M1 (未知 CLI 参数静默忽略)**：`check_health.py --jsn`、`track_progress.py --chek` 均会被静默忽略并按默认模式执行，Agent 集成时容易得到与预期不符的结果且退出码为 0。

### 6. 测试覆盖与质量工程 (Testing & QA)
- **问题 T1 (边界回归缺失)**：上述解析与失败路径均无测试断言。
- **问题 T2 (CI 语法检查遗漏)**：CI 的 `py_compile` 列表未包含 `tests/test_install_sh.py`。

---

## 三、改进方案与落地路径

### P1 级：架构核心正确性与门禁可信度

- **OPT-01: 修复清单优先级解析误伤标识符**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：优先级 token 改为“前后不得紧邻字母/数字”的严格匹配；移除优先级时一并消费 `级` 限定词与包裹括号，确保 `[P0级] OPT-07` 正确得到 ID `OPT-07`，`P2P`/`P3 processor` 不再被误判。
  - **预期收益**：任务 ID 与名称不再被破坏，进度统计与提交追踪保持准确。

- **OPT-02: 进度型状态不再计为完成**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：在完成词后紧跟百分比或分数（如 `完成 80%`、`Completed 3/5`）时按进度值判定，未达 100% 一律视为未完成；`Done (PR #2)` 等普通描述保持原判定。
  - **预期收益**：`--check` CI 门禁不会因部分完成而提前放行。

- **OPT-03: 修复 poetry/uv/pdm 的 unittest 与 compileall 命令**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：为托管运行器构造 `poetry run python -m ...` / `uv run python -m ...` / `pdm run python -m ...`，保留 `python -m` 直连模式不变。
  - **预期收益**：托管虚拟环境下的基线测试与语法检查命令可直接执行。

### P2 级：安全失败语义与 CLI 健壮性

- **OPT-04: git 状态探测失败时安全侧失败**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：`git status` 返回非 0 时记录 `status_error` 并置 `is_clean = False`；控制台明确提示“状态未知”，而非显示干净。
  - **预期收益**：前置安全检查不会在 git 异常时误放行未提交改动。

- **OPT-05: CLI 未知参数严格拒绝**
  - **涉及文件**：`scripts/check_health.py`, `scripts/track_progress.py`, `tests/test_check_health.py`, `tests/test_track_progress.py`
  - **方案**：显式维护合法参数集合；未知选项或多余位置参数输出明确错误并以退出码 2 结束。
  - **预期收益**：拼写错误不再静默产生错误模式的结果，Agent 调用更可预期。

### P3 级：工程规范与数据保真

- **OPT-06: `clean_cell` 保留标识符下划线**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：仅剥离成对/包裹式 Markdown 标记（`**x**`、`*x*`、`_x_`、`~~x~~`、`` `x` ``）以及行内代码/粗体，不再删除词内 `_`。
  - **预期收益**：`parse_package_json` 等名称与 `OPT_01` 类 ID 保持原样。

- **OPT-07: CI 语法检查覆盖安装测试**
  - **涉及文件**：`.github/workflows/ci.yml`
  - **方案**：将 `tests/test_install_sh.py` 加入 `py_compile` 步骤。
  - **预期收益**：安装集成测试的语法回归在 CI 中可见。

---

## 四、实施优先级与推进清单

| 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P1** | **OPT-01** | 修复清单优先级解析误伤标识符 | 任务 ID/名称不再被破坏 | `scripts/track_progress.py`, `tests/test_track_progress.py` | [x] |
| **P1** | **OPT-02** | 进度型状态不再计为完成 | CI 门禁不提前放行 | `scripts/track_progress.py`, `tests/test_track_progress.py` | [x] |
| **P1** | **OPT-03** | 修复托管运行器的 unittest/compileall 命令 | 基线命令可直接执行 | `scripts/check_health.py`, `tests/test_check_health.py` | [x] |
| **P2** | **OPT-04** | git 状态失败时安全侧失败 | 前置检查不误放行 | `scripts/check_health.py`, `tests/test_check_health.py` | [x] |
| **P2** | **OPT-05** | CLI 未知参数严格拒绝 | 拼写错误显式失败 | `scripts/check_health.py`, `scripts/track_progress.py`, `tests/` | [x] |
| **P3** | **OPT-06** | `clean_cell` 保留标识符下划线 | 任务名称/ID 保真 | `scripts/track_progress.py`, `tests/test_track_progress.py` | [x] |
| **P3** | **OPT-07** | CI 语法检查覆盖安装测试 | 安装测试语法回归可见 | `.github/workflows/ci.yml` | [x] |
