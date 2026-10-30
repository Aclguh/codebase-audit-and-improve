#!/usr/bin/env bash
set -e

SKILLS=("improve" "improve-all")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$1" == "--workspace" ]; then
    BASE_DIR="$(pwd)/.agents/skills"
else
    BASE_DIR="${HOME}/.gemini/config/skills"
fi

for SKILL_NAME in "${SKILLS[@]}"; do
    TARGET_DIR="${BASE_DIR}/${SKILL_NAME}"
    echo "Installing ${SKILL_NAME} into: ${TARGET_DIR}"
    mkdir -p "$(dirname "${TARGET_DIR}")"
    rm -rf "${TARGET_DIR}"
    cp -R "${SCRIPT_DIR}" "${TARGET_DIR}"
    rm -rf "${TARGET_DIR}/.git"

    if [ "${SKILL_NAME}" == "improve-all" ]; then
        cp -f "${SCRIPT_DIR}/skills/improve-all/SKILL.md" "${TARGET_DIR}/SKILL.md"
    else
        cp -f "${SCRIPT_DIR}/skills/improve/SKILL.md" "${TARGET_DIR}/SKILL.md"
    fi
done

echo "Successfully installed improve and improve-all!"
echo "Restart your agent session or reload workspace to activate (/improve and /improve-all)."
