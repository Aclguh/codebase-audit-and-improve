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
│   check_health.py (stack/git/gitignore, baseline runner)    │
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
| **架构设计 (Architecture)** | 4.8 / 5.0 | 三层职责清晰，两个 CLI 脚本彼此独立、无循环依赖，安装器与技能定义解耦良好。 |
| **性能与响应度 (Performance)** | 4.9 / 5.0 | 纯 CLI 场景，所有子进程均设置超时；无阻塞式长任务或流式瓶颈。 |
| **安全性与防御 (Security)** | 4.3 / 5.0 | `.gitignore` 已使用 `git check-ignore` 权威判定，路径写入有沙箱校验；但 `--fix-gitignore` 在追加失败时仍报告成功，CI 工作流也缺少最小权限声明。 |
| **代码质量 (Code Quality)** | 4.5 / 5.0 | 主要流程稳健；`detect_stack` 对不可读目录会抛出未捕获异常，`check_gitignore` 读取异常同样未兜底。 |
| **可维护性 (Maintainability)** | 4.6 / 5.0 | 双语 README、SKILL、references、历史 audits 齐备；根 `SKILL.md` 与打包技能内容重复但无同步守护。 |
| **测试覆盖 (Testing)** | 4.5 / 5.0 | 行覆盖率 97%，但 PowerShell 安装器完全没有自动化测试，`--check --json` 门禁分支与安装重装清理缺少回归断言。 |

- **静态代码分析基线**：`python -m ruff check .` → `0 errors`, `0 warnings`。
- **单元测试通过率**：`100% Pass` (72 / 72 tests, `python -m unittest discover -s tests`)。
- **代码行覆盖率**：`97%` (Hits: 572 / Total: 591，`coverage report -m`，门槛 90%)。
- **本地环境**：Python 3.10.2；CI 矩阵 Ubuntu/Windows × Python 3.10/3.11/3.12。

### 3. 优势与工程亮点

- 两套 CLI 工具均具备 `--help`、结构化 JSON 输出与明确退出码，便于 Agent 集成。
- 安装脚本参数校验、根目录防护、路径穿越防护与安装冒烟测试均已落地。
- 解析器已支持围栏代码块跳过、列重排、别名表头、进度型状态识别与多种完成状态表达。
- 文档体系完整（README 双语、SKILL、references、templates、历史 audits），远程 CI 已在 Linux/Windows 双平台运行。

---

## 二、全维度问题清单与根因分析

### 1. 架构设计 (Architecture Design)
- 未发现职责失衡或跨层调用；两个脚本各自独立，安装器与技能定义边界清晰。

### 2. 性能与响应度 (Performance)
- 未发现阻断性问题；`run_baseline_command` 已设置 120s 超时并捕获超时异常。

### 3. 安全性与沙箱防御 (Security)
- **问题 S1 (`--fix-gitignore` 假成功)**：`main()` 无条件调用 `add_to_gitignore()` 后把 `is_ignored` 置为 `True`，即使写入被沙箱校验拒绝（返回 `False`）或写入抛出 `OSError`，前置安全检查仍会报告“已保护”，Agent 可能带着未受保护的 `IMPROVEMENTS.md` 继续执行并污染提交历史。
- **问题 S2 (CI 令牌权限过大)**：`.github/workflows/ci.yml` 未声明 `permissions`，工作流继承仓库默认令牌权限；本工作流只做只读检出与测试，应显式收敛为 `contents: read`。

### 4. 代码质量与稳健性 (Code Quality)
- **问题 Q1 (不可读目录导致崩溃)**：`detect_stack` 在探测 `tests/`、`scripts/`、`src/` 时直接调用 `os.listdir`，遇到权限不足或并发删除会抛出 `OSError`，整个技术栈探测（以及 Phase 1 前置检查）中断。
- **问题 Q2 (`check_gitignore` 读取异常未兜底)**：`.gitignore` 是目录、权限不足或编码异常时，`open()` 抛出的异常会直接冒泡，`--json` 调用方拿到的是 traceback 而不是结构化结果。
- **问题 Q3 (PowerShell 安装器覆盖用户配置)**：`Install-Continue` 在现有 `config.json` 解析失败（例如 Continue 常见的 JSONC 注释）时，直接 `Copy-Item -Force` 用模板覆盖，用户原有配置被静默销毁。

### 5. 可维护性与工程化 (Maintainability)
- **问题 M1 (技能文档漂移风险)**：根 `SKILL.md` 与 `skills/improve/SKILL.md` 当前逐字一致，但没有任何校验，后续单侧修改会让仓库入口与安装产物语义分叉。
- **问题 M2 (安装脚本不可测)**：`install.ps1` 通过 `GetFolderPath(UserProfile)` 直接取真实用户目录，测试无法隔离，导致 PowerShell 安装器长期没有自动化测试（`install.sh` 有）。

