# SETUP GUIDE — How to stand up this course yourself

This guide is for **you** (the course author), not the learner. It walks
through turning this scaffold into a live, working GitHub course.

---

## 1. Create the GitHub repo

You have two options:

**Option A — Push as a normal repo (fastest way to test it yourself):**

```bash
cd /workspace/anthropic-sdk-course
git init
git add .
git commit -m "Scaffold: Anthropic Python SDK course (steps 1-3 PoC)"
gh repo create YOUR-USERNAME/anthropic-sdk-course --public --source=. --remote=origin --push
```

(Install the `gh` CLI first if you don't have it: https://cli.github.com/,
then run `gh auth login` once.)

**Option B — Make it a real "Use this template" course (for other learners):**

1. Push the repo as above.
2. Go to the repo on GitHub → **Settings** → check **"Template repository"**.
3. Share the URL. Anyone can now click **"Use this template"** to get their
   own independent copy with a clean Actions history.

---

## 2. Enable Actions

New repos usually have Actions enabled by default, but double check:

- Go to **Settings → Actions → General**.
- Under "Actions permissions," choose **"Allow all actions and reusable
  workflows"** (or at least allow `actions/checkout`, `actions/setup-python`,
  and the built-in `gh` CLI usage — those are all this course needs).
- Under "Workflow permissions" (same page, scroll down), select **"Read and
  write permissions"**. The workflows need to create issues, comment, close
  issues, and enable/disable other workflows — this requires write access.

---

## 3. Add your API key as a secret

Steps 2 and 3 make **real calls to the Anthropic API through this project's
IBM gateway** (`base_url="https://api.servicesessentials.ibm.com"`), both
when you (the learner) run the script locally AND when the GitHub Action
re-runs it to grade you. The client is constructed with `python-dotenv` +
`ICA_API_KEY` + that custom `base_url` — not the plain `Anthropic()` default.
That means the key needs to exist in two places:

1. **Your local `.env` file**, for testing: copy `.env.example` to `.env`
   and set `ICA_API_KEY=<your real key>`. The exercises call
   `load_dotenv()` to read it — `.env` is git-ignored, so it never gets
   committed.
2. **The repo's Actions secrets**, for grading:
   - Go to **Settings → Secrets and variables → Actions → New repository
     secret**.
   - Name: `ICA_API_KEY`
   - Value: your real key.
   - Click **Add secret**.

> 🌐 **Why `base_url`?** Passing `base_url=` points the SDK at a proxy/
> gateway in front of Anthropic's API instead of hitting `api.anthropic.com`
> directly. The SDK's request/response shapes stay identical — only the
> network destination changes. Useful when an org routes model traffic
> through an internal gateway for logging, cost tracking, or access control.

> 💰 **Cost note:** Steps 2 and 3 each make one small `messages.create()`
> call with `max_tokens=100`. This is a trivial cost per learner run
> (fractions of a cent), but if you expect many learners, keep an eye on
> your usage dashboard.

---

## 4. Kick off the course

The course starts itself automatically the first time something is pushed
to `main` — which happens the moment you push your initial commit (see
step 1 above). Workflow `Step 0 - Start Course` runs, and within a few
seconds you should see a new **Issue** appear titled "Step 1: Install the
SDK & create a client."

If nothing appears after ~30 seconds:

- Go to the **Actions** tab and check whether "Step 0 - Start Course" ran
  and what its logs say.
- Most common cause: workflow permissions weren't set to "Read and write"
  (see step 2 above) — the job will fail with a 403 when it tries to
  create the issue.

---

## 5. Test the flow yourself, as a learner would

1. Open the Step 1 issue that got created.
2. Follow its instructions exactly: create `exercises/practice1.py` locally
   with the given content, run it, then:

   ```bash
   git add exercises/practice1.py
   git commit -m "Step 1: install SDK and create client"
   git push
   ```

3. Watch the **Actions** tab — `Step 1 - Install SDK` should trigger within
   a couple seconds of the push landing on GitHub.
4. When it finishes (green check), refresh the Step 1 issue. You should see
   a ✅ comment, and the issue should be **closed**. A brand new **Step 2**
   issue should have opened automatically.
5. Repeat for Step 2 (`exercises/practice_message.py`) and Step 3
   (`exercises/practice_inspect.py`).
6. After Step 3 passes, a final **"🎉 Course complete!"** issue opens.

If a check fails, the workflow run will show a red ❌ in the Actions tab,
and (if the bot could figure out which issue to comment on) you'll see a
comment pointing you at the failed run's logs. Fix the file, push again —
the same workflow re-triggers on the next push to that file.

---

## 6. Restarting or resetting the course

Sooner or later you'll want a clean slate — you tested the flow yourself
and now want to hand the repo to a learner, or a learner wants to redo the
course from Step 1.

