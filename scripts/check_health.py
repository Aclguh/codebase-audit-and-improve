#!/usr/bin/env python3
"""
Project Health Inspector & Baseline Tool
Detects tech stacks, inspects .gitignore configuration, and checks baseline health commands.
"""

import os
import sys
import subprocess
import shutil

def detect_stack(cwd):
    stacks = []
    
    # Flutter / Dart
    if os.path.exists(os.path.join(cwd, "pubspec.yaml")):
        stacks.append({
            "name": "Flutter / Dart",
            "lint_cmd": "flutter analyze" if shutil.which("flutter") else "dart analyze",
            "test_cmd": "flutter test" if shutil.which("flutter") else "dart test",
            "coverage_cmd": "flutter test --coverage" if shutil.which("flutter") else "dart test --coverage"
        })
    
    # Node / TypeScript / JavaScript
    if os.path.exists(os.path.join(cwd, "package.json")):
        stacks.append({
            "name": "Node.js / TypeScript / JavaScript",
            "lint_cmd": "npm run lint",
            "test_cmd": "npm test",
            "coverage_cmd": "npm run test:coverage"
        })
    
    # Python
    if any(os.path.exists(os.path.join(cwd, f)) for f in ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile"]):
        stacks.append({
            "name": "Python",
            "lint_cmd": "ruff check ." if shutil.which("ruff") else "flake8",
            "test_cmd": "pytest",
            "coverage_cmd": "pytest --cov=."
        })
    
    # Rust
    if os.path.exists(os.path.join(cwd, "Cargo.toml")):
        stacks.append({
            "name": "Rust",
            "lint_cmd": "cargo clippy -- -D warnings",
            "test_cmd": "cargo test",
            "coverage_cmd": "cargo tarpaulin" if shutil.which("cargo-tarpaulin") else "cargo test"
        })
    
    # Go
    if os.path.exists(os.path.join(cwd, "go.mod")):
        stacks.append({
            "name": "Go",
            "lint_cmd": "golangci-lint run" if shutil.which("golangci-lint") else "go vet ./...",
            "test_cmd": "go test ./...",
            "coverage_cmd": "go test -coverprofile=coverage.out ./..."
        })
        
    return stacks

def check_gitignore(cwd):
    gitignore_path = os.path.join(cwd, ".gitignore")
    if not os.path.exists(gitignore_path):
        return False, "Missing .gitignore file"
    
    with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    has_improvements = "IMPROVEMENTS.md" in content or "improvements.md" in content.lower()
    return has_improvements, gitignore_path

def main():
    cwd = os.getcwd()
    print("=" * 60)
    print("Codebase Health & Stack Inspector")
    print(f"Working Directory: {cwd}")
    print("=" * 60)
    
    # 1. Stack Detection
    stacks = detect_stack(cwd)
    if not stacks:
        print("[!] No standard tech stack manifest detected in current directory.")
    else:
        print("\n[+] Detected Stacks:")
        for s in stacks:
            print(f"  - {s['name']}")
            print(f"    * Linter command:  {s['lint_cmd']}")
            print(f"    * Test command:    {s['test_cmd']}")
            print(f"    * Coverage command: {s['coverage_cmd']}")
            
    # 2. .gitignore Protection Check
    print("\n[+] Checking .gitignore configuration:")
    is_ignored, msg = check_gitignore(cwd)
    if is_ignored:
        print("  ✓ IMPROVEMENTS.md is properly protected in .gitignore")
    else:
        print("  ✗ IMPROVEMENTS.md is NOT found in .gitignore!")
        print("    Recommendation: Append 'IMPROVEMENTS.md' to .gitignore before creating tracking documents.")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
