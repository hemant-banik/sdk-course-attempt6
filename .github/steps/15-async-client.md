## 📘 Step 15 — Async Client: `AsyncAnthropic`

<!-- pedagogy-header:begin -->
**Phase 4: Production concerns** · Step 15 of 22 · ~20 min · ~$0.002 in API calls

> **Why this matters:** Any web backend serving more than one user at a time needs `AsyncAnthropic` — otherwise every request blocks a worker for the full length of a Claude call.
<!-- pedagogy-header:end -->

### 🎯 What you'll learn

- What "async" actually means, in plain English (and why it makes your app faster)
- The four Python keywords/functions you need: `async def`, `await`, `asyncio.run()`, `asyncio.gather()`
- How `AsyncAnthropic` differs from the `Anthropic` client you've used for 14 steps (spoiler: barely)
- How to fire two Claude requests **at the same time** and collect both answers
- What breaks if you forget `await` — and how to recognise that error instantly

---

### 🧠 The concept in plain English

Every request to Claude spends almost all of its time **waiting**. Your code
sends a few hundred bytes over the network, then sits there doing nothing for
2–5 seconds while Anthropic's servers think, then reads the answer back.

The regular `Anthropic` client is **synchronous** ("sync"): it *blocks*. While
it waits, your whole program is frozen. Two requests = two waits, one after
the other.

The `AsyncAnthropic` client is **asynchronous** ("async"): while one request is
waiting on the network, Python is allowed to go start the next one. The waits
**overlap**. Two requests that each take 3 seconds finish in ~3 seconds total
instead of ~6.

> 🍳 **Kitchen analogy:** sync is boiling one pot of pasta, waiting for it to
> finish, *then* putting the second pot on. Async is putting both pots on the
> stove at once. You didn't get a faster stove — you just stopped standing
> around waiting.

**Important:** async does not make a single request faster. It makes *many
independent requests* finish sooner by overlapping the dead time.

---

### 🗺️ Diagram — sync sequential vs async concurrent

```
SYNC  (client = Anthropic)          total wall-clock time ≈ 6s
────────────────────────────────────────────────────────────────
request 1  |■■■■■■■■■■■■ wait 3s ■■■■■■■■■■■■|
request 2                                     |■■■■■ wait 3s ■■■■■|
           0s                                3s                   6s


ASYNC (client = AsyncAnthropic + asyncio.gather)   total ≈ 3s
────────────────────────────────────────────────────────────────
request 1  |■■■■■■■■■■■■ wait 3s ■■■■■■■■■■■■|
request 2  |■■■■■■■■■■■■ wait 3s ■■■■■■■■■■■■|
           0s                                3s
           ↑ both launched here                ↑ gather() returns
             (order of results is still 1, 2 — guaranteed)
```

---

### 🐍 Python constructs used in this step

Read these once; every one of them appears in the exercise below.

| Construct | Plain-English meaning |
|---|---|
| `async def ask(...)` | Defines a **coroutine function**. Calling it does *not* run the body — it hands you back a "coroutine object", a to-do note that says "run me later". |
| `await something` | "Pause *this* coroutine here, let other work run, and wake me up when `something` has a result." You may only write `await` **inside** an `async def`. |
| `asyncio` | Python's built-in async engine (standard library — nothing to install). It owns the **event loop**, the scheduler that decides which paused coroutine to resume next. |
| `asyncio.run(main())` | The bridge from normal blocking Python into async land. It starts an event loop, runs the coroutine you give it until it finishes, then shuts the loop down. Call it **once**, at the bottom of your script. |
| `asyncio.gather(a, b)` | "Start coroutines `a` and `b` *both now*, wait for both, and give me a **list** of their results **in the order I passed them in**." This is what actually creates the concurrency. |
| `results[0]` / `results[1]` | **List indexing.** A list is an ordered container; `[0]` is the first item, `[1]` the second. `gather` returns a list, so `results[0]` is the first question's answer. |
| `question: str` and `-> str` | **Type hints.** Documentation for humans and editors: "this argument should be a string", "this function returns a string". Python does not enforce them at runtime. |
| `messages=[{"role": "user", "content": question}]` | A **list** (`[...]`) containing one **dict** (`{...}`). A dict is a set of `key: value` pairs. This is the same message shape you've used since Step 2. |
| `next(b.text for b in message.content if b.type == "text")` | A **generator expression** (the `... for ... in ... if ...` inside the parentheses) that lazily walks every content block, keeps only blocks whose `type` is `"text"`, and yields their `.text`. `next(...)` pulls **just the first one** and stops. This is how we skip past thinking blocks safely instead of assuming `content[0]`. |
| `model=`, `max_tokens=`, `messages=` | **Keyword arguments** ("kwargs"): named arguments passed as `name=value`, so order doesn't matter and the call reads clearly. |

