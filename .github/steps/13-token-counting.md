## 📘 Step 13 — Count tokens before you spend them

<!-- pedagogy-header:begin -->
**Phase 4: Production concerns** · Step 13 of 22 · ~15 min · $0 in API calls

> **Why this matters:** `count_tokens()` is a free dry run — it lets you reject an oversized request or show a cost estimate *before* you spend anything, which is how you avoid a surprise invoice.
<!-- pedagogy-header:end -->

### 🎯 What you'll learn

- What a **token** actually is, and why it isn't a word or a character
- How `client.messages.count_tokens()` prices a request **before** you send it
- Why `count_tokens()` takes the same shape as `messages.create()` but **no `max_tokens`**
- How to split a long string across lines without adding stray characters
- Python constructs used here: **implicit string concatenation**, **parentheses for line continuation**, **dict spanning multiple lines**, **trailing commas**, **attribute access**, **comparison of two integers**

---

### 🧠 Theory — a free dry run

Models don't read characters or words; they read **tokens**. A token is a
frequent chunk of text — often a whole short word, sometimes a word fragment,
sometimes just punctuation. As a rough English rule of thumb, **1 token ≈ 4
characters ≈ ¾ of a word**.

```
   "Hi"                                       →  1 token
   "photosynthesis"                           →  4 tokens ("photo|synth|es|is")
   "Please write a detailed explanation."      →  ~7 tokens
```

You're billed per token, and every model has a context window measured in
tokens. So "how big is this request?" is a question you often need answered
*before* paying for an answer.

`client.messages.count_tokens()` does exactly that. It accepts the same
`model=` and `messages=` you'd give `messages.create()`, and returns an
object with one useful field: `.input_tokens`. It generates **nothing**, so
there are no output tokens to pay for.

#### count_tokens vs create

```
   ┌───────────────────────────────────────────────────────────────────┐
   │  client.messages.count_tokens(model=..., messages=[...])          │
   │  ───────────────────────────────────────────────────────────────  │
   │   ✅ measures input size        ❌ generates no text              │
   │   ✅ no max_tokens needed       ❌ returns no .content            │
   │   → returns  .input_tokens  (an int)                              │
   └───────────────────────────────────────────────────────────────────┘
                                  ▼  once you're happy with the size
   ┌───────────────────────────────────────────────────────────────────┐
   │  client.messages.create(model=..., max_tokens=N, messages=[...])  │
   │  ───────────────────────────────────────────────────────────────  │
   │   ✅ generates a reply          💸 you pay for input + output      │
   │   ⚠️ max_tokens is REQUIRED     → returns  .content  (block list) │
   └───────────────────────────────────────────────────────────────────┘
```

`max_tokens` is a cap on the **output** you haven't asked for yet, so
`count_tokens` has no use for it — that's the whole reason it's absent.

Same client setup as every previous step — load `.env`, read
`ICA_API_KEY`, point at the gateway `base_url`:

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

