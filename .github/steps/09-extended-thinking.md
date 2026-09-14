## 📘 Step 9 — Extended thinking

<!-- pedagogy-header:begin -->
**Phase 3: Tools & reasoning** · Step 9 of 22 · ~20 min · ~$0.03 in API calls

> **Why this matters:** On multi-step math, planning, and debugging, a thinking budget is the cheapest accuracy upgrade available — and the ThinkingBlock ordering rule here is a real bug that bites production code.
<!-- pedagogy-header:end -->

### 🎯 What you'll learn

- What **extended thinking** is: Claude's scratch paper, returned to you as a separate block
- Why `message.content` is a **list** and never safe to index with `[0]`
- The relationship between `max_tokens` and `budget_tokens` (one contains the other)
- How to pull two different block types out of one response in a single loop
- Python constructs used here: **dict as an argument value**, **`for` loop over a list**, **`if` / `elif`**, **variable initialisation**, **`bool()`**, **`len()`**, **string slicing** (`text[:200]`)

---

### 🧠 Theory — giving Claude a scratch pad

Normally Claude answers immediately. With **extended thinking** enabled, it
first writes out its reasoning into a dedicated `thinking` content block,
*then* writes the final answer into a `text` block. You get both back.

Why bother? Two reasons:

1. **Better answers on hard problems.** Multi-step arithmetic, logic
   puzzles, and planning tasks get measurably more accurate when the model
   works through them before committing to an answer.
2. **Visibility.** You can read *how* it got there, which is invaluable for
   debugging prompts.

You turn it on with one keyword argument:

```python
thinking={"type": "enabled", "budget_tokens": 1024}
```

That's a **dict** passed as the value of the `thinking` argument.
`"type": "enabled"` switches the feature on. `budget_tokens` is the ceiling
on how many tokens Claude may spend thinking.

#### Block order, visually

```
                    message.content  (a Python list)
   ┌───────────────────────────────┬───────────────────────────────┐
   │  index 0                      │  index 1                      │
   │  ┌─────────────────────────┐  │  ┌─────────────────────────┐  │
   │  │ ThinkingBlock           │  │  │ TextBlock               │  │
   │  │  .type    = "thinking"  │  │  │  .type  = "text"        │  │
   │  │  .thinking = "27*34..." │  │  │  .text  = "918"         │  │
   │  │  .signature = "..."     │  │  │                         │  │
   │  └─────────────────────────┘  │  └─────────────────────────┘  │
   │  has .thinking, NO .text      │  has .text, NO .thinking      │
   └───────────────────────────────┴───────────────────────────────┘
                 ▲                                ▲
                 │                                │
   content[0].text  → 💥 AttributeError     content[1].text → "918"

   ✅ Correct approach: loop over every block and switch on block.type
```

The reason `content[0].text` explodes is right there in the picture: with
thinking on, index 0 is a `ThinkingBlock`, and a `ThinkingBlock` simply has
no `.text` attribute. Its text lives in `.thinking`. Never assume position;
always ask `block.type`.

#### The token budget, visually

```
   max_tokens = 2000  ────────────────────────────────────────────────
   ┌──────────────────────────────┬─────────────────────────────────┐
   │ budget_tokens = 1024         │ room left for the final answer  │
   │ (thinking lives here)        │ (~976 tokens)                   │
   └──────────────────────────────┴─────────────────────────────────┘
   budget_tokens MUST be strictly less than max_tokens.
```

`budget_tokens` is carved *out of* `max_tokens`, not added on top. If
`budget_tokens >= max_tokens`, there'd be no room left for an answer, and
the API returns a 400 error.

---

### 🐍 Python concepts, defined as they appear

**A dict passed as an argument value** — you can hand a whole dict to a
keyword argument. These two are identical:

```python
# via a variable
opts = {"type": "enabled", "budget_tokens": 1024}
client.messages.create(model=MODEL, max_tokens=2000, thinking=opts, messages=msgs)

# inline — exactly the same thing
client.messages.create(
    model=MODEL,
    max_tokens=2000,
    thinking={"type": "enabled", "budget_tokens": 1024},
    messages=msgs,
)
```

**Initialising a variable to an empty string** —

```python
thinking_text = ""
```

We create the variable *before* the loop with a harmless default. If the
response happens to contain no thinking block, the variable still exists
and `print` won't crash with `NameError: name 'thinking_text' is not
defined`. This "declare an empty accumulator first" pattern shows up
constantly in Python.

**A `for` loop over a list** — visit each item once, in order.

```python
for block in message.content:
    print(block.type)   # runs once per block in the list
