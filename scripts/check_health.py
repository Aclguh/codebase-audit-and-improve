#!/usr/bin/env python3
"""
Project Health Inspector & Baseline Tool
Detects tech stacks, package managers, monorepo workspaces, git tree status,
and inspects .gitignore configuration for safe temporary roadmap tracking.
"""

import os
import sys
import json
import subprocess
import shutil
import glob
from pathlib import Path

# Ensure UTF-8 output encoding across all operating systems and Windows CI runners
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def detect_package_manager(cwd):
    """Detect Node.js package manager based on lockfiles."""
    if os.path.exists(os.path.join(cwd, "pnpm-lock.yaml")):
        return "pnpm"
    if os.path.exists(os.path.join(cwd, "bun.lockb")) or os.path.exists(os.path.join(cwd, "bun.lock")):
        return "bun"
    if os.path.exists(os.path.join(cwd, "yarn.lock")):
        return "yarn"
    return "npm"

def detect_monorepo(cwd):
    """Detect if project is a Monorepo workspace."""
    monorepo_indicators = []
    
    if os.path.exists(os.path.join(cwd, "pnpm-workspace.yaml")):
        monorepo_indicators.append("pnpm workspace")
    if os.path.exists(os.path.join(cwd, "turbo.json")):
        monorepo_indicators.append("Turborepo")
    if os.path.exists(os.path.join(cwd, "lerna.json")):
        monorepo_indicators.append("Lerna")
    if os.path.exists(os.path.join(cwd, "nx.json")):
        monorepo_indicators.append("Nx")
        
    pkg_json_path = os.path.join(cwd, "package.json")
    if os.path.exists(pkg_json_path):
        try:
            with open(pkg_json_path, "r", encoding="utf-8") as f:
                pkg_data = json.load(f)
                if "workspaces" in pkg_data:
                    monorepo_indicators.append("npm/yarn workspaces")
        except Exception:
            pass

    cargo_path = os.path.join(cwd, "Cargo.toml")
    if os.path.exists(cargo_path):
        try:
            with open(cargo_path, "r", encoding="utf-8", errors="ignore") as f:
                if "[workspace]" in f.read():
                    monorepo_indicators.append("Cargo workspace")
        except Exception:
            pass
            
    return monorepo_indicators

def parse_package_json(cwd, pkg_mgr):
    """Parse scripts in package.json if available."""
    pkg_path = os.path.join(cwd, "package.json")
    scripts = {}
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                scripts = json.load(f).get("scripts", {})
        except Exception:
            scripts = {}

    run_cmd = f"{pkg_mgr} run" if pkg_mgr != "npm" else "npm run"
    
    # Lint command
    if "lint" in scripts:
        lint_cmd = f"{run_cmd} lint"
    elif "check" in scripts:
        lint_cmd = f"{run_cmd} check"
    else:
        lint_cmd = f"{pkg_mgr} exec eslint ." if shutil.which(pkg_mgr) else "npx eslint ."

    # Test command
    if "test" in scripts:
        test_cmd = f"{pkg_mgr} test" if pkg_mgr in ("pnpm", "yarn", "bun") else "npm test"
    else:
        test_cmd = f"{pkg_mgr} test"

    # Coverage command
    if "test:coverage" in scripts:
        coverage_cmd = f"{run_cmd} test:coverage"
    elif "coverage" in scripts:
        coverage_cmd = f"{run_cmd} coverage"
    else:
        coverage_cmd = f"{test_cmd} -- --coverage"

    return lint_cmd, test_cmd, coverage_cmd

