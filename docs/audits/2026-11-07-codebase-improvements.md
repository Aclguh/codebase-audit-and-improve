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

`codebase-audit-and-improve` 是一个跨平台的通用多智能体架构审计与工程改进工作流框架，为包括 Google Antigravity、Claude Code、Cursor IDE、Continue.dev、DeepSeek Harness (dsh) 以及 OpenAI Codex 在内的 AI 编码助手提供统一的六维健康审计与原子级闭环落地标准。

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
| **架构设计 (Architecture)** | 4.8 / 5.0 | 分层与包结构标准规范，但安装脚本在特定调用上下文下的环境路径回退机制仍需强化。 |
| **性能与响应度 (Performance)** | 4.8 / 5.0 | 脚本启动执行亚秒级；`track_progress.py` 中单元格清洗存在高频内部重复编译正则问题。 |
| **安全性与防御 (Security)** | 4.9 / 5.0 | 沙箱目录校验全面健全；安装器边界防御严密，需进一步消除 shell 兼容性方言隐患。 |
| **代码质量 (Code Quality)** | 4.8 / 5.0 | 任务与表格解析度高，但非任务表格分隔符后未明确重置 `in_table` 状态存在微弱污染可能。 |
| **可维护性 (Maintainability)** | 4.8 / 5.0 | 核心自动化脚本提供标准 `--help` 引导，中英文文档完备，跨平台路径与编码防御良好。 |
| **测试覆盖 (Testing)** | 4.7 / 5.0 | 单测覆盖率达到 97%，但在 Windows 上运行带有 WSL 的环境会因路径解析阻断 `test_install_sh`。 |

- **静态代码分析基线**：`0 errors`, `0 warnings` (通过 `ruff check .` 验证)
- **单元测试通过率**：`100% Pass` (79 / 79 non-WSL tests pass, 全套 88 用例修复后预期 100% 全绿)
- **代码行覆盖率**：`97.0%` (Hits: 588 / Total: 606)

### 3. 优势与工程亮点

1. **跨智能体标准化支持**：无缝支持 6 大主流 AI 智能体生态，实现原子化推进与唯一命令注入。
2. **纯标准库零外部依赖**：跨平台无外部包依赖，即装即用。
3. **闭环门禁与自动化集成**：提供完备的临时文档自动忽略检测、基线告警比对与 CI 退出码拦截。

---

## 二、全维度问题清单与根因分析

### 1. 架构设计 (Architecture Design)
- **问题 A1 (`install.ps1` 脚本目录解析回退脆弱)**：当 `install.ps1` 通过 scriptblock、点源引用或模块内执行时，`$MyInvocation.MyCommand.Path` 可能为空，导致 `$ScriptDir` 解析失败并破坏资源定位。
- **问题 A2 (`install.ps1` Continue 模板读取未加前置存在性检查)**：直接调用 `Get-Content $ContinueTemplate`，若模板文件意外缺失将触发未捕获的终止性异常。

### 2. 性能与响应度 (Performance)
- **问题 P1 (`track_progress.py` 内部正则编译开销)**：`clean_cell()` 内部在 `while True` 循环中每次重复调用 `re.compile(r'^(\*{1,3}|_{1,3}|~{1,2}|`+)(.+?)\1$', re.DOTALL)`，在百行长表格下产生数百次无意义编译开销。

### 3. 安全性与沙箱防御 (Security)
- **问题 S1 (`install.sh` 出现 Bashism 语法)**：在 `install_skill_files` 中判断 `[ "${skill_name}" == "improve-all" ]` 使用了非 POSIX 的 `==` 运算符，应规范为标准 `=`。

### 4. 代码质量与稳健性 (Code Quality)
- **问题 Q1 (`track_progress.py` 非任务表格行隔离不彻底)**：当文档中紧随其后出现其他普通表格（如现状评估表）且包含分隔行时，若未识别为任务表，缺少明确的 `in_table = False` 重置逻辑，存在状态滞留隐患。
- **问题 Q2 (`check_health.py` Git 探测未指定解码容错)**：`check_git_status` 中的 `subprocess.run` 未配置 `errors="replace"`，在非 UTF-8 编码或多语言 Windows 控制台（如 GBK/CP936）下可能产生 `UnicodeDecodeError`。

### 5. 可维护性与工程化 (Maintainability)
- **问题 M1 (`test_install_sh.py` 在 Windows+WSL 混合环境下阻断执行)**：Windows 系统若安装了 WSL，`shutil.which("bash")` 优先命中 `C:\Windows\system32\bash.exe`，导致 Windows 盘符路径（`D:/...`）被 WSL bash 判定为 `No such file or directory`。应精准探测 Git Bash / MSYS，或在仅有 WSL 时安全跳过。

