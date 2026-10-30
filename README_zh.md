# 代码库全方位审计与改进工作流 (`codebase-audit-and-improve`)

[![Skill](https://img.shields.io/badge/Antigravity-Skill-4285F4?logo=google)](https://github.com/Aclguh/codebase-audit-and-improve)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Aclguh/codebase-audit-and-improve/pulls)

[English](README.md) | [简体中文](README_zh.md)

---

**`codebase-audit-and-improve`** 是一套专为 Google Antigravity 及现代 AI 编程智能体打造的高标准工作流 Skill（注册命令为 `/improve` 与 `/improve-all`）。它将高层级架构审计与原子化工程落地紧密结合，通过结构化的 `IMPROVEMENTS.md` 实现端到端可追溯的重构治理。

## 核心特性

- **六大维度深度体检与子代理并行审计**：
  1. **架构设计**：检测上帝类/上帝组件、模块分层跨越、Monorepo 包隔离。
  2. **代码质量**：增量零容忍门禁（0 错误、0 新增告警）、类型严格性、异常吞没防护。
  3. **性能与响应度**：主线程同步 I/O 阻塞、单点打字全量重绘、流式与内存占用。
  4. **可维护性**：国际化覆盖、依赖过时、分级日志规范。
  5. **安全性与沙箱**：目录穿越漏洞防御、命令注入防御、解压防 Zip Slip。
  6. **测试与质量**：关键逻辑单测盲区、回归断言、CI 友好度。
  *(针对超 50+ 文件的大型项目，支持调用 `research` 只读子代理并行扫描，保护主会话上下文)*
- **全生态与 Monorepo 适配**：开箱即用支持 Flutter/Dart, Node.js (npm/pnpm/yarn/bun), Python (uv/poetry/pdm), Rust, Go, Java/Kotlin (Maven/Gradle), .NET/C#, C/C++ (CMake), PHP, Ruby 等。
- **结构化进度追踪 (`IMPROVEMENTS.md`)**：
  - 自动保障已在 `.gitignore` 中忽略，不污染远程代码仓库。
  - 标准化任务排期表（P0 紧急阻塞 -> P3 规范打磨），分配独立编号（`OPT-01`、`OPT-02` 等）。
  - 支持“归档模式”：全部落地后自动归档至 `docs/audits/`，沉淀为团队架构资产。
- **增量零容忍质量门禁 (Incremental Zero-Tolerance)**：
  - 一项改进对应一次独立 Git Commit（Conventional Commits 规范）。
  - 区分存量债务与增量告警：**0 错误、0 新增告警，全仓告警总数 <= 基线告警数**，避免老项目历史 warning 阻断紧急修复。
  - **分级测试**：原子循环期间执行受影响模块的轻量单测，全量回归放到 Phase 5 最终收敛阶段。
- **保护分支防御与自动化 PR 流**：
  - 自动识别当前是否为保护分支（`main`, `master`, `release`）。
  - 在保护分支上自动拉取特性分支并通过 GitHub CLI (`gh pr create`) 提 PR，防止直接向主干强推。
- **CI 验证闭环与无人值守**：
  - 与 `/goal` 及 `/improve-all` 深度集成，完成全量落地后自动跟踪 GitHub Actions CI 绿灯。

## 快速上手与多 Agent 安装

本项目原生支持在多个主流 AI Agent 工具的输入框中，输入 `/` 触发命令自动补全预览（包含名称与说明）与技能调用：
- **Google Antigravity**：原生 Skill 自动补全 (`/improve`, `/improve-all`)。
- **Anthropic Claude Code**：命令行交互原生下拉补全 (`/improve`, `/improve-all`)。
- **Cursor IDE**：Composer / Agent 输入框原生下拉补全 (`/improve`, `/improve-all`)。
- **Continue.dev**：VS Code / JetBrains 输入框下拉菜单 (`/improve`, `/improve-all`)。
- **DeepSeek Harness (dsh)**：Web UI / TUI / Desktop 输入框 `/` 自动补全与卡片渲染 (`/improve`, `/improve-all`)。
- **OpenAI Codex Desktop**：桌面端输入框原生技能下拉预览（输入 `/imp` 即提示 `Improve` 与 `Improve All`）。
- **OpenAI Codex CLI**：终端 TUI 严格将 `/` 保留为内置调度命令（如 `/skills`, `/model`, `/import` 等）；使用 `$improve` / `$improve-all` 进行技能引用，或运行 `/skills` 开启交互式技能管理弹窗，或在提问中自然语言调用。

### 1. 全局一键安装（全生态支持）

一键安装到本地所有已检测到的 Agent 工具目录中：

**PowerShell (Windows):**
```powershell
git clone https://github.com/Aclguh/codebase-audit-and-improve.git
cd codebase-audit-and-improve
.\install.ps1 -Target All
```

**Bash (Linux / macOS):**
```bash
git clone https://github.com/Aclguh/codebase-audit-and-improve.git
cd codebase-audit-and-improve
chmod +x install.sh && ./install.sh all
```

*提示：也可以指定单一工具安装：`-Target Antigravity`、`-Target Claude`、`-Target Cursor` 或 `-Target Continue`。*

### 2. 工作区专属安装（随项目提交团队共享）

直接在当前代码仓库工作区生成配置，团队内任何使用 Antigravity、Claude Code、Cursor 或 Continue 的成员打开项目输入 `/` 即可联想补全：

```powershell
# Windows
.\install.ps1 -Target All -Workspace

# Linux / macOS
./install.sh all --workspace
```

## 使用指南

### 方式 1：全自主端到端执行 (`/improve-all`)

一键串联基线检测、六维审计、路线图生成、原子提交循环、文档归档、提 PR 与 CI 监控：

```text
/improve-all
```

执行流程：
1. 前置工作区干净度与基线检测 (`check_health.py --json`)。
2. 六维度深度体检（支持子代理并行分治）。
3. 生成结构化 `IMPROVEMENTS.md`。
4. 自动按 P0 -> P3 顺序逐项原子实现（增量零容忍、分级单测、Conventional Commits）。
5. 全仓回归测试、归档/清理路线图、保护分支创建 PR、推送远程并监控 GitHub Actions CI 绿灯。

---

### 方式 2：分步交互式评估与治理 (`/improve`)

如果你希望在动手前先人工确认技术改进方案：

#### 1. 生成改进建议规划文档
```text
/improve
```
Agent 将对项目进行全面审计并生成包含架构拓扑、评分卡与实施清单的 `IMPROVEMENTS.md`。

#### 2. 触发自主落地
针对方案确认无误后，指示 Agent 开始落地：
```text
/goal 全部实现
```

#### 3. 验收与远程提交
当清单项全部勾选完毕后：
```text
push 并监控 GitHub CI 状态
```

## 仓库结构

```
codebase-audit-and-improve/
├── SKILL.md                     # Antigravity Skill 主定义 (/improve, /improve-all)
├── README.md                    # 英文文档
├── README_zh.md                 # 中文文档
├── LICENSE                      # MIT 开源协议
├── install.ps1                  # Windows 一键安装脚本
├── install.sh                   # Linux/macOS 一键安装脚本
├── references/                  # 参考规范与指导手册（按需加载）
│   ├── audit-dimensions.md      # 六大维度深度审计清单与子代理指导
│   ├── improvements-template.md # 通用 IMPROVEMENTS.md 标准模板
│   ├── execution-loop.md        # 原子循环规范、增量门禁与分级测试
│   └── ci-monitoring.md         # 分支保护、自动化 PR 与 CI 排查
├── scripts/                     # 辅助工具脚本
│   ├── check_health.py          # 技术栈识别、Monorepo 诊断与基线检测
│   └── track_progress.py        # 进度解析、动态列匹配与 CI 门禁检查
├── skills/                      # 预置单技能定义
│   ├── improve/                 # /improve Skill
│   └── improve-all/             # /improve-all Skill
├── tests/                       # 自动化单元测试套件
│   ├── test_check_health.py     # 探针工具测试
│   └── test_track_progress.py   # 进度解析工具测试
└── examples/
    └── sample-improvements.md   # 生产级样本 IMPROVEMENTS.md
```

## 辅助脚本速查

```bash
# 检测当前项目技术栈、Monorepo 及 Git 工作区保护状态
python scripts/check_health.py

# 输出供 Agent 消费的结构化 JSON
python scripts/check_health.py --json

# 自动将 IMPROVEMENTS.md 追加至 .gitignore
python scripts/check_health.py --fix-gitignore

# 解析与汇报 IMPROVEMENTS.md 进度
python scripts/track_progress.py IMPROVEMENTS.md

# CI 门禁检查（全部完成 exit 0，未完成 exit 1）
python scripts/track_progress.py --check

# 运行自动化测试套件
python -m unittest discover tests
```

## 开源协议

本项目采用 [MIT License](./LICENSE) 开源协议。
