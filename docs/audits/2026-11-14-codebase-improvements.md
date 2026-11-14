# Codebase Audit & Improve: Architecture & Code Quality Assessment (IMPROVEMENTS.md)

> **Document Nature**: Temporary project health audit and technical improvement tracking document (excluded in `.gitignore`).
> This document coordinates step-by-step refactoring and quality hardening. Complete each task with an atomic Git commit.
> Upon full completion, this document can be archived to `docs/audits/YYYY-MM-DD-codebase-improvements.md` (recommended) or deleted.

---

## 目录

- [一、项目现状与整体架构评估](#一项目现状与整体架构评估)
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
| **架构设计 (Architecture)** | 4.9 / 5.0 | 双脚本职责清晰、零循环依赖；仅探测段注释编号重复，属文档噪声。 |
| **性能与响应度 (Performance)** | 5.0 / 5.0 | 线性单遍扫描、正则预编译，无可感知热点。 |
| **安全性与沙箱防御 (Security)** | 4.9 / 5.0 | 凭据脱敏、安装路径白名单、git 状态失败关闭均有效；本轮未发现新缺口。 |
| **代码质量 (Code Quality)** | 4.5 / 5.0 | 静态分析零告警；阻塞标记 `[!]` 与带括号百分比的完成状态被解析器误读。 |
| **可维护性 (Maintainability)** | 4.6 / 5.0 | 文档与实现总体一致；`--fix-gitignore` 失败原因仅在 JSON 中可见，控制台误导用户重试。 |
| **测试覆盖 (Testing)** | 4.8 / 5.0 | `scripts/` 行覆盖率 97.3%，需为上述解析边界补齐回归断言。 |

- **静态代码分析基线**：`0 errors`, `0 warnings` (`python -m ruff check .` 全绿)
- **单元测试通过率**：`100% Pass` (125 tests, 118 executed, 7 skipped on non-Windows hosts)
- **代码行覆盖率**：`97.3%` (Hits: 691 / Total: 710, CI gate `--source=scripts`, threshold 90%)

### 3. 优势与工程亮点

1. **纯标准库零外部依赖**：两个脚本在任意干净 Python 3.10+ 环境中即装即用。
2. **Fail-closed 安全护栏**：git 状态无法核实时按脏树处理，安装路径限定在工作区与 HOME 之内，remote URL 自动脱敏。
3. **成熟的 Markdown 解析**：表格/清单双通道解析、代码围栏跳过、转义竖线、进度百分比与中英文状态词均已覆盖并有回归测试。

---

## 二、全维度问题清单与根因分析

### 1. 架构设计 (Architecture Design)
- **问题 A1 (注释编号重复)**：`detect_stack()` 中 Gradle 与 .NET 两段都以 `# 7.` 开头，后续编号随之错位，降低源码可读性。

### 2. 性能与响应度 (Performance)
- **问题 P1 (清单选取不确定)**：`.NET` 检测使用两次未排序的 `glob.glob` 并直接取首项，多个 `.csproj` 时清单名随文件系统枚举顺序变化，JSON 输出无法复现（与上一轮已修复的 Python 根清单问题同类）。

### 3. 安全性与沙箱防御 (Security)
- 无新增问题：凭据脱敏、安装路径白名单、失败关闭策略均保持有效。

### 4. 代码质量与稳健性 (Code Quality)
- **问题 Q1 (阻塞标记被丢弃)**：`references/execution-loop.md` 要求以 `[!] Blocked by ...` 标注阻塞任务，但清单正则只接受 `[ ]`/`[x]` 等完成标记，`[!]`/`[~]`/`[-]` 行被整行跳过，阻塞任务从总数中消失，`--check` 门禁可能在仍有阻塞项时通过。
- **问题 Q2 (完成状态表头漏识别)**：表头 `Completion`、`完成情况` 不在状态关键词内。若表中同时有任务名与 ID，则整表任务被当作未完成且永不翻转；若表只有 `Task | Completion` 两列，则整张表被丢弃并报 "No tracked tasks found"。
- **问题 Q3 (括号百分比误判为已完成)**：进度判定正则只接受紧邻关键字的百分比，`已完成 (80%)`、`Completed (80%)`、`已完成（80%）` 均被 `startswith("已完成"/"completed")` 兜底判为完成，进度 80% 的任务被错误勾选。

### 5. 可维护性与工程化 (Maintainability)
- **问题 M1 (失败原因不可见)**：`--fix-gitignore` 追加失败或追加后仍未被忽略时，详细信息只写入 JSON 的 `gitignore.message`；控制台仍输出 "Run --fix-gitignore or append manually"，引导用户重复刚失败的命令。

### 6. 测试覆盖与质量工程 (Testing & QA)
- **问题 T1 (解析边界缺少回归断言)**：上述阻塞标记、状态表头同义词、括号百分比、.NET 多清单确定性、控制台失败提示均无专门测试。

---

## 三、改进方案与落地路径

### P0 级：严重阻断、安全提权与崩溃隐患
- 无 P0 级阻断项。

### P1 级：架构核心解耦与高收益性能优化
- **OPT-01: 保留阻塞/进行中的清单任务**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：清单正则接受 `!`、`~`、`-`、`/` 等非完成标记，按“未完成”计入统计；为 `[!] Blocked by ...` 添加回归断言并验证 `--check` 以退出码 1 结束。
  - **预期收益**：阻塞任务不再从进度报告中消失，CI 门禁不会在仍有阻塞项时误判完成。

### P2 级：功能完备性、模块重构与容错降级
- **OPT-02: 识别 Completion / 完成情况 状态表头**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：状态关键词补充 `completion` 与 `完成情况`（含仅 `Task | Completion` 两列表格），确保完成行被正确统计。
  - **预期收益**：中英文状态表头不再导致已完成任务永久显示为待办或整表被丢弃。

- **OPT-03: 修正括号百分比进度判定**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：进度正则允许百分比/分数被圆括号、方括号（含全角括号）包裹；`< 100%` 一律视为未完成，`100%` 与 `5/5` 仍视为完成。
  - **预期收益**：`已完成 (80%)` 不再被误勾选，进度统计与实际状态一致。

### P3 级：工程规范、状态重构与测试加固
- **OPT-04: 确定性选取 .NET 清单**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：分别对 `*.csproj` 与 `*.sln` 排序后拼接（保持 csproj 优先），并断言多个 csproj 时选择字典序首项。
  - **预期收益**：跨机器 JSON 输出稳定可复现。

- **OPT-05: 控制台展示 gitignore 修复失败原因**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：人类可读模式在 `--fix-gitignore` 未成功时输出 `gitignore_msg` 详情，而非仅给出重复执行的建议。
  - **预期收益**：权限、只读文件系统等失败原因可直接定位。

- **OPT-06: 修正探测段注释编号**
  - **涉及文件**：`scripts/check_health.py`
  - **方案**：将重复的 `# 7.` 及后续段号改为连续编号（.NET 起顺延）。
  - **预期收益**：源码结构与注释一致，便于按编号引用。

---

## 四、实施优先级与推进清单

| 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P1** | **OPT-01** | 保留阻塞/进行中的清单任务 | 阻塞项不再消失，门禁可信 | `scripts/track_progress.py` | [x] |
| **P2** | **OPT-02** | 识别 Completion / 完成情况 表头 | 完成状态统计准确 | `scripts/track_progress.py` | [x] |
| **P2** | **OPT-03** | 修正括号百分比进度判定 | 80% 不再被当作完成 | `scripts/track_progress.py` | [x] |
| **P3** | **OPT-04** | 确定性选取 .NET 清单 | JSON 输出可复现 | `scripts/check_health.py` | [x] |
| **P3** | **OPT-05** | 控制台展示 gitignore 修复失败原因 | 失败原因可直接定位 | `scripts/check_health.py` | [x] |
| **P3** | **OPT-06** | 修正探测段注释编号 | 注释与结构一致 | `scripts/check_health.py` | [x] |