def detect_stack(cwd):
    """Detect all active tech stacks in the workspace."""
    stacks = []
    
    # 1. Flutter / Dart
    if os.path.exists(os.path.join(cwd, "pubspec.yaml")):
        has_flutter = shutil.which("flutter") is not None
        stacks.append({
            "name": "Flutter / Dart",
            "manifest": "pubspec.yaml",
            "lint_cmd": "flutter analyze" if has_flutter else "dart analyze",
            "test_cmd": "flutter test" if has_flutter else "dart test",
            "coverage_cmd": "flutter test --coverage" if has_flutter else "dart test --coverage"
        })
    
    # 2. Node.js / TypeScript / JavaScript
    if os.path.exists(os.path.join(cwd, "package.json")):
        pkg_mgr = detect_package_manager(cwd)
        lint_cmd, test_cmd, coverage_cmd = parse_package_json(cwd, pkg_mgr)
        stacks.append({
            "name": f"Node.js / TypeScript / JavaScript ({pkg_mgr})",
            "manifest": "package.json",
            "package_manager": pkg_mgr,
            "lint_cmd": lint_cmd,
            "test_cmd": test_cmd,
            "coverage_cmd": coverage_cmd
        })
    
    # 3. Python
    py_files = ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile"]
    matched_py = [f for f in py_files if os.path.exists(os.path.join(cwd, f))]
    if matched_py:
        # Detect runner
        runner = "python -m"
        if os.path.exists(os.path.join(cwd, "poetry.lock")) and shutil.which("poetry"):
            runner = "poetry run"
        elif os.path.exists(os.path.join(cwd, "uv.lock")) and shutil.which("uv"):
            runner = "uv run"
        elif os.path.exists(os.path.join(cwd, "pdm.lock")) and shutil.which("pdm"):
            runner = "pdm run"
            
        lint_cmd = f"{runner} ruff check ." if shutil.which("ruff") else f"{runner} flake8"
        test_cmd = f"{runner} pytest" if shutil.which("pytest") else f"{runner} unittest discover"
        coverage_cmd = f"{runner} pytest --cov=." if shutil.which("pytest") else f"{runner} coverage run -m unittest"
        
        stacks.append({
            "name": "Python",
            "manifest": matched_py[0],
            "lint_cmd": lint_cmd,
            "test_cmd": test_cmd,
            "coverage_cmd": coverage_cmd
        })
    
    # 4. Rust
    if os.path.exists(os.path.join(cwd, "Cargo.toml")):
        stacks.append({
            "name": "Rust",
            "manifest": "Cargo.toml",
            "lint_cmd": "cargo clippy -- -D warnings",
            "test_cmd": "cargo test",
            "coverage_cmd": "cargo tarpaulin" if shutil.which("cargo-tarpaulin") else "cargo test"
        })
    
    # 5. Go
    if os.path.exists(os.path.join(cwd, "go.mod")):
        stacks.append({
            "name": "Go",
            "manifest": "go.mod",
            "lint_cmd": "golangci-lint run" if shutil.which("golangci-lint") else "go vet ./...",
            "test_cmd": "go test ./...",
            "coverage_cmd": "go test -coverprofile=coverage.out ./..."
        })

    # 6. Java / Kotlin (Maven / Gradle)
    if os.path.exists(os.path.join(cwd, "pom.xml")):
        mvn_cmd = "./mvnw" if os.path.exists(os.path.join(cwd, "mvnw")) else "mvn"
        stacks.append({
            "name": "Java (Maven)",
            "manifest": "pom.xml",
            "lint_cmd": f"{mvn_cmd} checkstyle:check",
            "test_cmd": f"{mvn_cmd} test",
            "coverage_cmd": f"{mvn_cmd} jacoco:report"
        })
    elif any(os.path.exists(os.path.join(cwd, f)) for f in ["build.gradle", "build.gradle.kts"]):
        is_win = sys.platform.startswith("win")
        gradle_cmd = "gradlew.bat" if is_win and os.path.exists(os.path.join(cwd, "gradlew.bat")) else (
            "./gradlew" if os.path.exists(os.path.join(cwd, "gradlew")) else "gradle"
        )
        stacks.append({
            "name": "Java / Kotlin (Gradle)",
            "manifest": "build.gradle(.kts)",
            "lint_cmd": f"{gradle_cmd} check",
            "test_cmd": f"{gradle_cmd} test",
            "coverage_cmd": f"{gradle_cmd} jacocoTestReport"
        })

    # 7. .NET / C#
    csproj_files = list(glob.glob(os.path.join(cwd, "*.csproj"))) + list(glob.glob(os.path.join(cwd, "*.sln")))
    if csproj_files:
        stacks.append({
            "name": ".NET / C#",
            "manifest": os.path.basename(csproj_files[0]),
            "lint_cmd": "dotnet format --verify-no-changes",
            "test_cmd": "dotnet test",
            "coverage_cmd": "dotnet test /p:CollectCoverage=true"
        })

    # 8. C / C++ (CMake)
    if os.path.exists(os.path.join(cwd, "CMakeLists.txt")):
        stacks.append({
            "name": "C / C++ (CMake)",
            "manifest": "CMakeLists.txt",
            "lint_cmd": "cppcheck --enable=warning,style .",
            "test_cmd": "ctest --output-on-failure",
            "coverage_cmd": "ctest"
        })

    # 9. PHP
    if os.path.exists(os.path.join(cwd, "composer.json")):
        stacks.append({
            "name": "PHP (Composer)",
            "manifest": "composer.json",
            "lint_cmd": "composer run-script lint" if shutil.which("composer") else "./vendor/bin/phpcs",
            "test_cmd": "composer test" if shutil.which("composer") else "./vendor/bin/phpunit",
            "coverage_cmd": "./vendor/bin/phpunit --coverage-text"
        })

    # 10. Ruby
    if os.path.exists(os.path.join(cwd, "Gemfile")):
        stacks.append({
            "name": "Ruby (Bundler)",
            "manifest": "Gemfile",
            "lint_cmd": "bundle exec rubocop",
            "test_cmd": "bundle exec rspec",
            "coverage_cmd": "bundle exec rspec"
        })
        
    return stacks

