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
| **架构设计 (Architecture)** | 4.0 / 5.0 | 三层职责清晰，脚本内聚；`detect_stack` 较长但职责单一，暂不强行拆分。 |
| **性能与响应度 (Performance)** | 4.8 / 5.0 | 纯 CLI 场景，子进程均设超时；无主线程/流式瓶颈。 |
| **安全性与防御 (Security)** | 3.5 / 5.0 | `.gitignore` 判定在大小写敏感文件系统上会误报；安装脚本对异常 HOME 缺少硬防护。 |
| **代码质量 (Code Quality)** | 3.8 / 5.0 | 主要流程稳健，但安装参数与 Markdown 解析存在静默错误分支。 |
| **可维护性 (Maintainability)** | 3.5 / 5.0 | 跨平台路径、CLI 文档与 CI 质量门禁仍有缺口。 |
| **测试覆盖 (Testing)** | 4.0 / 5.0 | 行覆盖率 96%，但存在无效测试、静默 `except` 与安装脚本零覆盖。 |

- **静态代码分析基线**：`python -m py_compile` 全部通过；当前 CI 未配置真实 linter，等价基线告警数 `0`。
- **单元测试通过率**：`100% Pass` (40 / 40 tests, `python -m unittest discover`)
- **代码行覆盖率**：`96%` (Hits: 1063 / Total: 1110，`coverage report -m`)
- **本地环境**：Python 3.10.2；CI 矩阵 Ubuntu/Windows × Python 3.10/3.11/3.12。

### 3. 优势与工程亮点

- 两套 CLI 工具均具备 `--help`、结构化 JSON 输出与明确退出码，便于 Agent 集成。
- `.gitignore` 保护、保护分支识别、无状态列表格容错等此前审计问题均已落地并有回归测试。
- 文档体系完整（README 双语、SKILL、references、templates、历史 audits）。

---

## 二、全维度问题清单与根因分析

### 1. 架构设计 (Architecture Design)
- **问题 A1 (文档单一来源缺失)**：根 `SKILL.md` 与 `skills/improve/SKILL.md` 完全重复，修改时依赖人工同步，存在漂移风险（本轮保持现状，低风险接受）。

### 2. 性能与响应度 (Performance)
- 未发现阻断性问题；`run_baseline_command` 已设置 120s 超时并捕获超时异常。

### 3. 安全性与沙箱防御 (Security)
- **问题 S1 (gitignore 判定误报)**：`check_gitignore` 将规则与文件名同时小写化，在 Linux（大小写敏感）下，`.gitignore` 中的 `improvements.md` 会被误判为已忽略，而 Git 实际不会忽略，可能导致临时路线图被提交。
- **问题 S2 (安装根目录防护不足)**：`install.sh` 在 `HOME` 为空/为 `/` 时仍会拼出根级目标并使用 `rm -rf`，缺少显式失败保护。

### 4. 代码质量与稳健性 (Code Quality)
- **问题 Q1 (安装参数静默回退)**：`install.sh` 遇到未知 target（如拼写错误 `claud`）或未知选项时静默忽略，`TARGET` 保持默认 `all`，会误装全部 Agent 且以 0 退出；`--target` 缺少值时报错信息不明确。
- **问题 Q2 (表头优先级误判)**：`parse_header_columns` 先匹配 `task/任务` 再匹配 `status/状态`，导致 `任务状态`、`Task Status` 被当作「任务名称」，状态列丢失且名称变成 `[x]`。
- **问题 Q3 (围栏代码块未跳过)**：`parse_improvements_file` 会把 ```markdown 代码块中的示例任务表当作真实任务统计，污染进度与 `--check` 门禁。
- **问题 Q4 (任务表识别过窄)**：只有 `id+priority+name` 或含状态列的表才会被识别，`ID + Task` 这类精简任务表被整表丢弃。

### 5. 可维护性与工程化 (Maintainability)
- **问题 M1 (`install.ps1` 硬编码反斜杠)**：`skills\improve-all\SKILL.md`、`templates\cursor\...` 等路径在 PowerShell Core 非 Windows 环境不可用。
- **问题 M2 (CI 质量门禁不足)**：仅执行 `py_compile` 与 unittest，缺少真实静态分析与覆盖率阈值。

### 6. 测试覆盖与质量工程 (Testing & QA)
- **问题 T1 (无效/弱测试)**：`test_add_to_gitignore_sandbox_check` 中 `with patch(...): pass` 无任何断言；`test_check_git_status_live_repo` 用宽泛 `except: pass` 吞掉全部失败。
- **问题 T2 (安装脚本零测试)**：`install.sh` 仅被 CI 做语法检查，参数校验与真实安装路径没有回归测试。
- **问题 T3 (异常分支未覆盖)**：`check_health.py` 的 uv/pdm/flake8/npx 分支、git 异常、超时异常等仍为 0 覆盖。

---

## 三、改进方案与落地路径

### P0 级：严重阻断、安全提权与崩溃隐患
- **OPT-01: install.sh 参数严格校验**
  - **涉及文件**：`install.sh`, `tests/test_install_sh.py`
  - **方案**：未知 target/选项、缺失 `--target` 值均输出明确错误并以非 0 退出；解析后统一校验 target 白名单，禁止静默回退 `all`。
  - **预期收益**：杜绝拼写错误导致的全量误装，安装行为可预期。

- **OPT-02: gitignore 保护改用 `git check-ignore` 权威判定**
  - **涉及文件**：`scripts/check_health.py`, `tests/test_check_health.py`
  - **方案**：在 Git 仓库中优先调用 `git check-ignore -q -- IMPROVEMENTS.md`；仅在非 Git 环境或命令不可用时回退到规则启发式。
  - **预期收益**：修正 Linux 大小写敏感误报，避免临时文档被误提交。

- **OPT-03: 修正表头识别优先级并放宽任务表识别**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：按 priority → id → status → files → benefit → name 顺序匹配；ASCII 关键词使用词边界（避免 `Valid` 被当成 ID）；任务表在 `id+name` 或 `priority+name` 时也纳入统计。
  - **预期收益**：`任务状态`/`Task Status` 正确生效，更多自由风格任务表不再丢行。

### P1 级：架构核心解耦与高收益性能优化
- **OPT-04: 解析器跳过围栏代码块**
  - **涉及文件**：`scripts/track_progress.py`, `tests/test_track_progress.py`
  - **方案**：跟踪 ``` / ~~~ 围栏（支持长度与信息串），围栏内内容不参与表格/清单解析。
  - **预期收益**：模板示例不再污染真实进度，`--check` 门禁结果可信。

