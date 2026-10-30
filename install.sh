#!/usr/bin/env bash
# Multi-Agent Installer for improve and improve-all
# Supports Antigravity, Claude Code, Cursor, Continue.dev, DeepSeek Harness (dsh), and OpenAI Codex
# Deduplicated & clean: ensures each agent sees exactly ONE /improve and ONE /improve-all entry
set -e

TARGET="${1:-all}"
WORKSPACE=false

for arg in "$@"; do
    case "$arg" in
        --workspace) WORKSPACE=true ;;
        --target=*) TARGET="${arg#*=}" ;;
        antigravity|claude|cursor|continue|deepseek|codex|all) TARGET="$arg" ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_DIR="$(pwd)"
USER_HOME="${HOME}"

install_skill_files() {
    local dest="$1"
    local skill_name="$2"
    mkdir -p "${dest}"
    rm -rf "${dest}"/*
    cp -R "${SCRIPT_DIR}/references" "${dest}/"
    cp -R "${SCRIPT_DIR}/scripts" "${dest}/"
    rm -rf "${dest}/scripts/__pycache__"
    if [ -f "${SCRIPT_DIR}/LICENSE" ]; then
        cp "${SCRIPT_DIR}/LICENSE" "${dest}/"
    fi
    if [ "${skill_name}" == "improve-all" ]; then
        cp -f "${SCRIPT_DIR}/skills/improve-all/SKILL.md" "${dest}/SKILL.md"
    else
        cp -f "${SCRIPT_DIR}/skills/improve/SKILL.md" "${dest}/SKILL.md"
    fi
}

cleanup_legacy_duplicates() {
    # Remove redundant legacy commands that cause duplicate slash commands in Claude Code
    rm -f "${USER_HOME}/.claude/commands/improve.md" "${USER_HOME}/.claude/commands/improve-all.md"
    rmdir "${USER_HOME}/.claude/commands" 2>/dev/null || true

    # Remove global ~/.cursor/commands (which Claude Code auto-scans and duplicates)
    rm -f "${USER_HOME}/.cursor/commands/improve.md" "${USER_HOME}/.cursor/commands/improve-all.md"
    rmdir "${USER_HOME}/.cursor/commands" 2>/dev/null || true

    # Remove duplicate ~/.codex/skills if ~/.agents/skills exists (Codex scans both roots, duplicating entries in Codex Desktop)
    if [ -d "${USER_HOME}/.agents/skills/improve" ]; then
        rm -rf "${USER_HOME}/.codex/skills/improve" "${USER_HOME}/.codex/skills/improve-all"
    fi
}

install_antigravity() {
    echo -e "\033[36m[+] Installing for Antigravity...\033[0m"
    local base_dir
    if [ "$WORKSPACE" = true ]; then
        base_dir="${CURRENT_DIR}/.agents/skills"
    else
        base_dir="${USER_HOME}/.gemini/config/skills"
    fi
    for name in "improve" "improve-all"; do
        local dest="${base_dir}/${name}"
        install_skill_files "${dest}" "${name}"
        echo -e "\033[32m    ✓ Registered Antigravity skill: ${dest}\033[0m"
    done
}

install_claude() {
    echo -e "\033[36m[+] Installing for Claude Code...\033[0m"
    local skill_base
    if [ "$WORKSPACE" = true ]; then
        skill_base="${CURRENT_DIR}/.claude/skills"
    else
        skill_base="${USER_HOME}/.claude/skills"
    fi
    for name in "improve" "improve-all"; do
        local dest="${skill_base}/${name}"
        install_skill_files "${dest}" "${name}"
        echo -e "\033[32m    ✓ Registered Claude Skill: ${dest}\033[0m"
    done
}

install_cursor() {
    echo -e "\033[36m[+] Installing for Cursor IDE...\033[0m"
    if [ "$WORKSPACE" = true ]; then
        local cmd_base="${CURRENT_DIR}/.cursor/commands"
        mkdir -p "${cmd_base}"
        cp -f "${SCRIPT_DIR}/templates/cursor/improve.md" "${cmd_base}/improve.md"
        cp -f "${SCRIPT_DIR}/templates/cursor/improve-all.md" "${cmd_base}/improve-all.md"
        echo -e "\033[32m    ✓ Registered Workspace Cursor Commands in: ${cmd_base}\033[0m"
    else
        local rules_base="${USER_HOME}/.cursor/rules"
        mkdir -p "${rules_base}"
        cp -f "${SCRIPT_DIR}/templates/cursor/improve.md" "${rules_base}/improve.mdc"
        cp -f "${SCRIPT_DIR}/templates/cursor/improve-all.md" "${rules_base}/improve-all.mdc"
        echo -e "\033[32m    ✓ Registered Global Cursor Rules in: ${rules_base}\033[0m"
    fi
}

install_continue() {
    echo -e "\033[36m[+] Installing for Continue.dev...\033[0m"
    local config_dir
    if [ "$WORKSPACE" = true ]; then
        config_dir="${CURRENT_DIR}/.continue"
    else
        config_dir="${USER_HOME}/.continue"
    fi
    mkdir -p "${config_dir}"
    local config_file="${config_dir}/config.json"
    if [ ! -f "${config_file}" ]; then
        cp -f "${SCRIPT_DIR}/templates/continue/config.json" "${config_file}"
        echo -e "\033[32m    ✓ Created: ${config_file}\033[0m"
    else
        echo -e "\033[33m    ! Existing config.json found at ${config_file}. Please check templates/continue/config.json to merge customCommands.\033[0m"
    fi
}

install_deepseek() {
    echo -e "\033[36m[+] Installing for DeepSeek Harness (dsh)...\033[0m"
    local base_dir
    if [ "$WORKSPACE" = true ]; then
        base_dir="${CURRENT_DIR}/.agents/skills"
    else
        base_dir="${USER_HOME}/.agents/skills"
    fi
    for name in "improve" "improve-all"; do
        local dest="${base_dir}/${name}"
        install_skill_files "${dest}" "${name}"
        echo -e "\033[32m    ✓ Registered DeepSeek Harness Skill: ${dest}\033[0m"
    done
}

install_codex() {
    echo -e "\033[36m[+] Installing for OpenAI Codex...\033[0m"
    # OpenAI Codex natively discovers skills from ~/.agents/skills (the Agent Skills Specification standard).
    # Installing to .agents/skills ensures Codex Desktop & CLI have access without creating duplicate entries.
    local base_dir
    if [ "$WORKSPACE" = true ]; then
        base_dir="${CURRENT_DIR}/.agents/skills"
    else
        base_dir="${USER_HOME}/.agents/skills"
    fi
    for name in "improve" "improve-all"; do
        local dest="${base_dir}/${name}"
        install_skill_files "${dest}" "${name}"
        echo -e "\033[32m    ✓ Registered Codex Skill (via .agents/skills): ${dest}\033[0m"
    done
    local legacy_codex
    if [ "$WORKSPACE" = true ]; then
        legacy_codex="${CURRENT_DIR}/.codex/skills"
    else
        legacy_codex="${USER_HOME}/.codex/skills"
    fi
    rm -rf "${legacy_codex}/improve" "${legacy_codex}/improve-all"
}

# Run cleanup first
cleanup_legacy_duplicates

echo "================================================="
echo "Codebase Audit & Improve: Multi-Agent Installer"
echo "Target: ${TARGET} | Workspace: ${WORKSPACE}"
echo "================================================="

TARGET_LOWER=$(echo "$TARGET" | tr '[:upper:]' '[:lower:]')

if [ "$TARGET_LOWER" == "all" ] || [ "$TARGET_LOWER" == "antigravity" ]; then install_antigravity; fi
if [ "$TARGET_LOWER" == "all" ] || [ "$TARGET_LOWER" == "claude" ]; then install_claude; fi
if [ "$TARGET_LOWER" == "all" ] || [ "$TARGET_LOWER" == "cursor" ]; then install_cursor; fi
if [ "$TARGET_LOWER" == "all" ] || [ "$TARGET_LOWER" == "continue" ]; then install_continue; fi
if [ "$TARGET_LOWER" == "all" ] || [ "$TARGET_LOWER" == "deepseek" ]; then install_deepseek; fi
if [ "$TARGET_LOWER" == "all" ] || [ "$TARGET_LOWER" == "codex" ]; then install_codex; fi

echo ""
echo -e "\033[32mAll selected slash commands and skills have been cleanly installed without duplicates!\033[0m"
echo "Ready for Antigravity, Claude Code, Cursor, Continue, DeepSeek Harness, and Codex."
