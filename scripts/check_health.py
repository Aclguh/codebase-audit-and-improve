#!/usr/bin/env python3
"""
Project Health Inspector & Baseline Tool
Detects tech stacks, package managers, monorepo workspaces, git tree status,
and inspects .gitignore configuration for safe temporary roadmap tracking.
"""

import os
import sys
import re
import json
import subprocess
import shutil
import glob
import fnmatch
from pathlib import Path

# Precompiled credential sanitization pattern for git remote URLs
REMOTE_URL_CREDENTIAL_RE = re.compile(r'^(https?://)(?:[^:@/\s]+)(?::(?:[^@/\s]+))?@')

def sanitize_remote_url(url):
    """Sanitize embedded credentials from git remote URL to prevent leaking tokens or passwords."""
    if not url or not isinstance(url, str):
        return url
    return REMOTE_URL_CREDENTIAL_RE.sub(r'\1***@', url)

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
    if os.path.exists(os.path.join(cwd, "rush.json")):
        monorepo_indicators.append("Rush")
    if os.path.exists(os.path.join(cwd, "go.work")):
        monorepo_indicators.append("Go workspace")
        
    pkg_json_path = os.path.join(cwd, "package.json")
    if os.path.exists(pkg_json_path):
        try:
            # utf-8-sig tolerates the BOM Windows editors write ahead of the
            # JSON body, which json.load would otherwise reject outright.
            with open(pkg_json_path, "r", encoding="utf-8-sig") as f:
                pkg_data = json.load(f)
            if isinstance(pkg_data, dict):
                ws = pkg_data.get("workspaces")
                if ws and (isinstance(ws, list) or isinstance(ws, dict)):
                    monorepo_indicators.append("npm/yarn workspaces")
        except (OSError, ValueError):
            # Unreadable or malformed manifests must not abort detection.
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
            # Read as utf-8-sig so a BOM-prefixed manifest (common on Windows)
            # still yields its scripts instead of silently falling back to defaults.
            with open(pkg_path, "r", encoding="utf-8-sig") as f:
                pkg_data = json.load(f)
            if isinstance(pkg_data, dict):
                scripts = pkg_data.get("scripts", {})
        except (OSError, ValueError):
            scripts = {}
    # A legitimate package.json may carry a non-mapping "scripts" value (for
    # example null or a number). Treat anything else as no scripts so the
    # membership probes below never raise and abort stack detection.
    if not isinstance(scripts, dict):
        scripts = {}

    run_cmd = f"{pkg_mgr} run" if pkg_mgr != "npm" else "npm run"
    
    # Lint command
    if "lint" in scripts:
        lint_cmd = f"{run_cmd} lint"
    elif "check" in scripts:
        lint_cmd = f"{run_cmd} check"
    elif pkg_mgr == "bun":
        # Bun has no `exec` subcommand; `bunx` is its package-binary runner.
        lint_cmd = "bunx eslint ." if shutil.which("bun") else "npx eslint ."
    else:
        lint_cmd = f"{pkg_mgr} exec eslint ." if shutil.which(pkg_mgr) else "npx eslint ."

    # Test command. `bun test` runs Bun's built-in test runner, so a declared
    # package.json "test" script must be invoked explicitly with `bun run`.
    if "test" in scripts:
        test_cmd = "bun run test" if pkg_mgr == "bun" else (
            f"{pkg_mgr} test" if pkg_mgr in ("pnpm", "yarn") else "npm test"
        )
    else:
        test_cmd = "bun test" if pkg_mgr == "bun" else f"{pkg_mgr} test"

    # Coverage command
    if "test:coverage" in scripts:
        coverage_cmd = f"{run_cmd} test:coverage"
    elif "coverage" in scripts:
        coverage_cmd = f"{run_cmd} coverage"
    elif pkg_mgr == "bun":
        # `bun run` forwards flags directly; npm-style `--` is unnecessary.
        coverage_cmd = f"{test_cmd} --coverage"
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
    py_files = [
        "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
        "requirements-dev.txt", "Pipfile", "poetry.lock", "uv.lock",
        "pdm.lock", "tox.ini", "environment.yml"
    ]
    matched_py = [f for f in py_files if os.path.exists(os.path.join(cwd, f))]
    has_py_source = False
    manifest_name = matched_py[0] if matched_py else None

    if not matched_py:
        has_root_py = bool(list(glob.glob(os.path.join(cwd, "*.py"))))
        if has_root_py:
            has_py_source = True
            manifest_name = os.path.basename(list(glob.glob(os.path.join(cwd, "*.py")))[0])
        else:
            for candidate_dir in ["tests", "scripts", "src"]:
                d_path = os.path.join(cwd, candidate_dir)
                if not os.path.isdir(d_path):
                    continue
                try:
                    entries = os.listdir(d_path)
                except OSError:
                    # Unreadable candidate directory (permissions, concurrent
                    # removal) must not abort the whole stack detection.
                    continue
                if any(f.endswith(".py") for f in entries):
                    has_py_source = True
                    manifest_name = f"{candidate_dir}/"
                    break

    if matched_py or has_py_source:
        # Detect runner
        runner = "python -m"
        if os.path.exists(os.path.join(cwd, "poetry.lock")) and shutil.which("poetry"):
            runner = "poetry run"
        elif os.path.exists(os.path.join(cwd, "uv.lock")) and shutil.which("uv"):
            runner = "uv run"
        elif os.path.exists(os.path.join(cwd, "pdm.lock")) and shutil.which("pdm"):
            runner = "pdm run"
            
        # Managed runners (poetry/uv/pdm) do not expose `unittest` or
        # `compileall` as console scripts, so module-based commands must go
        # through the interpreter of that environment.
        module_runner = "python -m" if runner == "python -m" else f"{runner} python -m"

        has_tests_dir = os.path.isdir(os.path.join(cwd, "tests"))
        unittest_cmd = f"{module_runner} unittest discover -s tests" if has_tests_dir else f"{module_runner} unittest discover"
        unittest_cov_cmd = f"{module_runner} coverage run -m unittest discover -s tests" if has_tests_dir else f"{module_runner} coverage run -m unittest"

        has_ruff = shutil.which("ruff") is not None
        has_flake8 = shutil.which("flake8") is not None
        if has_ruff:
            lint_cmd = f"{runner} ruff check ."
        elif has_flake8:
            lint_cmd = f"{runner} flake8"
        else:
            lint_cmd = f"{module_runner} compileall -q ."

        has_pytest = shutil.which("pytest") is not None
        test_cmd = f"{runner} pytest" if has_pytest else unittest_cmd
        if has_pytest:
            coverage_cmd = f"{runner} coverage run -m pytest"
        else:
            coverage_cmd = unittest_cov_cmd
        
        stacks.append({
            "name": "Python",
            "manifest": manifest_name or "python",
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

    # 6. Java / Kotlin (Maven)
    if os.path.exists(os.path.join(cwd, "pom.xml")):
        has_mvnw = os.path.exists(os.path.join(cwd, "mvnw"))
        has_mvnw_cmd = os.path.exists(os.path.join(cwd, "mvnw.cmd"))
        if sys.platform.startswith("win"):
            # cmd.exe cannot run the POSIX ./mvnw shell script; prefer the
            # wrapper's .cmd entry point and fall back to the CLI.
            mvn_cmd = "mvnw.cmd" if has_mvnw_cmd else "mvn"
        else:
            mvn_cmd = "./mvnw" if has_mvnw else "mvn"
        stacks.append({
            "name": "Java (Maven)",
            "manifest": "pom.xml",
            "lint_cmd": f"{mvn_cmd} checkstyle:check",
            "test_cmd": f"{mvn_cmd} test",
            "coverage_cmd": f"{mvn_cmd} jacoco:report"
        })

    # 7. Java / Kotlin (Gradle)
    gradle_manifests = ["build.gradle.kts", "build.gradle", "settings.gradle.kts", "settings.gradle"]
    matched_gradle = [f for f in gradle_manifests if os.path.exists(os.path.join(cwd, f))]
    if matched_gradle:
        is_win = sys.platform.startswith("win")
        gradle_cmd = "gradlew.bat" if is_win and os.path.exists(os.path.join(cwd, "gradlew.bat")) else (
            "./gradlew" if os.path.exists(os.path.join(cwd, "gradlew")) else "gradle"
        )
        stacks.append({
            "name": "Java / Kotlin (Gradle)",
            "manifest": matched_gradle[0],
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
        
    # 11. Swift (Swift Package Manager / Xcode)
    if os.path.exists(os.path.join(cwd, "Package.swift")):
        has_swiftlint = shutil.which("swiftlint") is not None
        stacks.append({
            "name": "Swift (SPM)",
            "manifest": "Package.swift",
            "lint_cmd": "swiftlint" if has_swiftlint else "swift package describe",
            "test_cmd": "swift test",
            "coverage_cmd": "swift test --enable-code-coverage"
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
    
    if not shutil.which("git"):
        result["git_error"] = "git executable not found in PATH"
        return result

    status_verified = False
    try:
        p_check = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=cwd, capture_output=True, text=True, errors="replace", timeout=15)
        if p_check.returncode != 0:
            return result
        result["is_git"] = True

        # Check branch
        p_branch = subprocess.run(["git", "branch", "--show-current"], cwd=cwd, capture_output=True, text=True, errors="replace", timeout=15)
        branch = p_branch.stdout.strip() if p_branch.returncode == 0 else ""
        if not branch:
            p_head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=cwd, capture_output=True, text=True, errors="replace", timeout=15)
            if p_head.returncode == 0 and p_head.stdout.strip():
                branch = f"detached@{p_head.stdout.strip()}"
            else:
                branch = "HEAD (detached)"
        result["branch"] = branch
        b_lower = branch.lower()
        result["is_protected_branch"] = (
            b_lower in ("main", "master", "trunk", "release", "prod", "production")
            or b_lower.startswith(("release/", "releases/", "prod/", "production/", "release-", "prod-"))
        )

        # Check dirty working tree. If git status cannot be trusted, fail closed
        # instead of reporting a clean tree to the pre-flight safety guard.
        p_status = subprocess.run(["git", "status", "--porcelain"], cwd=cwd, capture_output=True, text=True, errors="replace", timeout=15)
        if p_status.returncode != 0:
            detail = (p_status.stderr or p_status.stdout).strip()
            result["is_clean"] = False
            result["status_error"] = detail or f"git status exited with code {p_status.returncode}"
        else:
            dirty_lines = [line for line in p_status.stdout.splitlines() if line.strip()]
            result["is_clean"] = len(dirty_lines) == 0
            result["dirty_files_count"] = len(dirty_lines)
            status_verified = True
        
        # Check remote origin
        p_remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=cwd, capture_output=True, text=True, errors="replace", timeout=15)
        if p_remote.returncode == 0 and p_remote.stdout.strip():
            result["remote_origin"] = sanitize_remote_url(p_remote.stdout.strip())

        else:
            p_remotes = subprocess.run(["git", "remote"], cwd=cwd, capture_output=True, text=True, errors="replace", timeout=15)
            if p_remotes.returncode == 0 and p_remotes.stdout.strip():
                first_remote = p_remotes.stdout.strip().splitlines()[0].strip()
                p_first = subprocess.run(["git", "remote", "get-url", first_remote], cwd=cwd, capture_output=True, text=True, errors="replace", timeout=15)
                if p_first.returncode == 0 and p_first.stdout.strip():
                    result["remote_origin"] = sanitize_remote_url(p_first.stdout.strip())


    except Exception as e:
        result["git_error"] = str(e)
        # A timeout or unexpected failure before the status check completed
        # must never be reported as a clean working tree.
        if result.get("is_git") and not status_verified:
            result["is_clean"] = False
            result["status_error"] = f"Unable to verify working tree status: {e}"

    return result

def git_reports_ignored(cwd):
    """Return Git's authoritative ignore verdict for IMPROVEMENTS.md.

    Returns True/False when Git can answer, or None when Git is unavailable or
    the directory is not a work tree (callers then fall back to pattern
    matching). This matters on case-sensitive filesystems, where a pattern such
    as ``improvements.md`` does not actually ignore ``IMPROVEMENTS.md``.
    """
    if not shutil.which("git"):
        return None
    try:
        probe = subprocess.run(
            ["git", "check-ignore", "-q", "--", "IMPROVEMENTS.md"],
            cwd=cwd,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=15,
            check=False,
        )
    except Exception:
        return None
    if probe.returncode == 0:
        return True
    if probe.returncode == 1:
        return False
    return None

def check_gitignore(cwd):
    """Inspect .gitignore configuration to ensure IMPROVEMENTS.md is ignored."""
    gitignore_path = os.path.join(cwd, ".gitignore")
    git_ignored = git_reports_ignored(cwd)
    if git_ignored is not None:
        if git_ignored:
            return True, "Confirmed ignored by git check-ignore", gitignore_path
        return False, "Not ignored by git check-ignore", gitignore_path

    if not os.path.exists(gitignore_path):
        return False, "Missing .gitignore file", gitignore_path

    try:
        with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except OSError as e:
        # Unreadable .gitignore (directory, permissions, lock) must not crash
        # the pre-flight check; report it as unprotected instead.
        return False, f"Unable to read .gitignore: {e}", gitignore_path

    # Later rules override earlier ones, so a negated rule (for example
    # ``!IMPROVEMENTS.md`` after ``*.md``) must be able to un-ignore the file.
    ignored = False
    message = "Found matching ignore pattern"
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        negate = line.startswith("!")
        if negate:
            line = line[1:].strip()
            if not line:
                continue
        line_clean = line.lstrip("/")
        # fnmatch.fnmatch normalizes case through os.path.normcase, so the
        # fallback follows Git's platform semantics: case-insensitive on
        # Windows and case-sensitive on POSIX filesystems.
        if fnmatch.fnmatch("IMPROVEMENTS.md", line_clean):
            ignored = not negate
            if line_clean.lower() in ("improvements.md", "*.md"):
                message = "Found explicit ignore rule"
            else:
                message = "Found matching ignore pattern"

    if ignored:
        return True, message, gitignore_path
    return False, "IMPROVEMENTS.md not ignored", gitignore_path

def add_to_gitignore(cwd):
    """Safely append IMPROVEMENTS.md to .gitignore."""
    abs_cwd = os.path.abspath(cwd)
    gitignore_path = os.path.abspath(os.path.join(abs_cwd, ".gitignore"))
    # Strictly ensure destination file resides directly within target workspace
    try:
        if os.path.dirname(gitignore_path) != abs_cwd or Path(gitignore_path).resolve().parent != Path(abs_cwd).resolve():
            return False
    except Exception:
        return False
    entry = "\n# Temporary audit and improvement roadmap\nIMPROVEMENTS.md\n"
    try:
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "a", encoding="utf-8") as f:
                f.write(entry)
        else:
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write(entry.lstrip())
    except OSError:
        # Read-only checkouts, .gitignore directories and locked files must
        # surface as a failed fix rather than an unhandled exception.
        return False
    return True

def run_baseline_command(cmd, cwd):
    """Execute a single diagnostic command and capture summary."""
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, errors="replace", timeout=120)
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
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: check-health [options]")
        print("   or: python scripts/check_health.py [options]\n")
        print("Project Health Inspector & Baseline Tool")
        print("Inspects project tech stacks, git repository status, and .gitignore safety.\n")
        print("Options:")
        print("  --json           Output full inspection results in JSON format")
        print("  --run-baseline   Execute project linters and test suites to record baseline")
        print("  --fix-gitignore  Safely append IMPROVEMENTS.md to .gitignore if missing")
        print("  -h, --help       Show this help message and exit")
        return

    valid_flags = {"--json", "--run-baseline", "--fix-gitignore"}
    unknown = [arg for arg in sys.argv[1:] if arg not in valid_flags]
    if unknown:
        print(f"[!] Error: Unknown option(s): {', '.join(unknown)}", file=sys.stderr)
        print("Run 'python scripts/check_health.py --help' for usage.", file=sys.stderr)
        sys.exit(2)

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
        if add_to_gitignore(cwd):
            # Re-read the file (and Git's verdict) so a write that did not
            # actually take effect is never reported as protected.
            is_ignored, recheck_msg, gitignore_path = check_gitignore(cwd)
            if is_ignored:
                gitignore_msg = "Appended IMPROVEMENTS.md to .gitignore"
            else:
                gitignore_msg = f"Appended IMPROVEMENTS.md but it is still not ignored: {recheck_msg}"
        else:
            gitignore_msg = "Failed to append IMPROVEMENTS.md to .gitignore"
        
    baseline_results = []
    if run_baseline and stacks:
        for primary_stack in stacks:
            if primary_stack.get("lint_cmd"):
                res = run_baseline_command(primary_stack["lint_cmd"], cwd)
                res["stack"] = primary_stack["name"]
                baseline_results.append(res)
            if primary_stack.get("test_cmd"):
                res = run_baseline_command(primary_stack["test_cmd"], cwd)
                res["stack"] = primary_stack["name"]
                baseline_results.append(res)

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
        if git_info.get("status_error"):
            print(f"  ✗ Unable to verify working tree status: {git_info['status_error']}")
            print("    Recommendation: Resolve the git error before starting.")
        elif git_info["is_clean"]:
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
            stack_label = f" [{res['stack']}]" if "stack" in res else ""
            print(f"  - `{res['cmd']}`{stack_label}: {status_text}")
            if not res.get("success") and res.get("error"):
                print(f"    Error detail: {res['error']}")

    print("\n" + "=" * 65)

if __name__ == "__main__":
    main()
