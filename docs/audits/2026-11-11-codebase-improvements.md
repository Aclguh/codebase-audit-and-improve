# Codebase Audit & Improve: Architecture & Code Quality Assessment (IMPROVEMENTS.md)

> **Document Nature**: Temporary project health audit and technical improvement tracking document (excluded in `.gitignore`).
> This document coordinates step-by-step refactoring and quality hardening. Complete each task with an atomic Git commit.
> Upon full completion, this document can be archived to `docs/audits/YYYY-MM-DD-codebase-improvements.md` (recommended) or deleted.

---

## 一、项目现状与整体架构评估

### 1. 架构定位与模块拓扑

`codebase-audit-and-improve` 是一个跨平台的多智能体代码库审计与改进工作流框架，为 Antigravity、Claude Code、Cursor、Continue.dev、DeepSeek Harness (dsh) 与 OpenAI Codex 提供统一的六维健康审计与原子化落地标准。

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
| **架构设计 (Architecture)** | 4.8 / 5.0 | 双脚本职责清晰、无循环依赖；安装器与文档分层合理。 |
| **性能与响应度 (Performance)** | 4.9 / 5.0 | 正则已预编译，路线图为单次线性扫描，全量扫描在秒级完成。 |
| **安全性与防御 (Security)** | 4.7 / 5.0 | 路径沙箱、根目录拒绝、Git 状态失败关闭均已就位。 |
| **代码质量 (Code Quality)** | 4.2 / 5.0 | 静态分析零告警，但清单解析存在非映射 `scripts` 导致的未捕获崩溃。 |
| **可维护性 (Maintainability)** | 4.4 / 5.0 | 文档完备，但测试源码存在 Python 3.12+ 非法转义告警，缺少全仓编译门禁。 |
| **测试覆盖 (Testing)** | 4.6 / 5.0 | 行覆盖率 97%，但上述崩溃与解析兼容性边界尚无回归断言。 |

- **静态代码分析基线**：`0 errors`, `0 warnings` (`ruff check .` 全绿)
- **单元测试通过率**：`100% Pass` (107 / 107 tests, 7 skipped)
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

### 4. 代码质量与稳健性 (Code Quality)
- **问题 Q1 (合法 package.json 导致健康检查崩溃)**：`package.json` 中 `"scripts": null`（或数字）是合法 JSON，`parse_package_json` 仅用 `.get("scripts", {})` 取值，后续 `"lint" in scripts` 对 `None`/`int` 迭代抛出 `TypeError`，`check_health.py --json` 直接回溯退出，预检阶段中断。
- **问题 Q2 (紧凑任务表名称列被状态单元格污染)**：任务的名称列缺失时，解析器无条件回退到第三列（`raw_cells[2]`）；对 `| Priority | ID | Status |` 这类紧凑表，任务名会变成 `[ ]` 之类的状态值。
- **问题 Q3 (CommonMark 有序清单被静默忽略)**：checklist 仅识别 `1.` 形式，合法 Markdown 的 `1)` 形式完全不被解析，路线图会被判定为 0 个任务并使 `--check` 门禁以退出码 2 失败。

### 5. 可维护性与工程化 (Maintainability)
- **问题 M1 (Python 3.12+ 非法转义告警)**：`tests/test_install_sh.py` 的文档字符串与 Windows 默认路径包含 `\W`、`\P` 等非法转义，Python 3.12 起每次编译都会输出 `SyntaxWarning`，未来版本将升级为错误；CI 的 `compileall -q` 与 ruff E4/E7/E9/F 规则集均未拦截。
- **问题 M2 (缺少全仓编译门禁)**：没有测试保证所有 Python 源码在“告警即错误”模式下可编译，同类问题可能再次引入。

### 6. 测试覆盖与质量工程 (Testing & QA)
- **问题 T1 (崩溃与解析边界无回归断言)**：非映射 `scripts`、名称列缺失的紧凑表、`1)` 清单与裸比例状态（`100%`、`5/5`）均无测试覆盖。

---

## 三、改进方案与落地路径

### P0 级：严重阻断、安全提权与崩溃隐患
- 无 P0 阻断项。

### P1 级：架构核心解耦与高收益性能优化
- **OPT-01: 修复非映射 `scripts` 导致的预检崩溃**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：仅当 `scripts` 为 `dict` 时使用，否则回退为空映射；补充 `null`、数字与数组三种回归断言。
  - **预期收益**：合法但非典型的 `package.json` 不再中断健康检查。

### P2 级：功能完备性、模块重构与容错降级
- **OPT-02: 消除测试源码非法转义并增加全仓编译门禁**
  - **涉及文件**：`tests/test_install_sh.py`, `tests/test_repo_docs.py`
  - **方案**：文档字符串改用原始字符串，Windows 默认路径改为转义反斜杠；新增“所有 `.py` 在 `SyntaxWarning` 视为错误时可编译”的仓库级测试。
  - **预期收益**：测试输出不再出现告警，并在 CI 中提前拦截未来 Python 版本的兼容性问题。

- **OPT-03: 修正紧凑任务表名称回退逻辑**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：名称列缺失时选择第一个未被 priority/id/status/files/benefit 占用的列；无可选列时回退为任务 ID，而不是状态单元格。
  - **预期收益**：进度报告中的任务名称准确可读。

- **OPT-04: 支持 `1)` 形式的 CommonMark 有序清单**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：checklist 正则同时接受 `.` 与 `)` 作为有序列表标记，保持现有 `-`/`*`/`+` 行为不变。
  - **预期收益**：合法 Markdown 路线图不再被解析为 0 个任务。

### P3 级：工程规范、状态重构与测试加固
- **OPT-05: 识别裸比例完成状态**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：`100%`、`5/5` 等裸比例判定为完成，`99%`、`3/5`、`0/0` 仍为未完成；保留现有“关键词 + 比例”的语义。
  - **预期收益**：以百分比/分数记录状态的路线图不再被误报为待办。

---

## 四、实施优先级与推进清单

| 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P1** | **OPT-01** | 修复非映射 `scripts` 导致的预检崩溃 | 预检对合法 package.json 不再崩溃 | `scripts/check_health.py`, `tests/test_check_health.py` | [x] |
| **P2** | **OPT-02** | 消除测试源码非法转义并增加全仓编译门禁 | 消除 Python 3.12+ 告警并前移拦截 | `tests/test_install_sh.py`, `tests/test_python_sources.py` | [x] |
| **P2** | **OPT-03** | 修正紧凑任务表名称回退逻辑 | 进度报告任务名称准确 | `scripts/track_progress.py`, `tests/test_track_progress.py` | [x] |
| **P2** | **OPT-04** | 支持 `1)` 形式的 CommonMark 有序清单 | 合法路线图不再解析为 0 任务 | `scripts/track_progress.py`, `tests/test_track_progress.py` | [x] |
| **P3** | **OPT-05** | 识别裸比例完成状态 | 百分比/分数状态不再误报待办 | `scripts/track_progress.py`, `tests/test_track_progress.py` | [x] |