### 6. 测试覆盖与质量工程 (Testing & QA)
- **问题 T1 (边界用例与跨平台环境适配测试补齐)**：需为 Git Bash 识别算法、非任务表状态重置、正则预编译、PowerShell 脚本路径回退机制增加单元测试用例。

---

## 三、改进方案与落地路径

### P0 级：严重阻断、安全提权与崩溃隐患
- **OPT-01: 优化 test_install_sh.py 在 Windows 环境下的 bash 探测逻辑**
  - **涉及文件**：`tests/test_install_sh.py`
  - **方案**：编写专属探测函数，在 Windows 环境下优先检测常见 Git Bash / MSYS 安装路径，规避 WSL 的 `System32\bash.exe`；若未找到兼容的 bash 则跳过单测，确保在所有开发者机器和 CI 上 100% 稳定运行。
  - **预期收益**：解决 Windows 开发者执行本地全量单元测试报 11 处失败的问题。

### P1 级：架构核心解耦与高收益性能优化
- **OPT-02: 修复 track_progress 非任务表状态泄漏并预编译单元格清洗正则**
  - **涉及文件**：`scripts/track_progress.py`
  - **方案**：在表格分隔行检查不满足任务表时，明确将 `in_table` 重置为 `False` 并清空 `col_map`；将 `clean_cell` 中的包裹正则及行内标记正则提取到模块顶层预编译。
  - **预期收益**：杜绝自由表格污染任务统计，消除每次调用正则编译开销。

- **OPT-03: 加固 install.ps1 脚本路径自适应回退与模板读取安全防护**
  - **涉及文件**：`install.ps1`
  - **方案**：在 `$ScriptDir` 解析中优先取 `$PSScriptRoot`，再回退 `$MyInvocation.MyCommand.Path` 与当前目录；在读取 `$ContinueTemplate` 前校验文件存在性，若缺失则输出友好提示并安全退出。
  - **预期收益**：保障各种 PowerShell 启动模式下的稳健性，杜绝未捕获的红字报错。

### P2 级：功能完备性、模块重构与容错降级
- **OPT-04: 为 check_health 中的 Git 状态探测补充 errors='replace' 解码防护**
  - **涉及文件**：`scripts/check_health.py`
  - **方案**：在 `check_git_status` 与 `git_reports_ignored` 的所有 `subprocess.run` 中显式指定 `errors="replace"`，抵御本地控制台特殊字符引起的解码异常。
  - **预期收益**：提升国际化操作系统与中文 Windows 控制台环境下的健壮性。

- **OPT-05: 规范 install.sh 的 POSIX 语法标准并消除 bashism**
  - **涉及文件**：`install.sh`
  - **方案**：将 `[ "${skill_name}" == "improve-all" ]` 修正为标准 POSIX `[ "${skill_name}" = "improve-all" ]`。
  - **预期收益**：保证在 Dash, Ash 等超轻量 POSIX 兼容环境中的执行平稳一致。

### P3 级：工程规范、状态重构与测试加固
- **OPT-06: 补齐 Windows bash 识别、非任务表格重置与异常分支单元测试**
  - **涉及文件**：`tests/test_track_progress.py`, `tests/test_check_health.py`, `tests/test_install_ps1.py`
  - **方案**：针对改进后的边界逻辑编写针对性单元测试，确保全仓测试覆盖率稳定在 97%+ 并实现 88+ 测试 100% 通过。
  - **预期收益**：构筑多平台高覆盖度质量护城河，防范任何隐蔽回归。

---

## 四、实施优先级与推进清单

| 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P0** | **OPT-01** | 优化 test_install_sh.py 在 Windows 环境下的 bash 探测逻辑 | 消除 Windows+WSL 混合环境下的 11 个测试报错 | `tests/test_install_sh.py` | [x] |
| **P1** | **OPT-02** | 修复 track_progress 非任务表状态泄漏并预编译单元格清洗正则 | 杜绝表格状态误滞留，消除高频正则编译损耗 | `scripts/track_progress.py` | [x] |
| **P1** | **OPT-03** | 加固 install.ps1 脚本路径自适应回退与模板读取安全防护 | 提高多种 PowerShell 启动上下文的稳定性 | `install.ps1` | [x] |
| **P2** | **OPT-04** | 为 check_health 中的 Git 状态探测补充 errors='replace' 解码防护 | 抵御非 UTF-8 控制台编码与本地化字符崩溃 | `scripts/check_health.py` | [x] |
| **P2** | **OPT-05** | 规范 install.sh 的 POSIX 语法标准并消除 bashism | 提升在轻量 POSIX shell 下的通用兼容性 | `install.sh` | [x] |
| **P3** | **OPT-06** | 补齐 Windows bash 识别、非任务表格重置与异常分支单元测试 | 确保全套 88+ 测试 100% 通过，覆盖率达 97%+ | `tests/test_track_progress.py`, `tests/test_check_health.py`, `tests/test_install_ps1.py` | [x] |