---

### 📖 Reference: the async client

Every sync method has an async twin under `AsyncAnthropic`, with **identical
parameters** — you just `await` the call. This project's client setup stays the
same (same key, same `base_url`), only the class name and the `asyncio.run()`
entry point change:

```python
import os
import asyncio
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

load_dotenv()
config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}

client = AsyncAnthropic(
    api_key=config["ICA_API_KEY"],
    base_url="https://api.servicesessentials.ibm.com",
)

async def main() -> None:
    message = await client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello, Claude"}],
    )
    text = next(b.text for b in message.content if b.type == "text")
    print(text)

asyncio.run(main())
```

Compared with the sync version you already know, only three things changed:

| Sync (Steps 2–14) | Async (this step) |
|---|---|
| `from anthropic import Anthropic` | `from anthropic import AsyncAnthropic` |
| `message = client.messages.create(...)` | `message = await client.messages.create(...)` |
| top-level code runs directly | code lives in `async def main()`, launched by `asyncio.run(main())` |

**When to use this:** any FastAPI/async web service, or when you're firing off
many independent Claude calls concurrently (e.g. processing 50 documents at
once) and don't want to block on each one sequentially. Firing several requests
with `asyncio.gather` lets them run concurrently, so the whole batch finishes in
roughly the time of ONE request instead of N sequential ones.

**When *not* to use it:** a simple script that makes one call. Async adds
ceremony (`async def`, `await`, `asyncio.run`) and buys you nothing if there's
no second request to overlap with.

---

### 🔍 Line-by-line walkthrough of the exercise script

```python
import os                                  # 1
import asyncio                             # 2
from dotenv import load_dotenv             # 3
from anthropic import AsyncAnthropic       # 4

load_dotenv()                              # 5
config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}   # 6

client = AsyncAnthropic(                   # 7
    api_key=config["ICA_API_KEY"],         # 8
    base_url="https://api.servicesessentials.ibm.com",    # 9
)

async def ask(question: str) -> str:       # 10
    message = await client.messages.create(               # 11
        model="claude-sonnet-5",           # 12
        max_tokens=50,                     # 13
        messages=[{"role": "user", "content": question}],  # 14
    )
    return next(b.text for b in message.content if b.type == "text")  # 15

async def main() -> None:                  # 16
    results = await asyncio.gather(        # 17
        ask("What is the capital of Italy? One word."),    # 18
        ask("What is 9 times 9? Just the number."),        # 19
    )
    print("answer_1:", results[0])         # 20
    print("answer_2:", results[1])         # 21

asyncio.run(main())                        # 22
```

1. `os` — standard library module for talking to the operating system; we need
   it to read environment variables.
2. `asyncio` — Python's async engine. Needed for `asyncio.run` and
   `asyncio.gather`.
3. `load_dotenv` — from the `python-dotenv` package; reads your `.env` file and
   copies each `KEY=value` line into the process environment.
4. `AsyncAnthropic` — the async version of the SDK client class.
5. Actually performs the `.env` read. Nothing happens until you call it.
6. Builds a **dict** holding the key. `os.environ.get("ICA_API_KEY")` returns
   the value, or `None` if it's missing (`.get` doesn't crash on a missing key,
   unlike `os.environ["..."]`).
7. Constructs the client object. **No network call happens here** — a client is
   just configuration (key + URL + retry settings) held in memory.
