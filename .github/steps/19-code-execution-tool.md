## 📘 Step 19 — Code execution tool (server-side sandbox)

<!-- pedagogy-header:begin -->
**Phase 3: Tools & reasoning** · Step 19 of 22 · ~20 min · ~$0.03 in API calls

> **Why this matters:** LLMs are bad at arithmetic and great at writing Python — handing Claude a sandbox turns 'probably 1,247' into a number that was actually computed.
<!-- pedagogy-header:end -->

### 🎯 What you'll learn

- The difference between a **client-side tool** (you run it) and a **server-side tool** (Anthropic runs it)
- How to enable code execution with one entry in the `tools=` list
- Why a **list of dicts** is the shape every `tools=` argument takes
- How to loop over `response.content` and filter blocks by `block.type`
- Why the tool **type string** contains a date, and what happens if you mistype it
- What the sandbox can and can't do (no internet!)

---

### 🧠 The concept in plain English

Large language models are famously shaky at arithmetic — they *predict* text, so
"the mean of these ten numbers" is a plausible-looking guess, not a calculation.

The code execution tool removes the guessing. You add one tool entry to your
request, and Claude gains the ability to **write real Python and run it** in a
sandbox on Anthropic's servers. The program's actual output is fed back into
Claude's reasoning, and Claude then tells you the answer. All inside a single
`messages.create()` call.

**Server-side vs client-side tools** — this is the key mental shift from Step 8:

| | Client-side tool (Step 8) | Server-side tool (this step) |
|---|---|---|
| Who executes it | **You**, in your own Python code | **Anthropic's** infrastructure |
| How you declare it | `{"name": ..., "input_schema": {...}}` | `{"type": "code_execution_20250825", "name": "code_execution"}` |
| Round trips | Claude stops → you run it → you send results back | None — handled inside one call |
| Your code must | implement the function | do nothing but read the answer |

So there is no `if block.type == "tool_use": ... run it ...` branch here. You just
read the final text.

---

### 🗺️ Diagram — client-side vs server-side tool flow

```mermaid
sequenceDiagram
    autonumber
    participant You as Your script
    participant API as Anthropic API
    participant Box as Sandbox (Python 3.11)

    rect rgb(255, 240, 240)
    note over You,API: CLIENT-SIDE tool (Step 8) — you do the work
    You->>API: messages.create(tools=[custom fn])
    API-->>You: stop_reason="tool_use" (waiting on you)
    You->>You: run the function yourself
    You->>API: send tool_result back (2nd call)
    API-->>You: final text
    end

    rect rgb(240, 250, 240)
    note over You,Box: SERVER-SIDE tool (this step) — one call, done
    You->>API: messages.create(tools=[code_execution_20250825])
    API->>Box: writes + runs real Python
    Box-->>API: stdout / result (e.g. 5.5)
    API-->>You: text block containing the true answer
    end
```

---

### 📖 Reference

The code execution tool lets Claude write and run
**real Python code** inside an Anthropic-managed sandbox — no code runs on
your machine, and you get the actual results (not a guess) back in the
same response.

A server-side tool is different from a client-side tool (like the
`custom` function tools from earlier steps): Claude doesn't ask *you* to
run anything. Instead, Anthropic's infrastructure runs the code and feeds
the result straight back into Claude's reasoning, all within one
`messages.create()` call.

```python
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=4096,
    messages=[
        {"role": "user", "content": "Use code execution to find the mean and stdev of [1,2,3,4,5,6,7,8,9,10]"}
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)
```

The response interleaves `server_tool_use` blocks (what Claude ran) with
`bash_code_execution_tool_result` / `text_editor_code_execution_tool_result`
blocks (what happened), plus a top-level `response.container.id` you can
reuse across requests to persist files and variables in the same sandbox.

**Sandbox specs:** Python 3.11, Linux/x86_64, 5 GiB RAM, no internet
access, pandas/numpy/matplotlib/scipy/pillow etc. pre-installed. Billed by
execution time (1,550 free hours/month per org, then $0.05/hour) — and
it's free entirely when paired with the web search or web fetch tools.

**When to use this:** Data analysis, chart generation, precise math Claude
shouldn't "guess" at, file format conversions — anything where you want
Claude to actually *run* code rather than just describe what code would do.

⚠️ **Exact type string matters.** The reference doc for this SDK version
specifies `"type": "code_execution_20250825"` — copy it exactly. A stale
or misspelled version string will be rejected by the API.

---

### 🐍 Python constructs used in this step

