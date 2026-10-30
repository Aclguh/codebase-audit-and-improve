#!/usr/bin/env bash
# Multi-Agent Installer for improve and improve-all
# Supports Antigravity, Claude Code, Cursor, and Continue.dev with slash command preview (/improve, /improve-all)
set -e

TARGET="${1:-all}"
WORKSPACE=false

for arg in "$@"; do
    case "$arg" in
        --workspace) WORKSPACE=true ;;
        --target=*) TARGET="${arg#*=}" ;;
        antigravity|claude|cursor|continue|all) TARGET="$arg" ;;
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
        echo -e "\033[32m    ✓ Registered skill: ${dest}\033[0m"
    done
}

install_claude() {
    echo -e "\033[36m[+] Installing for Claude Code...\033[0m"
    local skill_base
    local cmd_base
    if [ "$WORKSPACE" = true ]; then
        skill_base="${CURRENT_DIR}/.claude/skills"
        cmd_base="${CURRENT_DIR}/.claude/commands"
    else
        skill_base="${USER_HOME}/.claude/skills"
        cmd_base="${USER_HOME}/.claude/commands"
    fi
    for name in "improve" "improve-all"; do
        local dest="${skill_base}/${name}"
        install_skill_files "${dest}" "${name}"
        echo -e "\033[32m    ✓ Registered Claude Skill: ${dest}\033[0m"
    done
    mkdir -p "${cmd_base}"
    cp -f "${SCRIPT_DIR}/integrations/claude/commands/improve.md" "${cmd_base}/improve.md"
    cp -f "${SCRIPT_DIR}/integrations/claude/commands/improve-all.md" "${cmd_base}/improve-all.md"
    echo -e "\033[32m    ✓ Registered Claude Slash Commands in: ${cmd_base}\033[0m"
}

install_cursor() {
    echo -e "\033[36m[+] Installing for Cursor IDE...\033[0m"
    local cmd_base
    if [ "$WORKSPACE" = true ]; then
        cmd_base="${CURRENT_DIR}/.cursor/commands"
    else
        cmd_base="${USER_HOME}/.cursor/commands"
    fi
    mkdir -p "${cmd_base}"
    cp -f "${SCRIPT_DIR}/integrations/cursor/commands/improve.md" "${cmd_base}/improve.md"
    cp -f "${SCRIPT_DIR}/integrations/cursor/commands/improve-all.md" "${cmd_base}/improve-all.md"
    echo -e "\033[32m    ✓ Registered Cursor Slash Commands in: ${cmd_base}\033[0m"
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
        cp -f "${SCRIPT_DIR}/integrations/continue/config.json" "${config_file}"
        echo -e "\033[32m    ✓ Created: ${config_file}\033[0m"
    else
        echo -e "\033[33m    ! Existing config.json found at ${config_file}. Please check integrations/continue/config.json to merge customCommands.\033[0m"
    fi
}

echo "================================================="
echo "Codebase Audit & Improve: Multi-Agent Installer"
echo "Target: ${TARGET} | Workspace: ${WORKSPACE}"
echo "================================================="

TARGET_LOWER=$(echo "$TARGET" | tr '[:upper:]' '[:lower:]')

if [ "$TARGET_LOWER" == "all" ] || [ "$TARGET_LOWER" == "antigravity" ]; then install_antigravity; fi
if [ "$TARGET_LOWER" == "all" ] || [ "$TARGET_LOWER" == "claude" ]; then install_claude; fi
if [ "$TARGET_LOWER" == "all" ] || [ "$TARGET_LOWER" == "cursor" ]; then install_cursor; fi
if [ "$TARGET_LOWER" == "all" ] || [ "$TARGET_LOWER" == "continue" ]; then install_continue; fi

echo ""
echo -e "\033[32mAll selected slash commands and skills have been successfully installed!\033[0m"
echo "You can now type '/' in Antigravity, Claude Code, Cursor, or Continue to preview and autocomplete /improve and /improve-all."
