# Remote Push & GitHub CI Monitoring Guide

Once all tasks in `IMPROVEMENTS.md` are implemented and verified locally, follow this guide to push changes and monitor continuous integration (CI) workflows on GitHub.

---

## 1. Pre-Push Verification

Before pushing to the remote repository, ensure:
1. `git status` shows a clean working tree (no uncommitted or untracked changes).
2. All local tests pass cleanly.
3. If `IMPROVEMENTS.md` was intended to be deleted upon completion, verify it has been removed and committed.

---

## 2. Git Push

Push the current branch to origin:

```bash
# Push current branch
git push origin <current-branch>
```

---

## 3. GitHub CI Monitoring via `gh` CLI

Use the GitHub CLI (`gh`) to monitor automated CI pipelines without leaving the terminal:

### 1. Check Recent Workflow Runs:
```bash
gh run list --limit 3
```

Output displays:
- Status: `✓` (success), `*` (in progress), `X` (failed)
- Workflow name
- Branch and commit message
- Run ID and elapsed duration

### 2. Live Stream / Watch Active CI Run:
```bash
gh run watch
```
This monitors the in-flight CI run until completion.

### 3. Inspect Failed CI Logs:
If a CI check fails:
```bash
# View summary of failed steps for the latest run
gh run view --log-failed

# Or view a specific run ID
gh run view <run-id> --log-failed
```

---

## 4. Remediation Protocol

If a remote CI job fails (e.g. OS-specific path separators, missing secrets, strict CI linters):
1. Read the exact failure log using `gh run view --log-failed`.
2. Replicate and fix the issue locally.
3. Verify with local test runner.
4. Commit: `fix(ci): <description of CI fix>`.
5. Push again and re-verify until all CI checks display green `✓`.