| Construct | Plain-English meaning |
|---|---|
| `os.environ.get("ICA_API_KEY")` | Dict-style **`.get()`** lookup: returns the value, or `None` if the variable is missing (instead of raising `KeyError` like `[...]` does). |
| `tools=[ {...} ]` | A **keyword argument** whose value is a **list** containing one **dict**. It's a list because you may enable several tools at once; each tool is one dict. |
| `{"type": ..., "name": ...}` | A **dict** — key/value pairs in curly braces. For server tools the `type` selects *which built-in capability*, and `name` is the label Claude refers to it by. |
| `"code_execution_20250825"` | A **versioned type string**. The date is part of the name, not a comment: it pins the tool's exact behaviour so a future upgrade can't silently change your app. |
| `for block in response.content:` | A **for loop** over the response's list of content blocks. One response can contain several blocks of different kinds. |
| `block.type` | A string field on each block saying what kind it is: `"text"`, `"server_tool_use"`, `"bash_code_execution_tool_result"`, … |
| `if block.type == "text":` | A **conditional**. `==` tests equality. This filters the loop down to just the human-readable prose blocks, skipping the machinery blocks. |
| `print("answer:", block.text)` | Two arguments joined by one space → output begins exactly `answer: `. That prefix is what the checker greps for. |
| `max_tokens=4096` | The generation budget. It must cover Claude's code, the tool interaction, **and** the final explanation — hence much larger than earlier steps. |

---

### 🔍 Line-by-line walkthrough of the exercise script

```python
import anthropic                                   # 1
import os                                          # 2
from dotenv import load_dotenv                     # 3

load_dotenv()                                      # 4

client = anthropic.Anthropic(                      # 5
    api_key=os.environ.get("ICA_API_KEY"),         # 6
    base_url="https://api.servicesessentials.ibm.com",   # 7
)

response = client.messages.create(                 # 8
    model="claude-sonnet-5",                       # 9
    max_tokens=4096,                               # 10
    messages=[                                     # 11
        {"role": "user", "content": "Use code execution to find the mean of [1,...,10]. State the mean clearly in your final sentence."}
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],   # 12
)

for block in response.content:                     # 13
    if block.type == "text":                       # 14
        print("answer:", block.text)               # 15
```

1–3. Imports: the SDK, `os` for the environment, `load_dotenv` for `.env`.
4. Loads `.env` into the environment. Must run **before** line 6.
5. Builds the client. Nothing tool-specific here — tools are per-request.
6. `.get()` returns `None` if the key is absent, so a missing key surfaces as an
   `AuthenticationError` from the server rather than a `KeyError` locally.
7. Routes through this project's gateway.
8. One single API call does everything: prompt → Claude writes code → sandbox runs
   it → Claude explains. You never see the intermediate round trips.
9. Sonnet — plenty capable for this, and far cheaper than Opus.
10. **4096** on purpose. Claude must spend tokens on the code it writes *plus* the
    final sentence. Too small and you get the code but no answer.
11. The usual one-user-turn messages list. Note the prompt does two jobs: asks for
    code execution, and asks Claude to *state the mean clearly* — that instruction
    is what guarantees `5.5` appears in the text the checker inspects.
12. The whole feature, in one line: a list with a single dict. The `type` is the
    versioned built-in tool ID; `name` is the handle Claude uses.
13. Loops the response's blocks. Expect several: `server_tool_use` (the code
    Claude ran), a tool-result block (what the sandbox printed), and finally
    `text`.
14. Keeps only `text` blocks. Without this guard, line 15 would hit a
    `server_tool_use` block that has **no `.text` attribute** and crash.
15. Prints the answer with the required `answer:` label.

---

### ⚠️ What happens if you skip this

| If you skip / change… | What actually happens |
|---|---|
| the exact type string (e.g. `code_execution_20250801`, `code-execution`) | The API rejects the request: `BadRequestError` / "unrecognized tool type". Version strings are literal — no fuzzy matching. The checker also greps your source for `code_execution_20250825`. |
| the whole `tools=` argument | The call still succeeds! Claude just *guesses* the mean from pattern-matching. It might even say 5.5. But nothing was executed, and on harder math it will be confidently wrong. This is the exact failure mode the tool exists to prevent. |
| `if block.type == "text":` | `AttributeError: 'ServerToolUseBlock' object has no attribute 'text'` on the first non-text block. Always filter by type. |
| the `for` loop (using `response.content[0].text`) | Index 0 is often a `server_tool_use` block, not the answer → `AttributeError`, or you print machinery instead of prose. |
| the `answer:` label | The checker greps stdout for the literal `answer:`. Rename it to `Answer:` or `result:` and the step fails even though your code is correct. |
| `max_tokens=4096` → something small like 200 | Generation stops before Claude writes its concluding sentence. You get tool blocks but no `text` block containing `5.5` → checker fails on the missing `5.5`. |
| "State the mean clearly" in the prompt | Claude may run the code and then reply "I've calculated it above" without restating the number. The checker requires the literal `5.5` in stdout. |
| assuming the sandbox has internet | It does **not**. Any `requests.get(...)` Claude writes will fail inside the box. Pair with the web search tool (Step 20) if you need live data. |
| `load_dotenv()` / `ICA_API_KEY` / `base_url=` | `AuthenticationError`, or requests to the wrong host — and the checker greps your source for all three. |

