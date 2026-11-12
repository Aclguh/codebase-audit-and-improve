# Codebase Audit & Improve: Architecture & Code Quality Assessment (IMPROVEMENTS.md)

> **Document Nature**: Temporary project health audit and technical improvement tracking document (excluded in `.gitignore`).
> This document coordinates step-by-step refactoring and quality hardening. Complete each task with an atomic Git commit.
> Upon full completion, this document can be archived to `docs/audits/YYYY-MM-DD-codebase-improvements.md` (recommended) or deleted.

---

## 一、项目现状与整体架构评估

### 1. 架构定位与模块拓扑

`codebase-audit-and-improve` 是一个跨平台的多智能体代码库审计与改进工作流框架，为 Google Antigravity、Claude Code、Cursor、Continue.dev、DeepSeek Harness (dsh) 与 OpenAI Codex 提供统一的六维健康审计与原子化落地标准。

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
| **架构设计 (Architecture)** | 4.8 / 5.0 | 双脚本分层清晰无依赖；Gradle 检测与 Maven 耦合，缺少根目录 settings.gradle 检测。 |
| **性能与响应度 (Performance)** | 4.9 / 5.0 | 线性单遍扫描；正则预编译规范良好；全量测试与执行在秒级完成。 |
| **安全性与防御 (Security)** | 4.6 / 5.0 | 沙箱隔离良好，但 Git remote origin 未过滤嵌入的 token/password 凭据，存在泄露风险。 |
| **代码质量 (Code Quality)** | 4.6 / 5.0 | 静态分析 0 告警，但 GFM 无前导竖线表格未被解析，Markdown 链接未从状态与任务名中脱敏。 |
| **可维护性 (Maintainability)** | 4.7 / 5.0 | 脚本与文档高度一致；受保护分支未包含 trunk；install.sh 未清理深层 .pyc 文件。 |
| **测试覆盖 (Testing)** | 4.8 / 5.0 | 单元测试行覆盖率达 98% (2004/2041 stmts)；需对本次加固点增补回归断言。 |

- **静态代码分析基线**：`0 errors`, `0 warnings` (`ruff check .` 全绿)
- **单元测试通过率**：`100% Pass` (113 / 113 tests)
- **代码行覆盖率**：`98.0%` (Hits: 2004 / Total: 2041)

### 3. 优势与工程亮点

1. **纯标准库零外部依赖**：`check_health.py` 与 `track_progress.py` 严格基于 Python 3.10+ 标准库，在任何干净环境中即装即用。
2. **严密的自动化安全护栏**：文件穿越防线、主目录与工作区根目录隔离保护、Git 状态失败关闭逻辑均已就位。
3. **高标准增量零容忍**：静态代码分析与单元测试均以 0 告警与 100% 通过率为基本门禁。

---

## 二、全维度问题清单与根因分析

### 1. 架构设计 (Architecture Design)
- **问题 A1 (Gradle 检测与 Maven 紧耦合且忽略 settings.gradle)**：`detect_stack()` 将 Gradle 作为 Maven 的 `elif` 分支，当仓库同时包含 Maven 与 Gradle 时无法同时识别；且只检测 `build.gradle(.kts)`，忽略了仅在根目录配置 `settings.gradle(.kts)` 的多项目 Gradle 架构。

### 2. 性能与响应度 (Performance)
- 保持高性能：正则均已预编译，单遍扫描开销维持在毫秒级。

### 3. 安全性与沙箱防御 (Security)
- **问题 S1 (Git remote origin 暴露嵌入式敏感凭据)**：`git remote get-url` 返回可能包含 basic auth 或 access token 的 URL（如 `https://token:ghp_xxx@github.com/...`），`check_health.py` 未对凭据脱敏直接在 JSON 与控制台输出，可能在 CI 日志或交互界面中泄露私密令牌。
- **问题 S2 (受保护分支列表遗漏 trunk 分支)**：许多现代仓库（如 GitHub 默认主干分支或 Monorepo）使用 `trunk`，目前分支保护仅拦截 `main/master/release/prod`，对 `trunk` 未加保护。

### 4. 代码质量与稳健性 (Code Quality)
- **问题 Q1 (GFM 无前导竖线 Markdown 表格被整体忽略)**：GFM 规范 §4.10 明确支持无外层竖线的合法 Markdown 表格（如 `Col1 | Col2`），`track_progress.py` 严格要求 `line_clean.startswith("|")`，导致此类表格完全无法识别，进而触发任务未找到错误。
- **问题 Q2 (状态单元格与任务名中的 Markdown 链接破坏解析)**：开发者在表格或清单中常写入 `[Completed](url)` 或 `[x] [OPT-01](url)`，`clean_cell` 未将 `[text](url)` 解构为 `text`，导致带链接的状态被判定为未完成，任务名称残留 `](url)`。
- **问题 Q3 (package.json 中假值 workspaces 误报)**：`detect_monorepo()` 中仅使用 `"workspaces" in pkg_data`，当 `"workspaces": null`、`false` 或 `[]` 时仍误报为 npm/yarn workspaces；缺少对 Go 1.18+ 原生工作区文件 `go.work` 的检测。

