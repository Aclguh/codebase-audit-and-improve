# Atomic Implementation & Verification Execution Loop

This reference specifies the rigorous protocol agents and developers must follow when implementing tasks defined in `IMPROVEMENTS.md`.

---

## 1. Core Principles

1. **One Task, One Commit**: Never batch multiple unrelated improvements into a monolithic commit. Each task must have an isolated, revertible git history.
2. **Zero-Regression Rule**: Before any code is committed, automated tests must pass 100%, and static analysis must have zero errors and zero warnings.
3. **Preserve Surrounding Integrity**: Maintain all existing comments, docstrings, formatting standards, and unrelated methods in edited files.
4. **Living Checklist**: `IMPROVEMENTS.md` must be dynamically updated in synchronization with each completed task.

---

## 2. The 7-Step Task Execution Loop

```
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
│ Ensure 0 errors, 0 warnings (e.g., flutter analyze, eslint) │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Execute Test Suites                                 │
│ Verify 100% tests pass (target unit tests & full suite)     │
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
  - *Example*: `chore: 移除已全部落地的临时改进建议文档 IMPROVEMENTS.md`

---

## 4. Handling Failures and Regressions

If a test fails or a linter raises a warning during Step 4 or Step 5:
1. **Never commit broken code** or bypass checks with `--no-verify`.
2. Analyze the stack trace or lint error immediately.
3. Fix the underlying root cause in the affected file or update the test mock if contracts changed legitimately.
4. Re-run tests and linters until 100% green before proceeding to Step 6 and Step 7.
