#!/usr/bin/env bash
set -e

SKILL_NAME="codebase-audit-and-improve"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$1" == "--workspace" ]; then
    TARGET_DIR="$(pwd)/.agents/skills/${SKILL_NAME}"
else
    TARGET_DIR="${HOME}/.gemini/config/skills/${SKILL_NAME}"
fi

echo "Installing ${SKILL_NAME} into: ${TARGET_DIR}"

mkdir -p "$(dirname "${TARGET_DIR}")"
rm -rf "${TARGET_DIR}"
cp -R "${SCRIPT_DIR}" "${TARGET_DIR}"
rm -rf "${TARGET_DIR}/.git"

echo "✓ Successfully installed ${SKILL_NAME}!"
echo "Restart your agent session or reload workspace to activate."