8. `api_key=` your gateway credential, read out of the dict by key.
9. `base_url=` sends requests through this project's IBM gateway instead of
   `api.anthropic.com`. Required by the course checker.
10. Defines a coroutine function taking one string and (eventually) returning a
    string. `ask("...")` produces a coroutine; it runs only when awaited.
11. `await` the API call. This is the line where the coroutine pauses and hands
    control back to the event loop, so the *other* `ask(...)` can start its own
    request. This single keyword is what makes concurrency possible.
12. Model string — `claude-sonnet-5`, the course default (fast and cheap).
13. `max_tokens=50` caps the reply length. Small = cheap and quick; we only want
    a word or a number.
14. The messages list: one user turn whose content is whatever `question` was
    passed in.
15. Pull the first text block's text and return it. Using the generator
    expression instead of `message.content[0].text` protects you from models
    that emit a thinking block first.
16. `main` is the single top-level coroutine — the "front door" of the script.
    `-> None` means it returns nothing useful.
17. `await asyncio.gather(...)` — schedules **both** coroutines immediately, then
    waits for the slower of the two. Returns a list of results.
18–19. The two coroutine objects being handed to `gather`. Note there is **no
    `await` here** — you want to hand `gather` the un-started to-do notes so it
    can start them together. Awaiting them here would serialise them.
20. `results[0]` is the answer to question 18 — `gather` preserves argument
    order regardless of which request actually finished first.
21. `results[1]` is the answer to question 19.
22. `asyncio.run(main())` — the only synchronous line that does real work. It
    spins up the event loop, runs `main()` to completion, and closes the loop.

---

### ⚠️ What happens if you skip this

| If you skip / change… | What actually happens |
|---|---|
| the `await` on `client.messages.create(...)` | The call **never runs**. `message` becomes a coroutine object, and the next line dies with `AttributeError: 'coroutine' object has no attribute 'content'`, plus a `RuntimeWarning: coroutine ... was never awaited`. |
| `asyncio.run(main())` at the bottom | The script exits silently having printed nothing. You defined coroutines but never started an event loop, so no code inside `main()` ever executed. |
| `asyncio.gather` (using two separate `await ask(...)` calls instead) | It still *works* and still prints both answers — but sequentially, taking ~2× as long. You lose the entire benefit of this step, and **the Step 15 checker greps your source for `asyncio.gather` and will fail you.** |
| the `async` on `async def main()` | `await` inside a plain `def` is a hard `SyntaxError: 'await' outside async function`. Your script won't even start. |
| `AsyncAnthropic` (leaving it as `Anthropic`) | `await` on a normal (non-awaitable) `Message` object raises `TypeError: object Message can't be used in 'await' expression`. The two clients are not interchangeable. |
| `load_dotenv()` / `base_url=` | You'll get `AuthenticationError` (no key loaded) or requests aimed at the wrong host — and the checker greps your source for both, so it fails immediately. |
| `next(... if b.type == "text")`, indexing `content[0]` instead | Works most of the time, then randomly explodes with `AttributeError: 'ThinkingBlock' object has no attribute 'text'` when a model returns reasoning first. |

---

### 🏋️ Exercise

1. Create **`exercises/practice15_async_client.py`** with exactly this
   content:

   ```python
   import os
   import asyncio
   from dotenv import load_dotenv
   from anthropic import AsyncAnthropic

   load_dotenv()
   config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}

   client = AsyncAnthropic(
       api_key=config["ICA_API_KEY"],
       base_url="https://api.servicesessentials.ibm.com",
   )

   async def ask(question: str) -> str:
       message = await client.messages.create(
           model="claude-sonnet-5",
           max_tokens=50,
           messages=[{"role": "user", "content": question}],
       )
       return next(b.text for b in message.content if b.type == "text")

   async def main() -> None:
       results = await asyncio.gather(
           ask("What is the capital of Italy? One word."),
           ask("What is 9 times 9? Just the number."),
       )
       print("answer_1:", results[0])
       print("answer_2:", results[1])

   asyncio.run(main())
   ```

   ✅ **What should happen:** nothing yet — you're just creating the file.