```

`block` is a new name bound to each item in turn. The name is yours to
choose; `block` is just conventional here.

**`if` / `elif`** — `elif` means "else if". Python tests conditions top to
bottom and runs **at most one** branch. Since a block can't be both
`"thinking"` and `"text"`, `elif` is the right tool (and slightly faster
than a second independent `if`).

**`bool(x)`** — converts a value to `True` or `False`. Python treats an
empty string `""` as falsy and any non-empty string as truthy. So
`bool(thinking_text)` answers "did we actually capture some thinking text?"
without you needing to write `!= ""`.

```python
bool("")          # False
bool("anything")  # True
```

**`len(x)`** — the number of items in a sequence. For a string, that's the
character count. `len("hello")` is `5`.

**String slicing** — `text[:200]` means "the first 200 characters". Useful
for previewing long thinking blocks without flooding your terminal.
`text[5:]` means "from index 5 to the end".

**Attribute access on API objects** — `block.thinking` and `block.text` are
fields on the objects the SDK hands back. Reminder from Step 8: **dicts you
build use `["brackets"]`; objects the API returns use `.dots`.**

---

### 🏋️ Exercise

1. In this repo, create a new file at
   **`exercises/practice9_thinking.py`** with exactly this content:

   ```python
   import os
   from dotenv import load_dotenv
   from anthropic import Anthropic

   load_dotenv()
   config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}

   client = Anthropic(
       api_key=config["ICA_API_KEY"],
       base_url="https://api.servicesessentials.ibm.com",
   )

   message = client.messages.create(
       model="claude-sonnet-5",
       max_tokens=2000,
       thinking={"type": "enabled", "budget_tokens": 1024},
       messages=[{"role": "user", "content": "What is 27 * 34? Think it through step by step."}],
   )

   thinking_text = ""
   answer_text = ""
   for block in message.content:
       if block.type == "thinking":
           thinking_text = block.thinking
       elif block.type == "text":
           answer_text = block.text

   print("has thinking block:", bool(thinking_text))
   print("thinking length:", len(thinking_text))
   print("answer:", answer_text)
   ```

---

### 🔍 Line-by-line walkthrough

| Code | What it does, in plain English |
| --- | --- |
| `import os` | Standard library module for talking to the operating system — here, reading environment variables. |
| `from dotenv import load_dotenv` | Pulls one function out of the `python-dotenv` package. |
| `from anthropic import Anthropic` | Pulls the client **class** out of the SDK. |
| `load_dotenv()` | Reads `.env` and loads each `KEY=value` line into the environment. No arguments, but the parentheses are required — without them you'd reference the function instead of calling it. |
| `config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}` | A **dict** holding the key. `os.environ.get("X")` returns `None` instead of crashing if `X` is absent. |
| `client = Anthropic(api_key=..., base_url=...)` | Builds the client object. Two **keyword arguments**: your credential, and the gateway URL this course routes through. |
| `message = client.messages.create(` | Start the API call. Everything indented below is a keyword argument. |
| `model="claude-sonnet-5",` | Which model. Sonnet is fast and inexpensive — plenty for this task. |
| `max_tokens=2000,` | Hard ceiling on tokens generated, thinking **included**. |
| `thinking={"type": "enabled", "budget_tokens": 1024},` | Turns extended thinking on. `1024 < 2000`, so ~976 tokens remain for the answer. |
| `messages=[{"role": "user", "content": "What is 27 * 34? ..."}],` | The conversation: a **list** containing one **dict**. `"role"` is who's speaking; `"content"` is what they said. |
| `thinking_text = ""` | Empty accumulator, created before the loop so it always exists. |
| `answer_text = ""` | Same, for the final answer. |
| `for block in message.content:` | Walk every block in the response list, in order. |
| `if block.type == "thinking":` | Is this the scratch paper? `==` compares; a single `=` would assign and be a syntax error here. |
| `thinking_text = block.thinking` | Capture it. Note the attribute is `.thinking`, **not** `.text`. |
| `elif block.type == "text":` | Otherwise, is it the final answer? |
| `answer_text = block.text` | Capture it. Here the attribute *is* `.text`. |
| `print("has thinking block:", bool(thinking_text))` | Prints `True` if we captured non-empty thinking. |
| `print("thinking length:", len(thinking_text))` | Character count of the reasoning — proof the block wasn't empty. |
| `print("answer:", answer_text)` | Claude's final reply, which should contain `918`. |

---

### ⚠️ What happens if you skip this

**Index `message.content[0].text` instead of looping:**

```
AttributeError: 'ThinkingBlock' object has no attribute 'text'
```

With thinking enabled, index 0 is the thinking block. This is the single
most common crash in this step and the reason the loop exists. The fix is
never "try index 1" — block order isn't contractual. Always switch on
`block.type`.

**Set `budget_tokens` >= `max_tokens`:**

```
anthropic.BadRequestError: 400 - thinking.budget_tokens: must be less than max_tokens
```

The budget is carved out of the total, so there'd be nothing left to answer
with.

**Omit `budget_tokens` entirely** → 400 error; the field is mandatory
whenever `thinking` is `"enabled"`.

**Read `block.text` on a thinking block** → `AttributeError`. Thinking text
lives in `.thinking`. Different block type, different field name.

**Skip initialising `thinking_text = ""` before the loop** → if no thinking
block comes back, the `print` line raises `NameError: name 'thinking_text'
is not defined`. Initialising first makes the failure graceful (`False` and
`0`) instead of a crash.

**Use a second `if` instead of `elif`** → this one is actually harmless
here, since a block has exactly one type. Worth knowing they behave the
same when the conditions are mutually exclusive.

**Set `max_tokens` too low overall** (say `1200` with a `1024` budget) →
the request is legal, but thinking may consume nearly the whole budget and
truncate the answer, so `918` never prints and the checker fails. Leave
plenty of headroom.

---

2. Run it locally:

   ```bash
   pip install anthropic python-dotenv
   python exercises/practice9_thinking.py
   ```

   ✅ **What should happen:** `has thinking block: True` prints, followed by
   `thinking length:` with a number greater than 0, and `answer:` with
   Claude's final reply containing the correct product, `918`. Roughly:

   ```
   has thinking block: True
   thinking length: 412
   answer: 27 × 34 = 918
   ```

   The exact `thinking length` number will differ on every run — that's
   normal. All the checker requires is that it's greater than zero.

3. Commit and push your file to `main`:

   ```bash
   git add exercises/practice9_thinking.py
   git commit -m "Step 9: extended thinking"
   git push
   ```

4. Watch the **Actions** tab. The **"Step 9 — Extended Thinking"** check
   runs automatically. On success this issue closes and **Step 10** opens.
   If it fails, read the error in the Action's log, fix your file, and push
   again.

<details>
<summary>Having trouble?</summary>

**Setup problems**

- Double-check the file path is exactly `exercises/practice9_thinking.py`.
- `ModuleNotFoundError: No module named 'dotenv'` — install
  `python-dotenv` (the import name and package name differ).
- 401 / authentication error — `ICA_API_KEY` isn't reaching the client.
  Verify `.env` is in the directory you run `python` from and that
  `load_dotenv()` runs before `Anthropic(...)`.

**Errors specific to extended thinking**

- `AttributeError: 'ThinkingBlock' object has no attribute 'text'` —
  you're indexing `content[0]`. Loop over `message.content` and check
  `block.type` instead.
- `AttributeError: 'TextBlock' object has no attribute 'thinking'` — the
  mirror image: you read `.thinking` off the text block. Guard each read
  with its matching `block.type` check.
- `budget_tokens` must be **strictly less than** `max_tokens` — if you get a
  400 error about token budgets, raise `max_tokens` or lower `budget_tokens`.
- `400 - thinking: Extra inputs are not permitted` or similar — check the
  dict keys are spelled exactly `"type"` and `"budget_tokens"`.
- `has thinking block: False` and `thinking length: 0` — the loop never
  matched. Print `[b.type for b in message.content]` to see the actual
  block types coming back, then confirm you compared against `"thinking"`
  (lowercase, in quotes).
- Remember `message.content` is a **list of blocks** — you must loop over it
  and check `block.type` (`"thinking"` vs `"text"`); don't assume index `0`
  is always the text block when thinking is enabled.
- If `answer:` doesn't contain `918`, try rerunning — extended thinking
  greatly reduces arithmetic mistakes but ensure your prompt still asks for
  the multiplication clearly. Also confirm `max_tokens` is high enough that
  the answer isn't being truncated.
- `NameError: name 'thinking_text' is not defined` — you deleted the
  `thinking_text = ""` line above the loop. Put it back.
- `TypeError: object of type 'NoneType' has no len()` — you initialised the
  accumulator to `None` instead of `""`. `len(None)` is invalid; `len("")`
  is `0`.

**Checker specifics**

- The checker looks for `load_dotenv()`, `ICA_API_KEY`, and `base_url=` in
  your script — make sure all three are present.
- It also requires the literal string `"thinking"` and `budget_tokens` in
  your source, and the labels `has thinking block:`, `thinking length:`,
  and `answer:` in your output — plus `has thinking block: True`,
  a `thinking length:` greater than 0, and `918` somewhere in stdout. Don't
  rename any printed label.
- If the check fails complaining about `ICA_API_KEY`, make sure it's set as
  a repo secret (Settings → Secrets and variables → Actions).

</details>

<details>
<summary>Stuck? Reveal the solution</summary>

Give it a real attempt first — debugging your own code is where the learning
happens. If you're properly stuck, the complete working reference is here:

**[`solutions/practice9_thinking.py`](../../solutions/practice9_thinking.py)**

Copy it to `exercises/practice9_thinking.py`, run it, then read it line by line and make
sure you can explain *why* each part is there.

</details>