---

### 🏋️ Exercise

1. Create a file called `exercises/practice19_code_execution.py`
   in this repo with the following content:

```python
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ.get("ICA_API_KEY"),
    base_url="https://api.servicesessentials.ibm.com",
)

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=4096,
    messages=[
        {"role": "user", "content": "Use code execution to find the mean of [1,2,3,4,5,6,7,8,9,10]. State the mean clearly in your final sentence."}
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)

for block in response.content:
    if block.type == "text":
        print("answer:", block.text)
```

✅ **What should happen:** the script prints one line starting with
`answer:` whose text clearly states the mean is `5.5` (Claude computed
this by actually running Python in the sandbox, not by guessing).

Roughly:

```
answer: I ran the calculation in Python. The mean of [1,2,3,4,5,6,7,8,9,10] is 5.5.
```

(You may see more than one `answer:` line if Claude narrates before and after
running the code — that's fine, as long as one of them contains `5.5`.)

2. Run it locally to confirm it works:

```bash
python exercises/practice19_code_execution.py
```

✅ **What should happen:** no errors, and the printed answer mentions
`5.5` as the mean.

3. Commit and push your file to the `main` branch:

```bash
git add exercises/practice19_code_execution.py
git commit -m "Complete step 19: code execution tool"
git push
```

✅ **What should happen:** pushing triggers the "Step 19 - Code Execution
Tool" GitHub Actions workflow. Watch the **Actions** tab — a green
checkmark means this issue will auto-close and Step 20 will open
automatically.

<details>
<summary>Having trouble?</summary>

**Expected beginner errors**

- `AttributeError: 'ServerToolUseBlock' object has no attribute 'text'` — your
  `print` isn't guarded by `if block.type == "text":`, or it's indented one level
  too far left so it runs for every block.
- Nothing at all prints — every block was a tool block and Claude never produced
  text. Almost always a `max_tokens` that's too low; keep it at 4096.
- `answer:` prints but without `5.5` — Claude summarized vaguely. Keep the "State
  the mean clearly in your final sentence." instruction in the prompt.
- `TypeError: create() got an unexpected keyword argument 'tool'` — the parameter
  is plural: `tools=`.
- `TypeError: ... tools must be a list` / `unhashable type` — you passed the dict
  directly (`tools={...}`) instead of wrapping it in a list (`tools=[{...}]`).
- `anthropic.AuthenticationError` — `load_dotenv()` missing or `.env` not in the
  directory you ran `python` from. Note `.get()` returns `None` silently, so the
  failure appears as a server-side auth error rather than a local `KeyError`.
- The script takes 20–40 seconds. That's normal — a sandbox is being spun up. The
  checker allows 90 seconds.

**Course-specific gotchas**

- If you see an error mentioning an unrecognized tool type, double-check
  you spelled `code_execution_20250825` exactly — no typos, no extra
  spaces, correct date suffix.
- If `response.content` has no `text` blocks, check for a
  `server_tool_use` or tool-result block instead — Claude sometimes
  returns tool activity before its final text summary; the loop above
  only prints `text` blocks, so make sure `max_tokens` is high enough
  (4096) for Claude to finish its explanation after running code.
- The sandbox has **no internet access** — this exercise doesn't need it,
  but don't expect `requests.get()`-style code inside code execution to
  work.
- Keep `load_dotenv()`, `ICA_API_KEY`, and `base_url=` in your client
  setup — the checker verifies your script still uses this project's real
  client pattern.

</details>

<details>
<summary>Stuck? Reveal the solution</summary>

Give it a real attempt first — debugging your own code is where the learning
happens. If you're properly stuck, the complete working reference is here:

**[`solutions/practice19_code_execution.py`](../../solutions/practice19_code_execution.py)**

Copy it to `exercises/practice19_code_execution.py`, run it, then read it line by line and make
sure you can explain *why* each part is there.

</details>