def check_git_status(cwd):
    """Check git repository health, branch protection status, and dirty tree status."""
    result = {
        "is_git": False,
        "branch": None,
        "is_clean": True,
        "is_protected_branch": False,
        "dirty_files_count": 0,
        "remote_origin": None
    }
    
    git_dir = os.path.join(cwd, ".git")
    if not (os.path.exists(git_dir) or shutil.which("git")):
        return result
        
    try:
        # Check branch
        p_branch = subprocess.run(["git", "branch", "--show-current"], cwd=cwd, capture_output=True, text=True, check=True)
        branch = p_branch.stdout.strip()
        result["is_git"] = True
        result["branch"] = branch
        result["is_protected_branch"] = branch.lower() in ("main", "master", "release", "prod", "production")
        
        # Check dirty working tree
        p_status = subprocess.run(["git", "status", "--porcelain"], cwd=cwd, capture_output=True, text=True, check=True)
        dirty_lines = [line for line in p_status.stdout.splitlines() if line.strip()]
        result["is_clean"] = len(dirty_lines) == 0
        result["dirty_files_count"] = len(dirty_lines)
        
        # Check remote origin
        p_remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=cwd, capture_output=True, text=True)
        if p_remote.returncode == 0:
            result["remote_origin"] = p_remote.stdout.strip()
    except Exception:
        pass
        
    return result

def check_gitignore(cwd):
    """Inspect .gitignore configuration to ensure IMPROVEMENTS.md is ignored."""
    gitignore_path = os.path.join(cwd, ".gitignore")
    if not os.path.exists(gitignore_path):
        return False, "Missing .gitignore file", gitignore_path
    
    with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        # If line negates, continue
        if line.startswith("!"):
            continue
        line_clean = line.lstrip("/")
        if line_clean.lower() in ("improvements.md", "*.md"):
            return True, "Found explicit ignore rule", gitignore_path
            
    return False, "IMPROVEMENTS.md not ignored", gitignore_path

def add_to_gitignore(cwd):
    """Safely append IMPROVEMENTS.md to .gitignore."""
    gitignore_path = os.path.join(cwd, ".gitignore")
    entry = "\n# Temporary audit and improvement roadmap\nIMPROVEMENTS.md\n"
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "a", encoding="utf-8") as f:
            f.write(entry)
    else:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(entry.lstrip())
    return True

