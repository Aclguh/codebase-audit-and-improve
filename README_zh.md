# 代码库全方位审计与改进工作流 (`codebase-audit-and-improve`)

[![Skill](https://img.shields.io/badge/Antigravity-Skill-4285F4?logo=google)](https://github.com/Aclguh/codebase-audit-and-improve)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Aclguh/codebase-audit-and-improve/pulls)

[English](README.md) | [简体中文](README_zh.md)

---

**`codebase-audit-and-improve`** 是一套专为 Google Antigravity 及现代 AI 编程智能体打造的高标准工作流 Skill。它将高层级架构审计与原子化工程落地紧密结合，通过结构化的 `IMPROVEMENTS.md` 实现端到端可追溯的重构治理。

## 核心特性

- **六大维度深度体检**：
  1. **架构设计**：检测上帝类/上帝组件、模块分层跨越、状态管理割裂等。
  2. **代码质量**：静态检查 0 警告、类型严格性、异常吞没防护。
  3. **性能与响应度**：主线程同步 I/O 阻塞、单点打字全量重绘、流式与内存占用。
  4. **可维护性**：国际化覆盖、依赖过时、分级日志规范。
  5. **安全性与沙箱**：目录穿越漏洞防御、命令注入防御、解压防 Zip Slip。
  6. **测试与质量**：关键逻辑单测盲区、回归断言、CI 友好度。
- **结构化进度追踪 (`IMPROVEMENTS.md`)**：
  - 自动保障已在 `.gitignore` 中忽略，不污染远程代码仓库。
  - 标准化任务排期表（P0 紧急阻塞 -> P3 规范打磨），分配独立编号（`OPT-01`、`OPT-02` 等）。
- **原子化渐进交付闭环 (Atomic Execution Loop)**：
  - 一项改进对应一次独立 Git Commit（Conventional Commits 规范）。
  - 提交前必须通过静态代码分析（0 Error, 0 Warning）与单元测试（100% Pass）。
- **与 `/goal` 深度融合**：
  - 适合无人值守的长时间重构任务，全部完成并通过验证后输出完成信号。
- **CI 验证闭环**：
  - 任务全量落地后清理临时文档，自动推送远程仓库并通过 GitHub CLI (`gh`) 实时跟踪 CI 绿灯。

## 快速上手与安装

### 全局安装（适用于所有 Antigravity 工作区）

**PowerShell (Windows):**
```powershell
git clone https://github.com/Aclguh/codebase-audit-and-improve.git
cd codebase-audit-and-improve
.\install.ps1
```

**Bash (Linux / macOS):**
```bash
git clone https://github.com/Aclguh/codebase-audit-and-improve.git
cd codebase-audit-and-improve
chmod +x install.sh && ./install.sh
```

### 工作区安装（仅对当前项目生效）

```powershell
# Windows
.\install.ps1 -Workspace

# Linux / macOS
./install.sh --workspace
```

## 使用方法与触发词

在 Antigravity 对话中，向智能体发送以下提示词：

```text
请评估当前项目的整体状况，从代码质量、架构设计、性能、可维护性、安全性和测试覆盖等方面识别可改进之处。针对每项问题提供具体、可落地的改进建议并说明预期收益，按优先级排序。最终输出一份结构化的临时的改进建议文档IMPROVEMENTS.md，如果.gitignore中不存在的话，将其添加至.gitignore，完成后也不需要移除，包含现状分析、问题清单、改进方案与实施优先级。完成改进建议文档的任意一个内容后需进行提交，当改进建议文档被全部完成时可以删除。
```

如需让智能体自主按序全部实现：
```text
/goal 全部实现
```

当所有任务完成后：
```text
push并检测GitHub ci通过情况
```

## 仓库目录结构

```
codebase-audit-and-improve/
├── SKILL.md                     # Antigravity 核心 Skill 定义与 YAML 前言元数据
├── README.md                    # 英文项目介绍与使用手册
├── README_zh.md                 # 中文项目介绍与使用手册
├── LICENSE                      # MIT 开源许可证
├── install.ps1                  # Windows 一键安装脚本
├── install.sh                   # Linux/macOS 一键安装脚本
├── references/                  # 深度参考文档（按需递进加载，节约 Token）
│   ├── audit-dimensions.md      # 六大评估维度详细诊断清单与评分细则
│   ├── improvements-template.md # 通用、脱敏的 IMPROVEMENTS.md 标准模板
│   ├── execution-loop.md        # 原子化任务实施、静态检查与 Commit 规约
│   └── ci-monitoring.md         # GitHub CLI 监控与 CI 修复指引
├── scripts/                     # 辅助工具脚本
│   ├── check_health.py          # 跨平台工程技术栈探测与 .gitignore 检查
│   └── track_progress.py        # IMPROVEMENTS.md 解析器与任务完成度统计
└── examples/
    └── sample-improvements.md   # 脱敏的生产级 IMPROVEMENTS.md 示范样例
```

## 辅助脚本使用

```bash
# 检查当前项目技术栈及 .gitignore 是否已排除 IMPROVEMENTS.md
python scripts/check_health.py

# 统计 IMPROVEMENTS.md 的实施进度与各优先级完成状态
python scripts/track_progress.py IMPROVEMENTS.md
```

## 开源许可证

本项目采用 [MIT License](./LICENSE) 授权开源。
