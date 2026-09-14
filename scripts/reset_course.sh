#!/usr/bin/env bash
#
# Reset this course back to "never started" so you can run through it again.
#
#     bash scripts/reset_course.sh                  # interactive, keeps exercises/
#     bash scripts/reset_course.sh --delete-exercises
#     bash scripts/reset_course.sh --dry-run        # show the plan, change nothing
#
# Learner-facing: this runs on YOUR machine against YOUR fork, never in CI.
# It touches GitHub state (issues + which workflows are enabled) via the `gh`
# CLI, and optionally your local exercises/ files.
#
# Nothing destructive happens until you type "reset" at the confirmation
# prompt. --dry-run never asks and never writes. Your git history, commits and
# solutions/ are never touched.
#
# Why this script exists: re-running "Step 0 - Start Course" on a repo that has
# already been through the course does NOT restart it. Step 0 guards itself
# with `gh issue list --label step-1 --state all`, and `--state all` counts
# CLOSED issues too. So the run goes green, skips every step, and creates
# nothing — looking like a success while doing nothing. A real restart means
# deleting those old step issues, not just closing them.
#
set -euo pipefail

# --- args -------------------------------------------------------------------
DRY_RUN=false
DELETE_EXERCISES=false

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)           DRY_RUN=true ;;
    --delete-exercises)  DELETE_EXERCISES=true ;;
    -h|--help)           sed -n '3,24p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $1 (try --help)" >&2; exit 2 ;;
  esac
  shift
done

# Every mutating command goes through this, so --dry-run is honoured in exactly
# one place instead of being re-checked at each call site.
run() {
  if [ "$DRY_RUN" = true ]; then
    echo "    [dry-run] $*"
  else
    "$@"
  fi
}

say()  { printf '%s\n' "$*"; }
step() { printf '\n\033[1m%s\033[0m\n' "$*"; }

# --- preconditions ----------------------------------------------------------
if ! command -v gh >/dev/null 2>&1; then
  say "❌ The GitHub CLI (gh) is not installed."
  say "   Install it from https://cli.github.com/ then run: gh auth login"
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  say "❌ gh is installed but not logged in. Run: gh auth login"
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  say "❌ Not inside a git repository. cd to your course checkout first."
  exit 1
fi

# Resolve the repo from the local checkout so we can never reset someone
# else's copy by accident.
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)

# The step-N checker workflows. Step 0 gets re-enabled; these get disabled so a
# stray push can't trigger a mid-course grader before Step 0 has run.
STEP0_WORKFLOW="Step 0 - Start Course"

# --- gather current state ---------------------------------------------------
step "Course reset — $REPO"

# `mapfile` is bash 4+; macOS still ships bash 3.2, so read line by line.
read_lines() {  # read_lines VAR_NAME  <<< stdin
  local __name=$1 __line
  eval "$__name=()"
  while IFS= read -r __line; do
    [ -n "$__line" ] || continue
    eval "$__name+=(\"\$__line\")"
  done
}

# Both open and closed: closed issues are exactly what jams a restart.
# Step 0's guard keys on the "step-1" label specifically, so collect issues
# carrying EITHER label — a stray step-1 issue without "course" would silently
# keep blocking the restart. --search de-duplicates across both labels.
read_lines COURSE_ISSUES < <(
  gh issue list --repo "$REPO" --state all --limit 200 \
    --search 'label:course,step-1' --json number --jq '.[].number' 2>/dev/null || true
)

read_lines CHECK_WORKFLOWS < <(
  gh workflow list --repo "$REPO" --limit 100 --json name --jq '.[].name' \
    2>/dev/null | grep -E '^Step [0-9]+ - ' | grep -vxF "$STEP0_WORKFLOW" || true
)

EXERCISE_FILES=()
if [ -d exercises ]; then
  # Only the learner's practice*.py answers. exercises/README.md is part of the
  # course scaffold and is deliberately left alone.
  read_lines EXERCISE_FILES < <(
    find exercises -maxdepth 1 -name 'practice*.py' -type f | sort
  )
fi

