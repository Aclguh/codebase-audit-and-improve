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
| **安全性与沙箱防御 (Security)** | 4.5 / 5.0 | 凭据脱敏仅覆盖 `http(s)://`，`ssh://user:token@host` 形式的远端地址仍会原样进入 JSON 输出。 |
| **代码质量 (Code Quality)** | 4.4 / 5.0 | “100% complete”这类百分比前置的完成状态被漏判；`Pass rate 50%` 被误判为完成；`(Optional)`/`[Critical]` 被误识别为任务 ID 并从名称中剥离。 |
| **可维护性 (Maintainability)** | 4.7 / 5.0 | Dart 覆盖率命令缺少必填目录参数；Windows 上只有 POSIX `gradlew` 时会生成 cmd.exe 无法执行的 `./gradlew`。 |
| **测试覆盖 (Testing)** | 4.8 / 5.0 | `scripts/` 行覆盖率约 99%，上述边界分支均缺少回归断言。 |

- **静态代码分析基线**：`0 errors`, `0 warnings` (`python -m ruff check .`, 规则集 E4/E7/E9/F/W, ruff 0.17.3)
- **单元测试通过率**：`100% Pass` (144 / 144 tests，本机 Windows + Python 3.10.2；Linux 会跳过 PowerShell 安装器用例)
- **代码行覆盖率**：`98.8%` (Hits: 2380 / Total: 2410, 门禁 `--source=scripts` 阈值 90%)
- **跨版本验证**：CI 矩阵 Python 3.10 / 3.11 / 3.12 / 3.13 / 3.14 × Ubuntu / Windows

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

- **问题 S1 (非 HTTP 远端地址凭据泄露)**：`sanitize_remote_url()` 的前缀正则固定为 `https?://`。`ssh://user:token@host/repo.git`、`git+ssh://...` 等远端地址中的密码/令牌不会被替换，会原样写入 `check_health.py --json` 的 `remote_origin` 字段，进而流入 agent 上下文或日志。

### 4. 代码质量与稳健性 (Code Quality)

- **问题 Q1 (百分比前置的完成状态被漏判)**：`is_status_done()` 只识别“关键字 + 百分比”（`Done 100%`）与裸比例（`100%`），`100% complete` / `100% 完成` / `100% done` 这类常见写法返回未完成。自动生成的路线图若采用该写法，CI 门禁会永远停在 pending。
- **问题 Q2 (通过率被当作完成声明)**：`Pass rate 50%` 命中英文关键字前缀兜底（`pass` + 词边界），被判定为完成，与实际进度相反。
- **问题 Q3 (括号标签被误识别为任务 ID)**：清单解析中 `is_bracketed` 只判断“是否以方括号/圆括号包裹”，不校验内容形态。`- [ ] (Optional) Add docs` 会得到任务 ID `OPTIONAL`、名称 `Add docs`，`- [ ] [Critical] Fix login` 同理；任务标识被污染且名称丢失前缀。
- **问题 Q4 (Dart 覆盖率命令缺参数)**：纯 Dart 项目的 `coverage_cmd` 生成为 `dart test --coverage`，而 `package:test` 的 `--coverage` 是必填目录参数的选项，`--run-baseline` 等场景会直接报错。
- **问题 Q5 (Windows 上的 Gradle 包装器回退不可执行)**：当仓库只有 POSIX `gradlew` 而没有 `gradlew.bat` 时，Windows 分支仍生成 `./gradlew ...`，cmd.exe 无法执行。Maven 分支已正确处理同类问题。

### 5. 可维护性与工程化 (Maintainability)

- **问题 M1 (`.gitignore` 回退匹配不支持 `**/`)**：`git check-ignore` 不可用时（非 Git 目录、缺少 git），回退的 `fnmatch` 匹配把 `**/IMPROVEMENTS.md` 当作普通通配符，无法匹配根目录文件，导致已正确配置的保护被报告为缺失。

### 6. 测试覆盖与质量工程 (Testing & QA)

- **问题 T1 (边界分支缺少断言)**：上述 Q1–Q5、S1、M1 均无回归测试，修复后需同步补齐针对性用例。

---

## 三、改进方案与落地路径

### P0 级：严重阻断、安全提权与崩溃隐患

- 无 P0 级阻断项。

### P1 级：架构核心解耦与高收益性能优化

- **OPT-01: 识别百分比前置的完成状态**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：裸比例正则允许尾随完成关键字（`100% complete`、`100% 完成`、`5/5 done`），仍按数值是否达到 100% 判定。
  - **预期收益**：常见写法不再导致 CI 门禁永久 pending。

- **OPT-02: 修正清单任务 ID 的括号标签误判**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：括号包裹的候选 ID 只有在“无小写字母或含数字”（`OPT-05`、`fix-12`）时才接受，`(Optional)`、`[Critical]` 保留在任务名称中。
  - **预期收益**：任务标识与名称不再被普通英文标签污染。

### P2 级：功能完备性、模块重构与容错降级

- **OPT-03: 脱敏任意协议的远端地址凭据**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：凭据前缀正则从 `https?://` 扩展为任意 `scheme://`，保留 `git@host:path` 这类 scp 语法不变。
  - **预期收益**：`ssh://` 等地址中的令牌不再出现在 JSON 输出与日志中。

- **OPT-04: 修正通过率状态误判**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：新增 `Pass/Success/Completion rate N%` 比例识别，按数值判定是否达到 100%，不再落入关键字前缀兜底。
  - **预期收益**：`Pass rate 50%` 不再被当作已完成。

- **OPT-05: 修正 Dart 覆盖率命令**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：纯 Dart 项目的覆盖率命令改为 `dart test --coverage=coverage`。
  - **预期收益**：`--run-baseline` / 审计流程可直接执行覆盖率命令。

### P3 级：工程规范、状态重构与测试加固

- **OPT-06: Windows Gradle 包装器回退与 `**/` 忽略规则**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：Windows 且无 `gradlew.bat` 时回退到 `gradle`；`check_gitignore` 回退匹配支持剥离 `**/` 前缀。两项均补测试。
  - **预期收益**：跨平台命令可执行，非 Git 目录下的忽略判定与 Git 语义一致。

---

## 四、实施优先级与推进清单

| 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P1** | **OPT-01** | 识别百分比前置的完成状态 | 门禁不再永久 pending | `scripts/track_progress.py` | [x] |
| **P1** | **OPT-02** | 修正清单任务 ID 的括号标签误判 | ID 与名称不再被污染 | `scripts/track_progress.py` | [x] |
| **P2** | **OPT-03** | 脱敏任意协议的远端地址凭据 | 避免令牌进入 JSON/日志 | `scripts/check_health.py` | [x] |
| **P2** | **OPT-04** | 修正通过率状态误判 | 50% 通过率不再算完成 | `scripts/track_progress.py` | [x] |
| **P2** | **OPT-05** | 修正 Dart 覆盖率命令 | 覆盖率命令可直接执行 | `scripts/check_health.py` | [x] |
| **P3** | **OPT-06** | Windows Gradle 回退与 `**/` 忽略规则 | 跨平台命令与忽略判定正确 | `scripts/check_health.py` | [x] |