- **OPT-05: install.ps1 跨平台路径规范化**
  - **涉及文件**：`install.ps1`, `.github/workflows/ci.yml`
  - **方案**：所有 `\` 拼路径改为嵌套 `Join-Path`，并在 CI 增加一次临时工作区安装冒烟测试。
  - **预期收益**：兼容 PowerShell Core，验证真实复制链路而非仅 `-Help`。

- **OPT-06: install.sh 根目录防护**
  - **涉及文件**：`install.sh`, `tests/test_install_sh.py`
  - **方案**：全局安装前要求 `HOME` 非空且不为 `/`；目标目录必须位于预期 base 之下，否则报错退出。
  - **预期收益**：消除异常环境下对根级目录执行递归删除的风险。

### P2 级：功能完备性、模块重构与容错降级
- **OPT-07: 清理弱测试并补齐异常分支**
  - **涉及文件**：`tests/test_check_health.py`, `tests/test_track_progress.py`
  - **方案**：删除无断言的 patch 块，用 `skipUnless`/显式断言替代吞异常；补齐 uv/pdm/flake8/npx、git 异常、子进程超时等分支测试。
  - **预期收益**：测试可信度提升，异常路径具备回归保护。

- **OPT-08: CI 加入真实静态分析与覆盖率门禁**
  - **涉及文件**：`.github/workflows/ci.yml`, `pyproject.toml`
  - **方案**：新增 ruff 检查（按需配置 E402 忽略），并用 coverage 执行单测后 `--fail-under=90`；补充 dev 可选依赖。
  - **预期收益**：CI 从「能跑」升级为「有质量阈值」，阻止回归。

### P3 级：工程规范、状态重构与测试加固
- **OPT-09: 更新双语文档的 CLI 与开发验证说明**
  - **涉及文件**：`README.md`, `README_zh.md`
  - **方案**：补充 `--help` / `--run-baseline`、安装参数错误行为、ruff/coverage 本地验证命令。
  - **预期收益**：降低新贡献者上手成本，文档与实现一致。

---

## 四、实施优先级与推进清单

| 优先级 | 任务标识 | 任务名称 | 核心收益 | 涉及文件 | 状态 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **P0** | **OPT-01** | 严格校验 install.sh target 与选项参数 | 杜绝拼写错误导致全量误装 | `install.sh`, `tests/test_install_sh.py` | [x] |
| **P0** | **OPT-02** | 使用 git check-ignore 权威判定忽略状态 | 修复大小写敏感文件系统误报 | `scripts/check_health.py`, `tests/test_check_health.py` | [x] |
| **P0** | **OPT-03** | 修正表头识别优先级并放宽任务表识别 | 状态列不再丢失，任务表不再漏行 | `scripts/track_progress.py`, `tests/test_track_progress.py` | [x] |
| **P1** | **OPT-04** | 解析器跳过围栏代码块 | 示例任务不再污染进度统计 | `scripts/track_progress.py`, `tests/test_track_progress.py` | [x] |
| **P1** | **OPT-05** | install.ps1 路径 Join-Path 跨平台化 | 兼容 PowerShell Core 并增加安装冒烟 | `install.ps1`, `.github/workflows/ci.yml` | [x] |
| **P1** | **OPT-06** | install.sh 空/根 HOME 防护 | 消除根级目录误删风险 | `install.sh`, `tests/test_install_sh.py` | [x] |
| **P2** | **OPT-07** | 清理弱测试并补齐异常分支 | 测试可信度与异常覆盖提升 | `tests/test_check_health.py`, `tests/test_track_progress.py` | [x] |
| **P2** | **OPT-08** | CI 增加 ruff 与覆盖率门禁 | 建立可执行的代码质量阈值 | `.github/workflows/ci.yml`, `pyproject.toml` | [x] |
| **P3** | **OPT-09** | 更新双语 README 的 CLI/开发说明 | 文档与实现保持一致 | `README.md`, `README_zh.md` | [x] |
