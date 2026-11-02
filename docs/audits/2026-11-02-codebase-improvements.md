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
| **架构设计 (Architecture)** | 4.6 / 5.0 | 分层与接口清晰，但 `scripts/__init__.py` 未挂载子模块，且 `pyproject.toml` 缺少包过滤规则导致 `tests/` 被意外打包入分发包。 |
| **性能与响应度 (Performance)** | 4.7 / 5.0 | 执行轻量极快，但 Git 子进程缺少超时拦截，且多技术栈工作区中基线自检仅覆盖首个技术栈。 |
| **安全性与防御 (Security)** | 4.3 / 5.0 | `.gitignore` 沙箱防御存在前缀覆盖绕过隐患；PowerShell 安装器用户主目录需防止空路径解析到根目录。 |
| **代码质量 (Code Quality)** | 4.4 / 5.0 | 状态与待办解析能力完备，但完成状态关键字覆盖不足（如 `Merged`, `已解决`），且数字词（如 `Base64`, `OAuth2`）易被误判为任务标识。 |
| **可维护性 (Maintainability)** | 4.6 / 5.0 | 双语文档与模板完整；`install.ps1` 缺少标准 `-Help` 引导提示，`.gitignore` 缺少本地工作区多智能体配置及 Python 构建缓存忽略。 |
| **测试覆盖 (Testing)** | 4.6 / 5.0 | 当前单测通过率 100% (24/24)，覆盖率 94%；部分容错异常与新增栈探测分支尚待断言。 |

- **静态代码分析基线**：`0 errors`, `0 warnings` (通过 `python -m compileall -q .`)
- **单元测试通过率**：`100% Pass` (24 / 24 tests in 1.57s)
- **代码行覆盖率**：`94.0%` (Hits: 816 / Total: 864)

### 3. 优势与工程亮点

1. **跨智能体无缝集成**：同时支持 6 大主流 AI 智能体体系，自动化清理冗余配置，保证单命令唯一性。
2. **零外部依赖自足运行**：纯 Python 3 标准库构建，跨 Linux / macOS / Windows 原生开箱即用。
3. **闭环守卫与增量零容忍**：提供完备的临时文档自动忽略检测、基线告警比对与 CI 退出码拦截。

---

## 二、全维度问题清单与根因分析

### 1. 架构设计 (Architecture Design)
- **问题 A1 (`scripts/__init__.py` 缺少子模块导出)**：虽然声明了 `__all__ = ["check_health", "track_progress"]`，但未显式 `from . import check_health, track_progress`，导致使用者在执行 `import scripts; scripts.check_health` 时抛出 `AttributeError`。
- **问题 A2 (`pyproject.toml` 缺少包发现白名单)**：默认 setuptools 自动发现机制会将 `tests/` 目录识别为顶层包，导致打包发布后在用户环境污染全局 `tests` 模块。

### 2. 性能与响应度 (Performance)
- **问题 P1 (Git 探测缺少超时防护)**：`check_git_status` 调用 `subprocess.run` 探测分支与工作区时未指定 `timeout`，若遇到凭证交互或挂载卡顿，可能导致进程死锁。
- **问题 P2 (多技术栈基线自检遗漏)**：在前后端分离或多栈仓库中，`--run-baseline` 仅执行 `stacks[0]`，无法对所有检测到的技术栈进行完整诊断。

### 3. 安全性与沙箱防御 (Security)
- **问题 S1 (`add_to_gitignore` 前缀匹配绕过隐患)**：`gitignore_path.startswith(abs_cwd)` 在路径存在前缀同名时（如 `/app` 与 `/app_other/.gitignore`）会误放行，应强制校验目标路径的父目录严格等于目标工作区。
- **问题 S2 (PowerShell 路径空值守卫)**：`install.ps1` 在清理旧配置时，若环境变量 `$UserHome` 为空，直接拼接可能解析到驱动器根目录 `\.claude\commands`。

### 4. 代码质量与稳健性 (Code Quality)
- **问题 Q1 (`is_status_done` 状态识别不全)**：在 GitHub PR 及敏捷推进中，常见的完成状态如 `Merged`、`Merged (#3)`、`Complete`、`Success`、`已解决`、`已修复`、`已实现` 以及 `完成 (xxx)` 被误判为未完成。
- **问题 Q2 (任务标识正则存在误匹配)**：待办列表中若包含 `Base64`、`OAuth2`、`Win32`、`IPv6` 等包含数字的技术名词，会被误提取为任务标识并截断任务名称。
- **问题 Q3 (表头别名支持不全)**：`parse_header_columns` 缺少对英文 `severity`（优先级）、`progress`（状态）、`action`/`item`（任务名）的别名映射。

### 5. 可维护性与工程化 (Maintainability)
- **问题 M1 (`install.ps1` 缺少 `-Help` 参数)**：运行 `install.ps1 -Help` 或 `-h` 时不仅不显示帮助，反而会直接执行默认全局安装，缺乏命令行友好度。
- **问题 M2 (`.gitignore` 遗漏本地工作区智能体生成物与构建缓存)**：缺少对 `.claude/worktrees/`、`.agents/`、`.cursor/commands/`、`dist/`、`build/`、`*.egg-info/`、`.ruff_cache/` 的忽略规则。

### 6. 测试覆盖与质量工程 (Testing & QA)
- **问题 T1 (包导出、状态识别扩展与安全边界单测盲区)**：针对新增的包导入、状态别名、安全沙箱防御及 Swift 栈识别需增加系统化单测断言。
- **问题 T2 (CI 缺少 pip 安装与 CLI 工具执行验证)**：当前 CI 仅直接运行脚本文件，未测试通过 `pip install -e .` 安装后控制台脚本 `check-health` 和 `track-progress` 的端到端可用性。