2. Run it locally (make sure `.env` still has your `ICA_API_KEY`):

   ```bash
   python exercises/practice15_async_client.py
   ```

   ✅ **What should happen:** two printed lines, `answer_1: Rome` (or
   similar) and `answer_2: 81` — both requests ran concurrently via
   `asyncio.gather` rather than one after another.

   💡 **Optional proof it's really concurrent:** temporarily wrap the body of
   `main()` with timing and compare against two sequential `await ask(...)`
   calls:

   ```python
   import time

   start = time.time()
   # ... your gather call here ...
   print("elapsed:", round(time.time() - start, 2))
   ```

   The `gather` version should land near the time of a *single* request.
   Remove the timing code before committing so your output stays clean.

3. Commit and push:

   ```bash
   git add exercises/practice15_async_client.py
   git commit -m "Step 15: async client with AsyncAnthropic"
   git push
   ```

4. The **"Step 15 - Async Client"** check runs automatically. On success
   this issue closes and **Step 16** (Error handling) opens automatically.

<details>
<summary>Having trouble?</summary>

**Async-specific beginner errors**

- `RuntimeWarning: coroutine 'AsyncMessages.create' was never awaited` — you
  forgot `await` in front of `client.messages.create(...)`. The request was
  never sent.
- `AttributeError: 'coroutine' object has no attribute 'content'` — same root
  cause as above: `message` is the un-awaited to-do note, not a response.
- `SyntaxError: 'await' outside async function` — you used `await` in a plain
  `def` (or at the top level of the file). `await` only works inside
  `async def`.
- `TypeError: object Message can't be used in 'await' expression` — you're
  awaiting the **sync** `Anthropic` client. Switch the import and constructor to
  `AsyncAnthropic`.
- `RuntimeError: asyncio.run() cannot be called from a running event loop` —
  you're inside Jupyter/IPython, which already runs a loop. In a notebook use
  `await main()` directly in a cell; in a plain `.py` script keep
  `asyncio.run(main())`.
- `RuntimeError: Event loop is closed` on exit — harmless noise on some Windows
  Python builds after `asyncio.run` finishes; it doesn't affect the checker.
- `TypeError: 'coroutine' object is not subscriptable` on `results[0]` — you
  forgot the `await` in front of `asyncio.gather(...)`. `gather` itself must be
  awaited.
- Nothing prints at all, exit code 0 — you deleted or commented out
  `asyncio.run(main())`.

**Response-shape errors**

- If you see `AttributeError: 'ThinkingBlock' object has no attribute
  'text'` or `StopIteration`, some models return a thinking block before
  the text block — use `next(b.text for b in message.content if b.type
  == "text")` instead of indexing `content[0]` directly.

**Checker / config errors**

- `AsyncAnthropic` methods must be awaited — forgetting `await` gives you a
  coroutine object instead of a real response, and `message.content` will
  fail with an `AttributeError`.
- `asyncio.run(main())` must wrap an `async def main()` — you can't `await`
  at the top level of a plain script outside a coroutine.
- If both answers seem to run one after another rather than concurrently,
  double check you used `asyncio.gather(...)` and not two separate
  sequential `await ask(...)` calls.
- Keep `load_dotenv()`, `ICA_API_KEY`, and `base_url=` in your client setup
  — the checker verifies your script still uses this project's real client
  pattern, not the plain `AsyncAnthropic()` default.
- The checker also greps for the literal strings `AsyncAnthropic`,
  `async def`, `await `, `asyncio.run`, and `asyncio.gather`. If you renamed
  or refactored any of those away, add them back.
- `ModuleNotFoundError: No module named 'dotenv'` — install dependencies:
  `pip install anthropic python-dotenv`. (`asyncio` needs no install; it ships
  with Python.)

</details>

<details>
<summary>Stuck? Reveal the solution</summary>

Give it a real attempt first — debugging your own code is where the learning
happens. If you're properly stuck, the complete working reference is here:

**[`solutions/practice15_async_client.py`](../../solutions/practice15_async_client.py)**

Copy it to `exercises/practice15_async_client.py`, run it, then read it line by line and make
sure you can explain *why* each part is there.

</details>