say ""
say "This will:"
say "  1. DELETE ${#COURSE_ISSUES[@]} course issue(s) — open AND closed"
say "  2. Re-enable  \"$STEP0_WORKFLOW\""
say "  3. Disable    ${#CHECK_WORKFLOWS[@]} step checker workflow(s)"
if [ "$DELETE_EXERCISES" = true ]; then
  say "  4. DELETE ${#EXERCISE_FILES[@]} local file(s) in exercises/ (practice*.py)"
else
  say "  4. Keep your exercises/ files as they are (pass --delete-exercises to remove them)"
fi
say "  5. Trigger \"$STEP0_WORKFLOW\" to open a fresh Step 1 issue"
say ""
say "Not touched: git history, commits, solutions/, .env, exercises/README.md."

if [ ${#COURSE_ISSUES[@]} -eq 0 ] && [ ${#CHECK_WORKFLOWS[@]} -eq 0 ]; then
  say ""
  say "Nothing to reset — no course issues and no step workflows found."
  say "If you have never started the course, just push to main."
  exit 0
fi

# --- confirmation -----------------------------------------------------------
if [ "$DRY_RUN" = true ]; then
  say ""
  say "--dry-run: showing what would happen, changing nothing."
else
  say ""
  if [ ! -t 0 ]; then
    # No TTY (piped/CI). Refuse rather than assume consent.
    say "❌ Refusing to run without an interactive terminal to confirm in."
    say "   Re-run in a terminal, or use --dry-run to preview."
    exit 1
  fi
  printf 'Type "reset" to confirm (anything else aborts): '
  read -r reply
  if [ "$reply" != "reset" ]; then
    say "Aborted. Nothing was changed."
    exit 1
  fi
fi

# --- 1. delete course issues ------------------------------------------------
step "1/5 Deleting course issues"
if [ ${#COURSE_ISSUES[@]} -eq 0 ]; then
  say "    none found"
else
  for n in "${COURSE_ISSUES[@]}"; do
    say "    issue #$n"
    # Deleting, not closing: Step 0's guard counts closed issues as "started".
    run gh issue delete "$n" --repo "$REPO" --yes
  done
fi

# --- 2. re-enable Step 0 ----------------------------------------------------
step "2/5 Re-enabling \"$STEP0_WORKFLOW\""
run gh workflow enable "$STEP0_WORKFLOW" --repo "$REPO"

# --- 3. disable step checkers ----------------------------------------------
step "3/5 Disabling step checker workflows"
if [ ${#CHECK_WORKFLOWS[@]} -eq 0 ]; then
  say "    none found"
else
  for wf in "${CHECK_WORKFLOWS[@]}"; do
    say "    $wf"
    # Already-disabled workflows make gh exit non-zero; that is not an error.
    run gh workflow disable "$wf" --repo "$REPO" || true
  done
fi

# --- 4. local exercise files ------------------------------------------------
step "4/5 Local exercises/"
if [ "$DELETE_EXERCISES" != true ]; then
  say "    kept (${#EXERCISE_FILES[@]} practice file(s)) — re-run with --delete-exercises to remove"
elif [ ${#EXERCISE_FILES[@]} -eq 0 ]; then
  say "    nothing to delete"
else
  for f in "${EXERCISE_FILES[@]}"; do
    say "    rm $f"
    run rm -f "$f"
  done
  say ""
  say "    Deleted locally only. Commit and push to remove them on GitHub:"
  say "      git add -A exercises && git commit -m 'Reset course' && git push"
fi

# --- 5. kick off Step 0 -----------------------------------------------------
step "5/5 Starting the course again"
if run gh workflow run "$STEP0_WORKFLOW" --repo "$REPO"; then
  say "    dispatched"
else
  say "    Could not dispatch automatically. Start it by hand:"
  say "      Actions tab → \"$STEP0_WORKFLOW\" → Run workflow"
fi

step "Done"
if [ "$DRY_RUN" = true ]; then
  say "That was a dry run — nothing changed. Re-run without --dry-run to apply."
else
  say "Give it ~30s, then check the Issues tab for a fresh \"Step 1\" issue."
  say "If none appears, open the Actions tab and read the \"$STEP0_WORKFLOW\" logs."
fi
