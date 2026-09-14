# Course Architecture: "Introduction to the Anthropic Python SDK"

This document explains — in plain language — how this GitHub course works under
the hood, modeled directly on the real **github/skills** courses (e.g.
[`skills/introduction-to-github`](https://github.com/skills/introduction-to-github)).
If you've ever done "Introduction to GitHub" from github.com/skills, this is the
exact same machine, just re-themed around the Anthropic Python SDK.

---

## 1. The big idea in one paragraph

A learner clicks **"Use this template"** to get their own private copy of this
repo. The instant they create it, a GitHub Action wakes up, opens **Issue #1**
containing the theory + exercise for Step 1, and posts a comment. The learner
does the exercise **inside their own repo** (writes a Python file, runs a
script, pushes a commit). That push **triggers another Action** which checks
whether the exercise was actually completed correctly. If it was: the Action
comments "✅ nice job" on the issue, closes it, and opens the **next** issue
for Step 2. If not: nothing bad happens — the learner just doesn't get the
"complete" comment, tries again, and pushes again. This repeats until the
course is finished, at which point a final "🎉 you completed the course"
issue is posted and no more workflows fire.

Nothing runs on Anthropic's or GitHub's servers except the learner's own repo's
Actions runners. All state (which step you're on) lives in **which GitHub
Actions workflows are currently enabled/disabled** in that specific repo — no
external database, no dashboard.

---

## 2. Repo layout

```
anthropic-sdk-course/
├── README.md                          # Course landing page + "Use this template" button
├── SETUP-GUIDE.md                     # How the course AUTHOR (you) publishes this to GitHub
├── COURSE-ARCHITECTURE.md             # This file
├── .github/
│   ├── workflows/
│   │   ├── 00-start-course.yml        # Fires once, on first push to main; opens Step 1 issue
│   │   ├── 01-check-step1.yml         # Validates Step 1, opens Step 2 issue
│   │   ├── 02-check-step2.yml         # Validates Step 2, opens Step 3 issue
│   │   ├── 03-check-step3.yml         # Validates Step 3, opens Step 4 issue
│   │   ├── 04-check-step4.yml         # Validates Step 4, opens Step 5 issue
│   │   ├── 05-check-step5.yml         # Validates Step 5, opens Step 6 issue
│   │   ├── 06-check-step6.yml         # Validates Step 6, opens Step 7 issue
│   │   ├── 07-check-step7.yml         # Validates Step 7, opens Step 8 issue
│   │   ├── 08-check-step8.yml         # Validates Step 8, opens Step 9 issue
│   │   ├── 09-check-step9.yml         # Validates Step 9, opens Step 10 issue
│   │   ├── 10-check-step10.yml        # Validates Step 10, opens Step 11 issue
│   │   ├── 11-check-step11.yml        # Validates Step 11, opens Step 12 issue
│   │   ├── 12-check-step12.yml        # Validates Step 12, opens Step 13 issue
│   │   ├── 13-check-step13.yml        # Validates Step 13, opens Step 14 issue
│   │   ├── 14-check-step14.yml        # Validates Step 14, opens Step 15 issue
│   │   ├── 15-check-step15.yml        # Validates Step 15, opens Step 16 issue
│   │   ├── 16-check-step16.yml        # Validates Step 16, opens Step 17 issue
│   │   ├── 17-check-step17.yml        # Validates Step 17, opens Step 18 issue
│   │   ├── 18-check-step18.yml        # Validates Step 18, opens Step 19 issue
│   │   ├── 19-check-step19.yml        # Validates Step 19, opens Step 20 issue
│   │   ├── 20-check-step20.yml        # Validates Step 20, opens Step 21 issue
│   │   ├── 21-check-step21.yml        # Validates Step 21, opens Step 22 issue
│   │   └── 22-check-step22.yml        # Validates Step 22 capstone, posts course-complete (final, self-disables)
│   ├── steps/
│   │   ├── 00-welcome.md              # Posted into Issue #0 (kickoff)
│   │   ├── 01-install-sdk.md          # Theory + exercise for Step 1 (posted into issue)
│   │   ├── 02-first-message.md        # Theory + exercise for Step 2
│   │   ├── 03-inspect-response.md     # Theory + exercise for Step 3
│   │   ├── 04-message-roles.md        # Theory + exercise for Step 4
│   │   ├── 05-content-blocks-image.md # Theory + exercise for Step 5
│   │   ├── 06-streaming.md            # Theory + exercise for Step 6
│   │   ├── 07-structured-json-output.md # Theory + exercise for Step 7
│   │   ├── 08-tool-use.md             # Theory + exercise for Step 8
│   │   ├── 09-extended-thinking.md    # Theory + exercise for Step 9
│   │   ├── 10-vision-multi-image.md   # Theory + exercise for Step 10
│   │   ├── 11-pdf-support.md          # Theory + exercise for Step 11
│   │   ├── 12-prompt-caching.md       # Theory + exercise for Step 12
│   │   ├── 13-token-counting.md       # Theory + exercise for Step 13
│   │   ├── 14-batch-api.md            # Theory + exercise for Step 14
│   │   ├── 15-async-client.md         # Theory + exercise for Step 15
│   │   ├── 16-error-handling.md       # Theory + exercise for Step 16
│   │   ├── 17-models-available.md     # Theory + exercise for Step 17
│   │   ├── 18-files-api.md            # Theory + exercise for Step 18
│   │   ├── 19-code-execution-tool.md  # Theory + exercise for Step 19
│   │   ├── 20-web-search-tool.md      # Theory + exercise for Step 20
│   │   ├── 21-bedrock-vertex-clients.md # Theory + exercise for Step 21
│   │   ├── 22-capstone.md              # Build-an-app brief for Step 22 (final step)
│   │   └── 23-course-complete.md       # Final congratulations message
│   └── scripts/
│       ├── _report.py                 # Shared expected/actual/hint failure reporting
│       ├── check_step1.py .. check_step22.py  # One small Python validator per step
│       #   (imports/execs the learner's exercise file and checks its output/behavior)
└── exercises/                         # Learner writes files HERE as they progress
    └── (empty at start — the learner creates practice*.py here)
```

This mirrors the real github/skills layout almost 1:1:
- `.github/steps/*.md` = the exact same convention github/skills uses for
  per-step lesson content (they call it "step content"; it gets pasted into an
  issue comment by the Action, not rendered as a wiki page).
- `.github/workflows/*.yml` = one workflow per step, each **disabled** by
  default except the current one. "Progress" = "which single workflow file is
  currently enabled." That's the entire state machine.
- A `README.md` with a big "Use this template" / "Copy Exercise" badge, same
  as every github/skills repo.

### Why disable/enable workflows instead of a database?

Real github/skills courses do this because it's the simplest possible durable
state: GitHub itself stores "is this workflow enabled" per-repo, for free, and
it survives forever. There's no server to run, no database to pay for. The
tradeoff: it only works within a *single repo* (which is exactly what we want —
each learner's forked/templated copy is its own isolated course run).

---

## 3. The three trigger patterns you need

| Trigger | Used for | Example in this course |
|---|---|---|
| `on: push` (to `main`) | Kicking off the course the moment a learner's copy is created | `00-start-course.yml` |
| `on: push` with a `paths:` filter | Detecting that a specific exercise file changed | `01-check-step1.yml` triggers only when `exercises/practice1.py` is pushed |
| `on: workflow_dispatch` | Manual "re-run this check" button in the Actions tab, useful for debugging or if a learner wants to force a re-check | Added to every step workflow as a safety valve |

We deliberately **don't** use `on: issues` (comment-triggered) for grading in
this scaffold, because grading "did you write correct code" is best tied to
**pushes of the actual file**, not to someone typing "done" in a comment. Real
github/skills courses use the same push-based approach for code exercises.

---

## 4. How issues gate progression (step by step)

1. **Repo created from template** → `00-start-course.yml` runs (guarded so it
   only runs once — it checks whether a "step-1" labeled issue already
   exists before creating another).
2. That workflow uses the **GitHub CLI (`gh`)** (already available on every
   Actions runner, authenticated via the built-in `GITHUB_TOKEN`) to:
   - `gh issue create` — open "📘 Step 1: Install the SDK" with the contents
     of `.github/steps/01-install-sdk.md` as the body.
   - `gh workflow enable "Step 1"` and `gh workflow disable` everything else,
     so only the Step 1 checker is listening for pushes.
3. **Learner does the exercise** in their own clone: writes `practice1.py`,
   commits, pushes to `main`.
4. That push triggers `01-check-step1.yml` (because of the `paths:`
   filter matching `exercises/practice1.py`). The workflow:
   - Checks out the learner's code.
   - Runs `.github/scripts/check_step1.py`, a small Python script that
     imports/execs the learner's file and checks the output/behavior
     (e.g., "does `anthropic.__version__` get printed", "does a client
     object of the right type get created").
   - If the check **passes**: finds the open Step 1 issue via `gh issue list
     --search`, posts a "✅ Step 1 complete!" comment on it, closes it, opens
     the Step 2 issue from `.github/steps/02-first-message.md`, enables the
     Step 2 workflow and disables the Step 1 workflow.
   - If the check **fails**: the workflow run shows a red ❌ in the Actions
     tab (visible from the issue via the "checks" link) but nothing is
     closed — the learner reads the failure output, fixes their code, and
     pushes again. This is safe to repeat indefinitely.
5. This repeats for Step 2, Step 3, ... until the last step's workflow posts
   `.github/steps/23-course-complete.md` into a final issue and disables
   itself — no more workflows are left enabled, so the course naturally
   stops.

### Why "disable the old workflow, enable the next"?

- Prevents duplicate/late-firing triggers from an old step re-commenting
  after you've moved on.
- Makes "what step am I on" visually inspectable in the repo's **Actions**
  tab: exactly one workflow will show as "Active", the rest "Disabled".
- It's exactly the mechanism the real `skills/introduction-to-github`
  workflows use (`gh workflow disable "${{ github.workflow }}"` /
  `gh workflow enable "Step N"`), confirmed by inspecting that repo's actual
  workflow YAML.

---

## 5. What the learner actually experiences, end to end

1. Learner opens the course README on GitHub and clicks **"Use this
   template"** (or a prebuilt `github.com/new?template_owner=...` badge link,
   same UX as github/skills).
2. GitHub creates `their-username/anthropic-sdk-course` as a normal repo they
   own, with Actions enabled by default (public repos get free Actions
   minutes).
3. Learner adds their `ANTHROPIC_API_KEY` as a repo secret (Settings →
   Secrets and variables → Actions) — needed because Step 2+ exercises make
   *real* calls to the Anthropic API, both when the learner runs their script
   locally AND, in this scaffold, when the CI grading script re-runs the
   learner's code to confirm it actually calls the API correctly.
4. Within ~20 seconds, Issue #1 appears with the Step 1 lesson: a short
   theory blurb ("what is the SDK, how do you install it") pulled straight
   from the course's source material, plus a concrete "do this" activity.
5. Learner clones their new repo locally, creates `exercises/practice1.py`
   exactly as instructed, and pushes.
6. Within a few seconds, a comment appears on Issue #1: "✅ Step 1 complete!
   Opening Step 2..." — and Issue #1 closes, Issue #2 opens automatically.
7. Repeat for each step. At the end, a final "🎉 Course complete" issue
   appears and no further action is required.
8. If they get stuck, every step markdown includes a `<details><summary>
   Having trouble?</summary>` collapsible troubleshooting section, same
   pattern as github/skills.

---

## 6. Scope of this course

This repo implements **all 22 steps** end-to-end, covering every section of
the Anthropic Python SDK reference material plus a capstone that asks the
learner to assemble the pieces without a copy-pasteable answer:

- **Step 1** — Installation & Setup (`Anthropic()` client construction, env
  var vs explicit key).
- **Step 2** — `messages.create()` minimal call.
- **Step 3** — Inspecting the full response object (`id`, `model`,
  `stop_reason`, `usage`).
- **Step 4** — Message roles & multi-turn conversations.
- **Step 5** — Content blocks: text + image input (base64).
- **Step 6** — Streaming responses.
- **Step 7** — Structured / JSON output.
- **Step 8** — Tool use.
- **Step 9** — Extended thinking.
- **Step 10** — Vision: multiple images in one request.
- **Step 11** — PDF support.
- **Step 12** — Prompt caching.
- **Step 13** — Counting tokens before you spend them.
- **Step 14** — Batch API: create, poll, retrieve results.
- **Step 15** — Async Client: `AsyncAnthropic`.
- **Step 16** — Error handling: `APIError`, `RateLimitError`,
  `APIStatusError`.
- **Step 17** — Comparing models: same call, different model string.
- **Step 18** — Files API: upload once, reference by ID.
- **Step 19** — Code execution tool (server-side sandbox).
- **Step 20** — Web search tool (server-side).
- **Step 21** — Bedrock and Vertex client variants.
- **Step 22** — Capstone: build a tool-using CLI assistant (multi-turn
  conversation + `tool_use`/`tool_result` round trip + specific-exception
  handling + safe text extraction). Final step, posts course-complete.

Every step follows the **exact same pattern**: a `.github/steps/NN-*.md` file
(theory + exercise, adapted from the reference doc), a
`.github/workflows/NN-check-stepN.yml` file, a `check_stepN.py` validator, and
the "opens next issue" glue that enables the next workflow and disables the
current one. `SETUP-GUIDE.md` and this file explain the recipe if you want to
remix this course or extend it further.

---

## 7. Design decisions & tradeoffs (so you know why things are the way they are)

- **Validation runs the learner's actual code** (not just checks a file
  exists) so exercises that require a real API call are graded on real
  behavior, not just file presence. This does mean CI spends a few cents of
  Anthropic API credits per push — acceptable for a learning course, and the
  learner is told about this cost up front in the README.
- **One workflow file per step**, not one giant workflow with a big
  `if/else`, because that's what github/skills does and it keeps the Actions
  tab readable (each step shows as its own named check).
- **`exercises/` is a plain folder in the learner's own repo**, not a
  separate branch per step (unlike `introduction-to-github`, which uses
  branches for its Git-teaching purpose). Since this course teaches an SDK,
  not Git itself, keeping everything on `main` is simpler and matches how a
  learner would normally develop a small Python project.
- **Grading script failures never crash the workflow ungracefully** — the
  Python checker prints an explicit ✅/❌ reason and exits `0` on pass or `1`
  on fail. The workflow step reads that exit code (`if: success()` /
  `if: failure()`) to decide whether to post the "complete" comment or a
  "try again" comment. Repeated pushes are always safe — nothing is ever
  left in a broken state.