### Read this first: the confusing case

**Re-running "Step 0 - Start Course" when Step 1 issues already exist does
nothing — and still reports success.**

Step 0 guards against opening duplicate issues:

```bash
gh issue list --label "step-1" --state all
```

Note `--state all`. The guard counts **closed** issues too. So once you've
worked through Step 1, its issue is closed — and from then on, Step 0 will
skip issue creation forever. The workflow run goes **green** ✅ with a log
line saying the issue already exists, no new issue appears, and nothing
tells you you're stuck.

If you re-ran Step 0 and no issue showed up, this is why. Closing or
reopening issues won't help — the old issues must be **deleted** (see
below), because `--state all` matches them in any state.

The same applies to the per-step check workflows: they're deliberately
disabled until the previous step passes. A reset has to re-enable Step 0
*and* disable the step checkers, or the sequence starts out of order.

### The scripted way (recommended)

```bash
./scripts/reset_course.sh --dry-run   # preview — changes nothing
./scripts/reset_course.sh             # do it, after confirming
```

It prints exactly what it will touch, then requires you to type `reset`
(nothing else proceeds). It refuses to run at all without an interactive
terminal, so it can't be triggered accidentally from CI or a pipe.

What it does, in order:

1. Deletes every issue labelled `course` **or** `step-1` — **open and
   closed**, which is what unsticks the guard above. (Both labels, because
   the guard keys on `step-1`; a stray `step-1` issue without `course`
   would keep blocking the restart.)
2. Re-enables `Step 0 - Start Course`.
3. Disables all the `Step N - ...` check workflows.
4. Leaves `exercises/practice*.py` **alone** unless you pass
   `--delete-exercises`.
5. Dispatches Step 0, which opens a fresh Step 1 issue.

It never touches your git history, commits, `solutions/`, `.env`, or
`exercises/README.md`. Requires the `gh` CLI, authenticated
(`gh auth login`) — it runs on your machine, not in CI.

> Deleting issues needs admin rights on the repo. If `gh` reports a
> permissions error on step 1, you're likely not an owner/admin.

### The manual way

If you'd rather not run the script, or want to understand what it does:

1. **Delete the course issues** (not just close them) — Issues tab, or:

   ```bash
   gh issue list --state all --search 'label:course,step-1' --json number \
     --jq '.[].number' | xargs -I{} gh issue delete {} --yes
   ```

   The `label:course,step-1` search means "either label" — `step-1` is the
   one Step 0's guard actually checks.

2. **Re-enable Step 0** — Actions → "Step 0 - Start Course" → `···` →
   Enable workflow. Or `gh workflow enable "Step 0 - Start Course"`.

3. **Disable the step checkers** so steps can't run out of order:

   ```bash
   gh workflow list --all --json name --jq '.[].name' \
     | grep -E '^Step [1-9]' \
     | xargs -I{} gh workflow disable "{}"
   ```

4. **Decide about `exercises/`.** Deleting the learner's `practice*.py`
   files is optional:

   - **Keep them** to re-run the graders against existing work. Note that
     pushing a change to a practice file re-triggers its checker, so a
     completed exercise may pass again immediately.
   - **Delete them** for a genuinely blank start. They're recreated by the
     learner, not by the workflows. Deleting locally isn't enough — commit
     and push, or GitHub still has them.

5. **Manually dispatch Step 0** — Actions → "Step 0 - Start Course" → "Run
   workflow" → Run. Or `gh workflow run "Step 0 - Start Course"`.

   Do this **after** step 1, otherwise the guard skips issue creation again
   and you're back where you started.

### Verifying the reset worked

- A new **Step 1** issue is open, and it's the *only* `course` issue
  (`gh issue list --state all --search 'label:course,step-1'` shows one row).
- Actions shows `Step 0 - Start Course` **enabled**, every `Step N` checker
  **disabled**.
- Pushing `exercises/practice1_hello.py` triggers "Step 1" and nothing else.

---

## 7. Extending to more sections

This scaffold wires up Sections 1-2 of the 22-section reference material
(3 exercises total) as a working proof of concept. To add Section 3
onward, for each new step:

1. Add `.github/steps/0N-<slug>.md` with theory + exercise, adapted from
   the matching section in `Anthropic-Python-SDK-Reference.md`.
2. Add `.github/scripts/check_stepN.py` — a small script that runs the
   learner's file and checks stdout/behavior.
3. Add `.github/workflows/0N-check-stepN.yml`, copying the pattern from
   `02-check-step2.yml` or `03-check-step3.yml` (update file paths, issue
   labels, step numbers, and workflow names to enable/disable).
4. Update the previous step's workflow to open the new issue and enable
   the new workflow, instead of the course-complete issue.

See `COURSE-ARCHITECTURE.md` for the full design rationale and diagrams.
