# Six-Dimensional Project Health Audit Framework

This reference outlines the criteria, diagnostic questions, risk rating guidelines, and subagent delegation strategies across the six core dimensions.

---

## Subagent-Assisted Parallel Audit (Context Optimization)

> [!TIP]
> In large codebases (> 50 source files), conducting exhaustive file inspection in a single conversation context can quickly saturate token limits.
> It is strongly recommended to invoke read-only subagents (e.g. `research` subagents) in parallel:
> - **Subagent 1**: Architecture & Modularity (God classes, layer boundaries, Monorepo coupling).
> - **Subagent 2**: Security & Sandbox Defense (Path traversal, command injection, Zip Slip).
> - **Subagent 3**: Test & Baseline Diagnostics (Test runners, baseline warnings count, coverage blindspots).
>
> Subagents return concise summaries, allowing the parent agent to generate `IMPROVEMENTS.md` with minimal context overhead.

---

## 1. Architecture Design & Modularity (架构设计)

### Audit Criteria:
- **Separation of Concerns**: Domain logic, data access, presentation, and external infrastructure should have clear boundaries.
- **God Class / God Component Detection**: Inspect source files for excessive length (> 800 lines) or overloaded responsibilities (e.g. handling state, rendering, I/O, networking, and dialogs in a single class).
- **Coupling & Cohesion**: Look for circular module imports, excessive constructor parameter drilling (Prop Drilling), or bypassing architectural layers.
- **Monorepo / Workspace Isolation**: In monorepos, verify that package boundaries are strictly respected and shared internal libraries do not import downstream application packages.
- **State Management Consistency**: Verify that state management (e.g. Riverpod, Redux, Zustand, Vuex, Bloc) is adopted uniformly rather than mixed inconsistently with raw component state.

### Diagnostic Questions:
- Does the UI layer directly touch raw file handles, database drivers, or shell processes?
- Are business models decoupled from UI rendering widgets/templates?
- Are adapters used to isolate third-party vendor dependencies?

---

## 2. Code Quality & Robustness (代码质量与稳健性)

### Audit Criteria:
- **Static Analysis Compliance & Baseline Recording**: Execute project linters (`flutter analyze`, `npm run lint`, `cargo clippy`, `ruff check`, etc.). Record baseline warning count to enforce the **Incremental Zero-Tolerance** gate.
- **Type Safety & Strict Nullness**: Ensure strict typing is enabled; avoid indiscriminate usage of `any`, `dynamic`, `Object?` type casting, or unchecked force-unwrapping.
- **Error & Exception Handling**: Replace empty `catch {}` blocks with structured, typed domain exceptions and actionable error reporting.
- **Resource Management**: Ensure files, streams, network controllers, timers, database connections, and subprocesses are properly closed/disposed in lifecycle hooks.

### Diagnostic Questions:
- Are there unhandled asynchronous promise rejections or unawaited futures?
- Are error messages informative for developers and end-users?

---

## 3. Performance & Responsiveness (性能与响应度)

### Audit Criteria:
- **Main / UI Thread Blocking**: Detect synchronous file I/O (e.g. `readFileSync`, `File.readAsBytesSync`) or heavy CPU computations running on the UI thread.
- **Granular Rebuilds vs Full Re-rendering**: Check whether typing into an input field or updating a single item triggers full-tree rebuilds or redraws.
- **Streaming vs Memory Buffering**: Ensure large downloads, logs, AI model responses, or file decodings use streaming (SSE, chunked streams) instead of reading entire files into RAM.
- **Memory Footprint & OOM Defense**: Audit image caches, object pooling, and unbounded in-memory caches.

### Diagnostic Questions:
- Does user interaction drop frames (jank) during heavy operations?
- Are long-running agent tasks streamable and interruptible?

---

## 4. Maintainability & Engineering Practices (可维护性与工程化)

### Audit Criteria:
- **Internationalization (i18n)**: Check whether user-facing text is hardcoded or properly externalized into localization resource files (`arb`, `json`, `po`, etc.).
- **Dependency Hygiene**: Audit dependencies for deprecated, discontinued, or abandoned packages. Check lockfiles (`pnpm-lock.yaml`, `Cargo.lock`, `poetry.lock`) for consistency.
- **Structured Logging**: Replace raw console logging (`print`, `console.log`) with structured, leveled loggers (`debug`, `info`, `warn`, `error`).
- **Configuration & Environment**: Ensure API URLs, credentials, and feature flags are isolated in configuration files or environment variables.

### Diagnostic Questions:
- How easy is it for a new developer to onboard and run the project locally?
- Is there a clear roadmap for updating legacy dependencies?

---

## 5. Security & Sandbox Defense (安全性与沙箱防御)

### Audit Criteria:
- **Path Traversal (Directory Traversal)**: Verify that file paths provided by users, plugins, or configurations cannot escape their intended sandbox root via `../` or relative paths.
- **Shell Command Injection**: When executing shell commands (`Process.run`, `child_process.exec`, `subprocess.Popen`), ensure arguments are passed as separate argument lists rather than raw concatenated command strings.
- **Archive Extraction Safety (Zip Slip)**: Verify that `.zip`, `.tar.gz`, or package extraction routines validate destination entry paths before writing files to disk.
- **External Links & Content Security**: Ensure external browser links include `target="_blank" rel="noopener noreferrer"`.
- **Sensitive Credential Storage**: Passwords, API tokens, and secret keys must use OS-level secure storage (Keychain, Keystore, EncryptedSharedPreferences) rather than plaintext configuration files.

### Diagnostic Questions:
- Can an external script or malicious payload escape the application sandbox?
- Are user inputs sanitized before rendering as HTML or markdown?

---

## 6. Testing & Quality Assurance (测试覆盖与质量工程)

### Audit Criteria:
- **Core Business Logic Coverage**: Pure functions, mathematical algorithms, diff utilities, parser logic, and state reducers must have comprehensive unit test coverage.
- **Regression Tests**: Any past bugs or critical edge cases should have dedicated regression test cases.
- **Mocking & Isolation**: Network calls and platform APIs should have deterministic mocks or in-memory fakes to ensure tests can run in headless CI environments without external services.
- **Tiered Test Friendliness**: Ensure targeted tests can be executed quickly (< 30s) during atomic refactoring loops.

### Diagnostic Questions:
- What is the current line and branch test coverage percentage?
- Are there tests that fail intermittently (flaky tests)?