---

## 三、改进方案与落地路径

### P0 级：严重阻断、安全提权与崩溃隐患
- **OPT-01: 加固 .gitignore 路径沙箱防御与 PowerShell 用户目录根保护**
  - **涉及文件**：`scripts/check_health.py`, `install.ps1`
  - **方案**：使用 `os.path.dirname(gitignore_path) == abs_cwd` 精确判断父目录归属，并在 `install.ps1` 增加 `$UserHome` 非空非根保护。
  - **预期收益**：杜绝路径逃逸风险与非预期全局文件删除。

### P1 级：架构核心解耦与高收益性能优化
- **OPT-02: 修复 scripts 包命名空间导出与 pyproject 构建包范围隔离**
  - **涉及文件**：`scripts/__init__.py`, `pyproject.toml`
  - **方案**：在 `scripts/__init__.py` 中显式导入 `check_health` 与 `track_progress`；在 `pyproject.toml` 增加 `[tool.setuptools.packages.find]` 显式包含 `scripts*` 并排除 `tests*`。
  - **预期收益**：保证标准模块导入与 wheel 分发包干净规范，避免全局命名空间污染。

- **OPT-03: 扩展完成状态识别、防数字词被误判为任务标识并补全表头别名**
  - **涉及文件**：`scripts/track_progress.py`
  - **方案**：扩充 `is_status_done` 关键字（支持 `Merged`, `Complete`, `Success`, `已解决`, `已修复`, `已实现` 等）；强化任务 ID 正则提取逻辑，限定结构化标识前缀或显式包围符，避免技术专有名词误伤；完善表头列名映射。
  - **预期收益**：全面提升任务状态与标识解析容错率。

### P2 级：功能完备性、模块重构与容错降级
- **OPT-04: 增加 Swift 栈探测、Git 超时守卫、远程分支回退与多栈基线执行**
  - **涉及文件**：`scripts/check_health.py`
  - **方案**：增加 `Package.swift` 探测；为 Git 命令增加 `timeout=15` 并在缺失 `origin` 时回退至首个可用远程源；多技术栈场景下遍历全部技术栈执行基线校验。
  - **预期收益**：扩展苹果生态支持，防止进程死锁，提升多栈工程诊断完整性。

- **OPT-05: 为 install.ps1 增加 -Help 提示并在 .gitignore 忽略工作区智能体生成物**
  - **涉及文件**：`install.ps1`, `.gitignore`
  - **方案**：在 `install.ps1` 中增加 `[switch]$Help` 处理逻辑；在 `.gitignore` 补充 `.claude/worktrees/`, `.agents/`, `.cursor/commands/`, `dist/`, `build/`, `*.egg-info/`, `.ruff_cache/`。
  - **预期收益**：命令行体验对齐 `install.sh`，工作区测试后保持工作树干净。

### P3 级：工程规范、状态重构与测试加固
- **OPT-06: 增加 pip 安装与 CLI 命令行工具端到端调用验证**
  - **涉及文件**：`.github/workflows/ci.yml`
  - **方案**：在 CI 流程中增加 `pip install -e .` 及 `check-health --json`、`track-progress examples/sample-improvements.md --json` 验证步。
  - **预期收益**：保障发布的 CLI 工具在不同操作系统与 Python 环境均能直接调用。

- **OPT-07: 全面补齐安全沙箱、包导出、状态解析、Swift栈与超时分支的单元测试**
  - **涉及文件**：`tests/test_check_health.py`, `tests/test_track_progress.py`
  - **方案**：为所有新特性、边界场景与防御分支编写测试用例，全仓代码覆盖率提升至 97%+。
  - **预期收益**：筑牢质量基石，确保零回归。

---

## 四、实施优先级与推进清单

| 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P0** | **OPT-01** | 加固 .gitignore 路径沙箱防御与 PowerShell 用户目录根保护 | 彻底阻断路径越界与根路径误删隐患 | `scripts/check_health.py`, `install.ps1` | [x] |
| **P1** | **OPT-02** | 修复 scripts 包命名空间导出与 pyproject 构建包范围隔离 | 规范模块导入，杜绝测试包污染全局环境 | `scripts/__init__.py`, `pyproject.toml` | [x] |
| **P1** | **OPT-03** | 扩展完成状态识别、防数字词被误判为任务标识并补全表头别名 | 极大增强任务进度解析容错率 | `scripts/track_progress.py` | [x] |
| **P2** | **OPT-04** | 增加 Swift 栈探测、Git 超时守卫、远程分支回退与多栈基线执行 | 增强多栈适配能力并杜绝进程挂死 | `scripts/check_health.py` | [x] |
| **P2** | **OPT-05** | 为 install.ps1 增加 -Help 提示并在 .gitignore 忽略工作区智能体生成物 | 对齐多端安装体验，维护工作树纯净 | `install.ps1`, `.gitignore` | [x] |
| **P3** | **OPT-06** | 增加 pip 安装与 CLI 命令行工具端到端调用验证 | 强化 CI 自动化验证与发布质量 | `.github/workflows/ci.yml` | [x] |
| **P3** | **OPT-07** | 全面补齐安全沙箱、包导出、状态解析、Swift栈与超时分支的单元测试 | 提升测试覆盖率至 97%+ | `tests/test_check_health.py`, `tests/test_track_progress.py` | [x] |