### 5. 可维护性与工程化 (Maintainability)
- **问题 M1 (install.sh 未清理历史 .pyc 字节码文件)**：`install.ps1` 会深度扫描并删除 `scripts/` 下的 `*.pyc` 文件，而 `install.sh` 仅删除了 `__pycache__` 目录，未对残留的单个 `.pyc` 进行清理。

### 6. 测试覆盖与质量工程 (Testing & QA)
- **问题 T1 (缺少针对新增边界与安全脱敏的回归测试)**：需为 URL 凭据脱敏、无前导竖线表格、Markdown 链接清洗、settings.gradle 识别、go.work 工作区检测增补专门的单元测试用例。

---

## 三、改进方案与落地路径

### P0 级：严重阻断、安全提权与崩溃隐患
- 无 P0 级阻断项。

### P1 级：架构核心解耦与高收益性能优化
- **OPT-01: Git remote origin 凭据敏感信息脱敏**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：增加 `sanitize_remote_url` 函数，使用正则将 HTTP(S) URL 中嵌入的用户名、密码或令牌（如 `https://user:token@host/repo`）脱敏为 `https://***@host/repo`。
  - **预期收益**：杜绝在健康检测报告与 JSON 输出中意外泄露敏感凭证。

- **OPT-02: 支持 GFM 无前导竖线标准表格解析**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：优化表格行切分与检测逻辑，在行包含 `|` 且处于表格上下文或后续为分隔线时均可正确解析无前导竖线的 GFM 表格。
  - **预期收益**：兼容全部符合 GFM 规范的 Markdown 表格路线图。

### P2 级：功能完备性、模块重构与容错降级
- **OPT-03: 清洗状态单元格与任务名称中的 Markdown 链接**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：在 `clean_cell` 中增加 Markdown 链接正则替换 `[text](url) -> text`，使 `[Completed](url)` 能被正确识别为完成，且任务名不残留多余链接标记。
  - **预期收益**：提升富文本与带 PR/Issue 链接路线图的解析准确度。

- **OPT-04: 解耦 Gradle 检测并支持根目录 settings.gradle(.kts)**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：将 Gradle 独立为独立 `if` 检查，支持 `settings.gradle` 与 `settings.gradle.kts`，并精确报告实际匹配到的清单文件名。
  - **预期收益**：完美支持 Gradle 多项目工程与 Maven/Gradle 混合工程。

### P3 级：工程规范、状态重构与测试加固
- **OPT-05: 增强工作区检测 (go.work 与 package.json 假值防护)**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：`detect_monorepo` 增加 `go.work` 识别，并对 `package.json` 中的 `workspaces` 进行类型和真值检查。
  - **预期收益**：消除工作区误报，扩充 Go 语言工作区生态支持。

- **OPT-06: 扩充 trunk 受保护分支与 install.sh 字节码清理**
  - **涉及文件**：`scripts/check_health.py`, `install.sh`, `tests/test_check_health.py`
  - **方案**：将 `trunk` 纳入受保护分支列表；在 `install.sh` 中增加删除 `*.pyc` 的逻辑，与 `install.ps1` 保持一致。
  - **预期收益**：防止在 trunk 主干分支直接误提交，保持跨平台安装器行为对称。

---

## 四、实施优先级与推进清单

| 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P1** | **OPT-01** | Git remote origin 凭据敏感信息脱敏 | 杜绝在报告中泄露私密令牌与密码 | `scripts/check_health.py` | [x] |
| **P1** | **OPT-02** | 支持 GFM 无前导竖线标准表格解析 | 全面兼容 GFM 规范无外层竖线表格 | `scripts/track_progress.py` | [x] |
| **P2** | **OPT-03** | 清洗状态单元格与任务名中的 Markdown 链接 | 支持带链接状态与干净任务名提取 | `scripts/track_progress.py` | [x] |
| **P2** | **OPT-04** | 解耦 Gradle 检测并支持根目录 settings.gradle | 准确识别 Gradle 多项目与混合工程 | `scripts/check_health.py` | [x] |
| **P3** | **OPT-05** | 增强工作区检测 (go.work 与 package.json 假值防护) | 消除假值误报，支持 Go 原生工作区 | `scripts/check_health.py` | [x] |
| **P3** | **OPT-06** | 扩充 trunk 受保护分支与 install.sh 字节码清理 | 防止 trunk 直接误提交，统一安装清理 | `scripts/check_health.py`, `install.sh` | [x] |