### 6. 测试覆盖与质量工程 (Testing & QA)
- **问题 T1 (`--check --json` 门禁分支无覆盖)**：`track_progress.py` JSON 输出分支中的 `pending > 0 → exit 1` 逻辑没有断言，CI 门禁失效时无法被测试发现。
- **问题 T2 (CI 语法检查清单写死)**：CI 的 `py_compile` 步骤逐个列出文件，新增测试文件不会被自动纳入。
- **问题 T3 (重装残留)**：`install.sh` 重装时执行 `rm -rf "${dest:?}"/*`，不会清理隐藏文件（如 `.DS_Store`、编辑器缓存），旧技能目录可能残留无关内容。

---

## 三、改进方案与落地路径

### P1 级：安全语义与用户数据保护

- **OPT-01: 修正 `--fix-gitignore` 的失败语义**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：`add_to_gitignore()` 捕获写入类 `OSError`；`check_gitignore()` 读取异常时返回“未保护”；`main()` 仅在写入成功且复核通过后报告受保护，否则输出明确失败信息并保持 `is_protected=false`。
  - **预期收益**：前置安全检查不再假成功，Agent 不会在未受保护状态下继续执行。

- **OPT-02: 保护 PowerShell 安装器的 Continue 配置与测试隔离**
  - **涉及文件**：`install.ps1`, `tests/test_install_ps1.py`
  - **方案**：`config.json` 解析失败时保留原文件并给出警告，不再覆盖；用户目录优先取 `USERPROFILE`（与 `install.sh` 的 `HOME` 语义一致），并拒绝空白或文件系统根目录；新增 PowerShell 安装器测试（帮助、工作区安装、非法目标、损坏配置保留、根目录拒绝）。
  - **预期收益**：避免用户配置被静默销毁，PowerShell 安装器首次获得可隔离的自动化回归。

### P2 级：健壮性与工程门禁

- **OPT-03: 技术栈探测容忍不可读目录**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：`os.listdir` 包裹异常处理，跳过无法读取的候选目录；补充权限/并发删除场景回归测试。
  - **预期收益**：Phase 1 探测在受限目录下不再崩溃。

- **OPT-04: CI 工作流收敛令牌权限**
  - **涉及文件**：`.github/workflows/ci.yml`
  - **方案**：在 workflow 级声明 `permissions: contents: read`。
  - **预期收益**：遵循最小权限原则，降低供应链风险。

- **OPT-05: 安装重装清理陈旧与隐藏文件**
  - **涉及文件**：`install.sh`, `tests/test_install_sh.py`
  - **方案**：先 `rm -rf "${dest:?}"` 再重建目录，代替仅删除非隐藏通配文件；补充重装后陈旧文件（含隐藏文件）被清除的回归测试。
  - **预期收益**：重复安装结果确定，技能目录不残留无关内容。

### P3 级：测试与文档守护

- **OPT-06: 补齐 `--check --json` 门禁回归测试**
  - **涉及文件**：`tests/test_track_progress.py`
  - **方案**：断言待办任务在 `--json --check` 下输出 `pending>0` 并以退出码 1 结束；`--quiet` 不产生控制台输出。
  - **预期收益**：CI 门禁语义有回归保护。

- **OPT-07: CI 语法检查覆盖全部脚本与测试**
  - **涉及文件**：`.github/workflows/ci.yml`
  - **方案**：将写死的 `py_compile` 文件清单替换为 `python -m compileall -q scripts tests`。
  - **预期收益**：新增脚本/测试自动纳入语法门禁。

- **OPT-08: 守护根 SKILL.md 与打包技能同步**
  - **涉及文件**：`tests/test_repo_docs.py`
  - **方案**：新增仓库文档一致性测试，断言根 `SKILL.md` 与 `skills/improve/SKILL.md` 完全一致，并校验两个技能入口的 frontmatter `name`。
  - **预期收益**：入口文档与安装产物不会悄悄分叉。

---

## 四、实施优先级与推进清单

| 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P1** | **OPT-01** | 修正 `--fix-gitignore` 失败语义与读取容错 | 前置安全检查不再假成功 | `scripts/check_health.py`, `tests/test_check_health.py` | [x] |
| **P1** | **OPT-02** | 保护 Continue 配置并隔离 PowerShell 安装测试 | 防止用户配置被覆盖，补齐安装器测试 | `install.ps1`, `tests/test_install_ps1.py` | [x] |
| **P2** | **OPT-03** | 技术栈探测容忍不可读目录 | 受限目录下探测不崩溃 | `scripts/check_health.py`, `tests/test_check_health.py` | [x] |
| **P2** | **OPT-04** | CI 工作流收敛令牌权限 | 最小权限，降低供应链风险 | `.github/workflows/ci.yml` | [x] |
| **P2** | **OPT-05** | 安装重装清理陈旧与隐藏文件 | 重复安装结果确定 | `install.sh`, `tests/test_install_sh.py` | [x] |
| **P3** | **OPT-06** | 补齐 `--check --json` 门禁回归测试 | CI 门禁语义有回归保护 | `tests/test_track_progress.py` | [x] |
| **P3** | **OPT-07** | CI 语法检查覆盖全部脚本与测试 | 新增文件自动纳入门禁 | `.github/workflows/ci.yml` | [x] |
| **P3** | **OPT-08** | 守护根 SKILL.md 与打包技能同步 | 入口文档与安装产物不分叉 | `tests/test_repo_docs.py` | [x] |
