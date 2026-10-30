# Atomic Implementation & Verification Execution Loop

This reference specifies the rigorous protocol agents and developers must follow when implementing tasks defined in `IMPROVEMENTS.md`.

---

## 1. Core Principles

1. **Pre-flight Working Tree Cleanliness**: Always verify `git status --porcelain` is clean before starting the execution loop. Never mix uncommitted user changes into atomic improvement commits. If uncommitted work exists, stash or commit it first.
2. **One Task, One Commit**: Never batch multiple unrelated improvements into a monolithic commit. Each task must have an isolated, revertible git history.
3. **Incremental Zero-Tolerance Rule (增量零容忍)**:
   - Always distinguish between **pre-existing baseline warnings** and **newly introduced warnings**.
   - Quality gate condition:
     - Static analysis errors: **Must be 0**.
     - Newly introduced warnings in modified files: **Must be 0**.
     - Overall repository warning count: **Must not exceed baseline count** (`current_warnings <= baseline_warnings`).
   - *Rationale*: In large legacy codebases, do not block an urgent P0 security patch or architectural decoupling because untouched legacy files contain pre-existing lint warnings.
4. **Tiered Testing Strategy (分级测试体系)**:
   - **Per-Task Inner Loop**: Execute focused tests (unit tests and regression assertions specifically covering modified files/modules). Keep feedback cycle under 30 seconds.
   - **Global Outer Loop (Phase 5)**: Execute the full project test suite across all modules before final push and PR creation.
5. **Preserve Surrounding Integrity**: Maintain all existing comments, docstrings, formatting standards, and unrelated methods in edited files.
6. **Living Checklist**: `IMPROVEMENTS.md` must be dynamically updated in synchronization with each completed task.

---

## 2. The 7-Step Task Execution Loop

```
┌─────────────────────────────────────────────────────────────┐
│ Step 0: Pre-flight Verification                             │
│ Ensure working tree is clean (git status --porcelain == 0)   │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Task Selection & Scope Isolation                    │
│ Select next pending task (starting with P0 -> P1 -> P2 -> P3)│
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Inspection & Minimal Change Design                  │
│ Read target files, analyze call hierarchies & test cases    │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Implement Code Modification                         │
│ Apply focused edits; preserve existing interfaces & comments│
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Run Static Code Analysis                            │
│ Enforce Incremental Zero-Tolerance (0 errors, 0 new warnings)│
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Execute Tiered Test Suites                          │
│ Verify 100% pass on target unit & regression tests          │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 6: Update Task Status in IMPROVEMENTS.md               │
│ Change [ ] to [x], record commit reference or notes         │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 7: Atomic Conventional Git Commit                      │
│ git commit -m "<type>(<scope>): <concise message>"          │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Conventional Commit Standards

Commits must follow the Conventional Commits specification:

```
<type>(<scope>): <concise description in Chinese or English>
```

### Type Definitions:
- **`fix`**: Security patches, bug fixes, or null-safety corrections.
  - *Example*: `fix(security): 修复路径穿越漏洞并添加规范化安全校验`
- **`perf`**: Performance optimizations, asynchronous I/O, UI re-render reduction.
  - *Example*: `perf(chat): 解耦输入框打字监听并消除主屏全量重绘`
- **`refactor`**: Code restructuring without altering existing runtime behavior.
  - *Example*: `refactor(ui): 抽取独立会话历史抽屉组件并拆分上帝类`
- **`test`**: New unit tests, mock objects, regression assertions, or coverage expansion.
  - *Example*: `test(core): 补齐插件沙箱解压与边界路径断言用例`
- **`chore`**: Dependency updates, build configurations, or document lifecycle management.
  - *Example*: `chore: 归档已全部落地的临时改进建议文档至 docs/audits/`

---

## 4. Handling Failures and Rollback Protocol

If a test fails or a linter raises a new warning during Step 4 or Step 5:
1. **Never commit broken code** or bypass checks with `--no-verify`.
2. Analyze the stack trace or lint error immediately.
3. Fix the underlying root cause in the affected file or update the test mock if contracts changed legitimately.
4. Re-run tests and linters until green before proceeding to Step 6 and Step 7.

### Rollback / Impasse Recovery:
If a task implementation proves unviable, causes circular regressions, or exceeds safe refactoring boundaries:
1. Discard modified files cleanly:
   ```bash
   git restore .
   git clean -fd
   ```
2. Annotate the blocker in `IMPROVEMENTS.md` (e.g. `[!] Blocked by dependency XYZ`).
3. Re-evaluate whether the task should be decomposed into smaller sub-tasks before proceeding.