count = client.messages.count_tokens(
    model="claude-sonnet-5",
    messages=[{"role": "user", "content": "Hello, world"}],
)
print(count.input_tokens)   # e.g. 10
```

**What to expect:** a small integer — the exact input token count for that
message, with zero completion tokens spent, since `count_tokens` never
actually generates a response.

**When to use this:** budget-checking before an expensive request
(especially with big documents or long conversation history), trimming
context to fit a window, or estimating cost for a batch job before
submitting it. It's free and fast — always cheaper than discovering you
blew your context window mid-request.

---

### 🐍 Python concepts, defined as they appear

**Implicit string concatenation** — this is the one that surprises people.
Two string literals sitting next to each other, with nothing between them,
are joined by Python automatically:

```python
"hello " "world"        # → "hello world"
```

Which is why this works inside parentheses across several lines:

```python
message = {
    "role": "user",
    "content": (
        "Please write a detailed, three-paragraph explanation of how "
        "photosynthesis works, including the role of chlorophyll and "
        "sunlight."
    ),
}
```

There is **no `+`** and **no comma** between the pieces. Python glues them
into one long string. Notice each fragment ends with a space *before* the
closing quote — without it you'd get `how photosynthesis` run together as
`howphotosynthesis`.

⚠️ If you accidentally put a **comma** between them, you no longer have a
string — you have a **tuple** of three strings, and the API will reject it
with a validation error. This is a classic beginner trap.

**Parentheses for line continuation** — Python normally treats a newline as
the end of a statement. Inside `(`, `[`, or `{`, newlines are ignored, so
you can break long expressions across lines for readability. The `(` after
`"content":` exists purely to permit the three-line string.

**A dict spanning multiple lines** —

```python
messages=[{
    "role": "user",
    "content": (...),
}]
```

Same dict as if it were on one line; the brackets make the newlines
invisible to Python. Formatting is for humans.

**Trailing commas** — the comma after the last item (`"sunlight."),` then
`}]`) is legal and encouraged: it means adding another key later is a
one-line diff, and you can't forget a comma. Python ignores it.

**Attribute access** — `short_count.input_tokens` reads the integer field
off the object `count_tokens` returned. Objects use dots; the dicts you
build use `["brackets"]`.

**Comparing two integers** — the checker parses both printed numbers and
asserts `long_tokens > short_tokens`. That's the observable proof that token
count scales with text length; nothing in your code needs to do the
comparison.

---

### 🏋️ Exercise

1. Create **`exercises/practice13_token_counting.py`** with exactly this
   content:

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

   short_count = client.messages.count_tokens(
       model="claude-sonnet-5",
       messages=[{"role": "user", "content": "Hi"}],
   )
   long_count = client.messages.count_tokens(
       model="claude-sonnet-5",
       messages=[{
           "role": "user",
           "content": (
               "Please write a detailed, three-paragraph explanation of how "
               "photosynthesis works, including the role of chlorophyll and "
               "sunlight."
           ),
       }],
   )
   print("short_tokens:", short_count.input_tokens)
   print("long_tokens:", long_count.input_tokens)
   ```

   ✅ **What should happen:** nothing yet — you're just creating the file.

---

### 🔍 Line-by-line walkthrough

| Code | What it does, in plain English |
| --- | --- |
| `import os` | For reading environment variables. |
| `from dotenv import load_dotenv` | One function from `python-dotenv`. |
| `from anthropic import Anthropic` | The SDK client class. |
| `load_dotenv()` | Loads `.env` into the environment so the key is visible to `os.environ`. |
| `config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}` | A **dict** holding the key; `.get()` returns `None` instead of raising if it's missing. |
| `client = Anthropic(api_key=..., base_url=...)` | Builds the client. `base_url` routes through this course's gateway rather than the public endpoint. |
| `short_count = client.messages.count_tokens(` | The counting call. Note the method name is `count_tokens`, not `create` — it never generates text. |
| `model="claude-sonnet-5",` | Tokenisation is model-specific, so you must say which model you're measuring for. |
| `messages=[{"role": "user", "content": "Hi"}],` | A **list** with one **dict**: a single two-character user message. |
| *(no `max_tokens` here)* | Deliberate. `max_tokens` caps generated output, and nothing is generated. |
| `long_count = client.messages.count_tokens(` | The same call for a much longer message, so we can compare. |
| `messages=[{` | Opening the list and the dict; the newline is fine because we're inside brackets. |
| `"role": "user",` | Who's speaking. |
| `"content": (` | The open parenthesis lets the string continue over three lines. |
| `"Please write a detailed, three-paragraph explanation of how "` | Fragment 1 — note the trailing space inside the quote. |
| `"photosynthesis works, including the role of chlorophyll and "` | Fragment 2 — also ends with a space. |
| `"sunlight."` | Fragment 3. Python concatenates all three into one string with **no commas** between them. |
| `),` | Closes the parenthesis, then a comma to end the `"content"` entry. |
| `}],` | Closes the dict and the list. |
| `print("short_tokens:", short_count.input_tokens)` | Prints the small count. `.input_tokens` is the only field you need. |
| `print("long_tokens:", long_count.input_tokens)` | Prints the larger count. Should be visibly bigger. |

---

### ⚠️ What happens if you skip this

**Put a comma between the string fragments:**

```text
"content": (
    "Please write a detailed... ",     # ← this comma is the bug
    "photosynthesis works... ",
),
```

You've built a **tuple** of strings, not a string. Result:

```
anthropic.BadRequestError: 400 - messages.0.content: Input should be a valid string
```

Remove the commas — adjacent literals concatenate on their own.

**Forget the trailing space at the end of each fragment** → the words fuse
(`howphotosynthesis`), which still runs but tokenises oddly and reads wrong.
Put the space *inside* the closing quote.

**Call `create()` instead of `count_tokens()`** → you get a real generated
reply, you pay for output tokens, and there's no `.input_tokens` on the
result in the place you expect (it's `response.usage.input_tokens`). Worse,
`create()` **requires** `max_tokens`, so you'd get:

```
TypeError: create() missing 1 required keyword-only argument: 'max_tokens'
```

**Try to read `.content` off the count result** →

```
AttributeError: 'MessageTokensCount' object has no attribute 'content'
```

Nothing was generated, so there's no content. Only `.input_tokens` exists.

**Swap the two message bodies** → `long_tokens` comes back smaller than
`short_tokens` and the checker fails with an explicit message telling you the
long one should be bigger.

**Rename either printed label** (e.g. `print("short:", ...)`) → the checker
greps stdout for the exact labels `short_tokens:` and `long_tokens:` and
fails. Keep them verbatim.

**Skip `load_dotenv()`** → `api_key` is `None` and you get a 401 before any
counting happens.

---

2. Run it locally (make sure `.env` still has your `ICA_API_KEY`):

   ```bash
   python exercises/practice13_token_counting.py
   ```

   ✅ **What should happen:** two lines print. `short_tokens` should be a
   small number (roughly 1–5), and `long_tokens` should be noticeably
   larger (several dozen) — confirming the count scales with text length.
   Roughly:

   ```
   short_tokens: 9
   long_tokens: 32
   ```

   Exact numbers vary by model and SDK version (a few tokens of overhead are
   always added for message framing, which is why `"Hi"` costs more than 1).
   All that matters is that the long one is larger.

3. Commit and push:

   ```bash
   git add exercises/practice13_token_counting.py
   git commit -m "Step 13: count tokens before sending a request"
   git push
   ```

4. The **"Step 13 - Token Counting"** check runs automatically. On success
   this issue closes and **Step 14** (Batch API) opens automatically.

<details>
<summary>Having trouble?</summary>

**Setup problems**

- Double-check the file path is exactly
  `exercises/practice13_token_counting.py`.
- `ModuleNotFoundError: No module named 'dotenv'` — install
  `python-dotenv` (the package name differs from the import name).
- 401 / authentication error — confirm `.env` is in the directory you run
  `python` from and `load_dotenv()` runs before `Anthropic(...)`.

**Errors specific to this step**

- `400 - messages.0.content: Input should be a valid string` — you put
  commas between the multi-line string fragments, creating a tuple. Delete
  the commas.
- `AttributeError: 'MessageTokensCount' object has no attribute 'content'`
  — `count_tokens()` generates nothing; the only field is `.input_tokens`.
- `AttributeError: ... no attribute 'count_tokens'` — your `anthropic`
  package predates the method. Run `pip install --upgrade anthropic`.
- `TypeError: count_tokens() got an unexpected keyword argument
  'max_tokens'` — leave `max_tokens` out entirely.
- `count_tokens()` takes the same `model=` and `messages=` shape as
  `messages.create()`, but **no** `max_tokens` — leaving it out (or adding
  it) shouldn't error, but the exercise above deliberately omits it since
  it isn't needed for counting.
- If `long_tokens` isn't bigger than `short_tokens`, double check you
  didn't swap the two message contents.
- `SyntaxError: invalid syntax` around the multi-line string — a
  parenthesis is unbalanced. Count that every `(`, `[`, `{` has a partner.
- Both counts print the same number — you probably passed the same
  `messages` list to both calls. Check the second one uses the long text.

**Checker specifics**

- Keep both `print("short_tokens": ...)` and `print("long_tokens": ...)`
  lines exactly as labeled — the checker looks for both labels in your
  script's stdout.
- The checker also greps your source for `count_tokens` and requires
  `long_tokens` to parse as a larger integer than `short_tokens`.
- Keep `load_dotenv()`, `ICA_API_KEY`, and `base_url=` in your client setup
  — the checker verifies your script still uses this project's real client
  pattern, not the plain `Anthropic()` default.

</details>

<details>
<summary>Stuck? Reveal the solution</summary>

Give it a real attempt first — debugging your own code is where the learning
happens. If you're properly stuck, the complete working reference is here:

**[`solutions/practice13_token_counting.py`](../../solutions/practice13_token_counting.py)**

Copy it to `exercises/practice13_token_counting.py`, run it, then read it line by line and make
sure you can explain *why* each part is there.

</details>