def run_baseline_command(cmd, cwd):
    """Execute a single diagnostic command and capture summary."""
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=120)
        return {
            "cmd": cmd,
            "exit_code": p.returncode,
            "output_lines": len(p.stdout.splitlines()) + len(p.stderr.splitlines()),
            "success": p.returncode == 0,
            "stdout_preview": p.stdout.strip()[:300],
            "stderr_preview": p.stderr.strip()[:300]
        }
    except Exception as e:
        return {
            "cmd": cmd,
            "exit_code": -1,
            "success": False,
            "error": str(e)
        }

def main():
    cwd = os.getcwd()
    as_json = "--json" in sys.argv
    run_baseline = "--run-baseline" in sys.argv
    fix_gitignore = "--fix-gitignore" in sys.argv
    
    # 1. Monorepo detection
    monorepo = detect_monorepo(cwd)
    
    # 2. Stack detection
    stacks = detect_stack(cwd)
    
    # 3. Git status
    git_info = check_git_status(cwd)
    
    # 4. .gitignore check
    is_ignored, gitignore_msg, gitignore_path = check_gitignore(cwd)
    if not is_ignored and fix_gitignore:
        add_to_gitignore(cwd)
        is_ignored = True
        gitignore_msg = "Appended IMPROVEMENTS.md to .gitignore"
        
    baseline_results = []
    if run_baseline and stacks:
        primary_stack = stacks[0]
        if primary_stack.get("lint_cmd"):
            baseline_results.append(run_baseline_command(primary_stack["lint_cmd"], cwd))
        if primary_stack.get("test_cmd"):
            baseline_results.append(run_baseline_command(primary_stack["test_cmd"], cwd))

    data = {
        "working_directory": cwd,
        "monorepo_indicators": monorepo,
        "detected_stacks": stacks,
        "git_status": git_info,
        "gitignore": {
            "is_protected": is_ignored,
            "message": gitignore_msg,
            "path": gitignore_path
        },
        "baseline_checks": baseline_results
    }

    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    # Standard human-readable console report
    print("=" * 65)
    print("Codebase Health & Stack Inspector")
    print(f"Working Directory: {cwd}")
    if monorepo:
        print(f"Workspace Architecture: Monorepo ({', '.join(monorepo)})")
    print("=" * 65)
    
    # 1. Tech Stacks
    if not stacks:
        print("[!] No standard tech stack manifest detected in current directory.")
    else:
        print("\n[+] Detected Stacks:")
        for s in stacks:
            print(f"  - {s['name']} (manifest: {s.get('manifest', 'N/A')})")
            print(f"    * Linter command:   {s['lint_cmd']}")
            print(f"    * Test command:     {s['test_cmd']}")
            print(f"    * Coverage command: {s['coverage_cmd']}")
            
    # 2. Git Status & Safety Guard
    print("\n[+] Git Repository Guard:")
    if git_info["is_git"]:
        branch_desc = f"{git_info['branch']}"
        if git_info["is_protected_branch"]:
            branch_desc += " [PROTECTED BRANCH - Recommendation: create feature branch for PR]"
        print(f"  - Current Branch: {branch_desc}")
        if git_info["is_clean"]:
            print("  ✓ Working tree is clean (Safe to start atomic loop)")
        else:
            print(f"  ✗ Working tree is DIRTY ({git_info['dirty_files_count']} uncommitted file(s)!)")
            print("    Recommendation: Commit or stash uncommitted changes before starting.")
    else:
        print("  ! Current directory is not a Git repository.")

    # 3. .gitignore Protection Check
    print("\n[+] Checking .gitignore configuration:")
    if is_ignored:
        print("  ✓ IMPROVEMENTS.md is properly protected in .gitignore")
    else:
        print("  ✗ IMPROVEMENTS.md is NOT found in .gitignore!")
        print("    Recommendation: Run 'python scripts/check_health.py --fix-gitignore' or append manually.")

    # 4. Baseline command results (if requested)
    if baseline_results:
        print("\n[+] Baseline Command Execution:")
        for res in baseline_results:
            status_text = "PASS" if res.get("success") else f"FAIL (Exit code {res.get('exit_code')})"
            print(f"  - `{res['cmd']}`: {status_text}")

    print("\n" + "=" * 65)

if __name__ == "__main__":
    main()
