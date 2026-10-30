# Remote Push, Branch Protection & GitHub CI Monitoring Guide

Once all tasks in `IMPROVEMENTS.md` are implemented and verified locally, follow this guide to handle document lifecycle, branch protection, pull requests, and continuous integration (CI) workflows on GitHub.

---

## 1. Pre-Push Verification & Document Lifecycle

Before pushing to the remote repository, ensure:
1. `git status` shows a clean working tree (no uncommitted or untracked changes).
2. Full project regression tests and linters pass cleanly.
3. **Document Lifecycle Options**:
   - **Option A: Archive Mode (Recommended)**:
     Move the completed roadmap to `docs/audits/` so valuable architectural decisions and metrics are retained:
     ```bash
     mkdir -p docs/audits
     mv IMPROVEMENTS.md docs/audits/$(date +%Y-%m-%d)-codebase-improvements.md
     git add docs/audits/
     git commit -m "docs(audit): archive completed improvements roadmap"
     ```
   - **Option B: Cleanup Mode (Temporary Planning)**:
     If the user requested deleting upon 100% completion:
     ```bash
     rm IMPROVEMENTS.md
     git commit -am "chore: remove completed temporary roadmap IMPROVEMENTS.md"
     ```

---

## 2. Branch Protection & Safe PR Workflow

Always check whether the current branch is a protected branch (`main`, `master`, `release`, `prod`):

```bash
git branch --show-current
```

### Case A: On a Protected Branch (`main` / `master`)
Never push direct commits to a protected branch in collaborative repositories. Instead, promote changes to a dedicated feature branch and open a Pull Request:

1. Create a feature branch with all commits:
   ```bash
   BRANCH_NAME="refactor/audit-improvements-$(date +%Y%m%d)"
   git checkout -b "$BRANCH_NAME"
   git push -u origin "$BRANCH_NAME"
   ```
2. Create Pull Request using GitHub CLI (`gh`):
   ```bash
   gh pr create \
     --title "refactor: codebase health audit and atomic improvements" \
     --body "Automated audit and implementation pass across architecture, code quality, security, and test coverage."
   ```

### Case B: On a Feature / Topic Branch
Push directly to origin:
```bash
git push origin $(git branch --show-current)
```

---

## 3. GitHub CI Monitoring via `gh` CLI

Use the GitHub CLI (`gh`) to monitor automated CI pipelines:

### 1. Verify GitHub CLI Authentication:
```bash
gh auth status
```
*Note*: If `gh` is not installed or unauthenticated, inform the user with the PR URL to check CI in the GitHub web interface.

### 2. Check Recent Workflow Runs:
```bash
gh run list --limit 3
```

### 3. Live Stream / Watch Active CI Run:
```bash
gh run watch
```
Or if watching a PR:
```bash
gh pr checks --watch
```

### 4. Inspect Failed CI Logs:
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
