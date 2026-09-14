#!/usr/bin/env bash
# Welcome banner, printed by devcontainer.json's postAttachCommand every time
# the learner attaches to the Codespace.
#
# Deliberately never exits non-zero: a failing postAttachCommand shows up as an
# alarming error toast in VS Code, and a cosmetic banner must never do that.
set -u

BOLD='\033[1m'; DIM='\033[2m'; GREEN='\033[32m'; YELLOW='\033[33m'; RESET='\033[0m'

printf '\n'
printf "${BOLD}==========================================================${RESET}\n"
printf "${BOLD}  Welcome to the Anthropic Python SDK course \xF0\x9F\x91\x8B${RESET}\n"
printf "${BOLD}==========================================================${RESET}\n\n"

if [ -f .env ]; then
  # Is there a real-looking key in there yet?
  key_line="$(grep -E '^[[:space:]]*ICA_API_KEY[[:space:]]*=' .env 2>/dev/null | tail -1 || true)"
  key_value="${key_line#*=}"
  key_value="$(printf '%s' "$key_value" | tr -d '"'"'"' \t\r')"

  case "$key_value" in
    ""|your-*|your_*|YOUR-*|YOUR_*|xxx*|XXX*|paste*|PASTE*|changeme*|sk-ant-xxx*|replace*|REPLACE*)
      printf "${YELLOW}\xE2\x9A\xA0  ACTION NEEDED: paste your API key into .env${RESET}\n\n"
      printf "  1. Open the ${BOLD}.env${RESET} file in the file explorer on the left.\n"
      printf "  2. Replace the placeholder so the line reads:\n"
      printf "       ${BOLD}ICA_API_KEY=<your real key>${RESET}\n"
      printf "  3. Save the file (no quotes, no spaces around the '=').\n"
      printf "  4. Verify it worked:  ${BOLD}python3 scripts/preflight.py${RESET}\n\n"
      ;;
    *)
      printf "${GREEN}\xE2\x9C\x94  .env already has an ICA_API_KEY set.${RESET}\n"
      printf "   Double-check everything with: ${BOLD}python3 scripts/preflight.py${RESET}\n\n"
      ;;
  esac
else
  printf "${YELLOW}\xE2\x9A\xA0  No .env file found.${RESET}\n\n"
  printf "  Run:  ${BOLD}cp .env.example .env${RESET}\n"
  printf "  then paste your key into it as ${BOLD}ICA_API_KEY=<your real key>${RESET}\n"
  printf "  and verify with:  ${BOLD}python3 scripts/preflight.py${RESET}\n\n"
fi

printf "${DIM}Heads-up: repository *Actions* secrets are NOT visible in this${RESET}\n"
printf "${DIM}terminal. Actions secrets only feed the grader. For your own runs,${RESET}\n"
printf "${DIM}either add a *Codespaces* secret named ICA_API_KEY (then rebuild${RESET}\n"
printf "${DIM}the container) or just fill in .env by hand as shown above.${RESET}\n"
printf "${DIM}Your work is graded on push - check the Issues tab for Step 1.${RESET}\n\n"

exit 0
