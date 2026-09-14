## 📘 Step 18 — Upload once, reference by ID

<!-- pedagogy-header:begin -->
**Phase 5: Scale & deployment** · Step 18 of 22 · ~20 min · ~$0.005 in API calls

> **Why this matters:** Upload the 200-page manual once and reference it by ID forever — re-sending the same base64 blob on every question is the most common way teams accidentally 10x their upload bandwidth.
<!-- pedagogy-header:end -->

### 🎯 What you'll learn

- What the Files API is for, and why re-sending a file on every request is wasteful
- The upload → `file_id` → reference lifecycle
- `with open(...) as f:` — what a **context manager** is and why it beats plain `open()`
- File modes `"w"` vs `"rb"` (text write vs binary read) and why upload needs binary
- **Tuples** — why `file=("name.txt", f, "text/plain")` has round brackets
- **Generator expressions** + `next(...)` — how to safely find the text block in a response
- What breaks if you forget the `with` block, use the wrong mode, or mistype the source dict

---

### 🧠 The concept in plain English

Before this step, every file you sent Claude was **base64-encoded and pasted
into the request body** (Steps 5, 10, 11). That works, but it means:

- the same 5 MB PDF is uploaded again on *every single question* you ask about it,
- your request payloads get huge and slow,
- and your code is cluttered with encoding boilerplate.

The Files API fixes this: **upload the file once, get back a short `file_id`
string, then just mention that ID** in as many `messages.create()` calls as you
like. The file lives on Anthropic's side; your requests stay tiny.

Think of `file_id` like a coat-check ticket. You hand over the coat once and get
a small ticket. From then on you show the ticket, not the coat.

---

### 🗺️ Diagram — the file lifecycle

```
   YOUR MACHINE                         ANTHROPIC / GATEWAY
   ────────────                         ───────────────────

 upload_notes.txt
        │
        │  (1) with open(..., "rb") as f
        │      client.files.upload(
        │          file=("upload_notes.txt", f, "text/plain"))
        ▼
   [ bytes ] ─────────────────────────▶  stores the file
                                                 │
        ◀────────────────────────────────────────┘
             (2) returns uploaded.id = "file_011CNha8..."
                            │
                            │  keep this short string
                            ▼
                     ┌──────────────┐
                     │   file_id    │  ← reuse as many times as you want
                     └──────┬───────┘
                            │
   (3) messages.create(...) │  {"type": "document",
       payload is TINY —    │   "source": {"type": "file",
       just the ID string   │             "file_id": file_id}}
                            ▼
                                       Claude reads the stored file
        ◀────────────────────────────────────────
             (4) response.content -> [TextBlock("summary...")]

   Housekeeping (all free):
     client.files.list()               → what have I uploaded?
     client.files.retrieve_metadata(id)→ size / type / created_at
     client.files.delete(id)           → clean up

   ┌─────────────────────────────────────────────────────────┐
   │ OLD WAY (base64):  file bytes travel on EVERY request   │
   │ FILES API:         file bytes travel ONCE, then just ID │
   └─────────────────────────────────────────────────────────┘
```

---

### 📖 Reference: the pattern

Upload a file once, get a `file_id` back, and reference it in as many
`messages.create()` calls as you want — no more re-sending base64 on every
request.

```python
# Upload
with open("/path/to/document.pdf", "rb") as f:
    uploaded = client.files.upload(file=("document.pdf", f, "application/pdf"))

file_id = uploaded.id
print(file_id)   # "file_011CNha8iCJcU1wXNR6q4V8w"

# Reference it in a message — document block, using {"type": "file", "file_id": ...}
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Summarize this document."},
                {"type": "document", "source": {"type": "file", "file_id": file_id}},
            ],
        }
    ],
)

# Manage files
client.files.list()
client.files.retrieve_metadata(file_id)
client.files.delete(file_id)
```

Images use the same pattern with
`{"type": "image", "source": {"type": "file", "file_id": ...}}`. Limits:
500MB per file, 1TB per organization; Files API operations themselves are
free (you only pay input-token cost when the file content is actually used
in a Messages request).

**When to use this:** Any file you'll reference more than once — a
reference PDF for repeated Q&A, a logo image reused across many generation
calls, or datasets fed into the code execution tool (Step 19). Skips the
base64-encoding overhead and keeps request payloads small.

> **⚠️ Note on this project's gateway:** the Files API endpoints
> (`client.files.upload`, `.list`, `.retrieve_metadata`, `.delete`) are part
> of the standard `anthropic` SDK surface and are used exactly as documented
> above. If your gateway/base_url doesn't proxy the Files API the same way
> it proxies `messages.create()`, you may see a 404 or "not supported"
> error from `files.upload()` — if that happens, note it in your PR/issue
> comment and the checker will still validate your *code pattern* is
> correct (upload → get file_id → reference in a document block), even if
> the live call needs a direct `ANTHROPIC_API_KEY` fallback instead of the
> gateway. This is the one step where the closest available real pattern is
> used, per the course notes.

---

### 🐍 Python constructs used in this step

| Construct | Plain-English meaning |
|---|---|
| `open("name.txt", "w")` | Opens a file for **w**riting **text**. Creates it if missing, **erases it if it exists**. |
| `open("name.txt", "rb")` | Opens for **r**eading in **b**inary mode. You get raw `bytes`, not `str`. Uploads need bytes because a file could be a PDF or PNG, not just text. |
| `with ... as f:` | A **context manager**. It guarantees `f.close()` runs when the indented block ends — even if an exception is raised inside. Without it, the file handle stays open and your written bytes may sit unflushed in a buffer. |
| `f` | The **file object** the `with` line hands you. `f.write(...)` puts text in; passing `f` itself to `upload()` lets the SDK stream bytes out. |
| `f.write("...")` | Writes a string into an open text-mode file. Returns the number of characters written (usually ignored). |
| `("upload_notes.txt", f, "text/plain")` | A **tuple** — an ordered, immutable group in *round* brackets. The SDK expects exactly three parts in this order: **filename**, **file object**, **MIME type**. |
| **MIME type** | A short string telling the server what kind of bytes these are: `text/plain`, `application/pdf`, `image/png`. Get it wrong and the server may refuse or misinterpret the file. |
| `uploaded.id` | Attribute on the object returned by `upload()`. The `file_...` string is the only thing you need to keep. |
| nested dicts | `{"type": "document", "source": {"type": "file", "file_id": ...}}` is a dict whose `"source"` value is *another* dict. The API's shape is strict — the `file_id` lives on the inner one, not the outer one. |
| `b.type == "text"` | Reading the `.type` field off a content block. Responses can contain several block kinds (`thinking`, `text`, `tool_use`); `==` compares for equality. |
| `(b.text for b in response.content if b.type == "text")` | A **generator expression**: a lazy, one-at-a-time sequence. Round brackets (not `[]`) mean it doesn't build a whole list — it yields values on demand. The `if` clause filters out non-text blocks. |
| `next(gen)` | Pulls the **first** item out of a generator and stops there. Combined above, it means "give me the text of the first text block". Raises `StopIteration` if the generator is empty. |
| `next(gen, "")` | Same, but with a **default**: returns `""` instead of raising if nothing matches. Safer in production code. |

---

### 🔍 Line-by-line walkthrough of the exercise script

```python
with open("upload_notes.txt", "w") as f:                              # 1
    f.write("Claude is an AI model made by Anthropic. ...")           # 2

with open("upload_notes.txt", "rb") as f:                             # 3
    uploaded = client.files.upload(                                   # 4
        file=("upload_notes.txt", f, "text/plain"))                   # 5

print("file_id:", uploaded.id)                                        # 6

response = client.messages.create(                                    # 7
    model="claude-sonnet-5",                                          # 8
    max_tokens=200,                                                   # 9
    messages=[{                                                       # 10
        "role": "user",
        "content": [                                                  # 11
            {"type": "text", "text": "Summarize this document in one sentence."},   # 12
            {"type": "document",                                      # 13
             "source": {"type": "file", "file_id": uploaded.id}},     # 14
        ],
    }],
)
summary = next(b.text for b in response.content if b.type == "text")  # 15
print("summary:", summary)                                            # 16
```

1. Creates a small local file to have something real to upload. Mode `"w"`
   truncates any existing file — fine here, since we own the name.
2. Writes one sentence of content. Keeping it short means the summary is easy to
   eyeball for correctness.
3. **Re-opens the same file, this time as `"rb"`.** Two separate `with` blocks,
   because you can't write and binary-read through one handle. When block 1
   ended, Python flushed and closed the file, so the bytes are safely on disk.
4. `client.files.upload(...)` — the actual HTTP upload. This is the new API
   surface in this step.
5. The three-part tuple: filename the server should record, the open binary
   handle to stream from, and the MIME type. Order matters.
6. Prints the returned ID. **The label `file_id:` is required by the checker**,
   and it also verifies the value starts with `file_`.
7. A completely ordinary `messages.create()` call — the Files API doesn't need a
   special method to *use* a file.
8. Sonnet: capable and cheap enough for a one-sentence summary.
9. 200 tokens is plenty for one sentence.
10. `messages` is a list holding one user-turn dict.
11. `content` is a **list of blocks**, not a plain string — you need block form
    whenever you mix text with a document or image.
12. Block 1: the instruction, as a `text` block.
13. Block 2 opens the `document` block.
14. The reference itself. `"type": "file"` tells the API "look this up by ID
    rather than expecting inline base64", and `file_id` is the ticket from line 6.
15. Finds the text of the first `text` block. Written this way (rather than
    `response.content[0].text`) because thinking-enabled models put a
    `ThinkingBlock` at index 0 — indexing blindly would crash.
16. Prints the summary under the required `summary:` label.

---

### ⚠️ What happens if you skip this

| If you skip / change… | What actually happens |
|---|---|
| the `with` on the **write** block (plain `open(...)` + `write`) | The handle is never closed, so your text can still be sitting in an OS buffer when the upload reads the file. You upload **0 bytes** and Claude summarizes nothing. Classic, maddening bug. |
| the `with` on the **read** block | The file object leaks. On a loop over many files you eventually hit `OSError: [Errno 24] Too many open files`. |
| mode `"rb"` → `"r"` | You pass a *text* handle where bytes are expected → `TypeError` from the HTTP layer, or a corrupted upload for any non-ASCII/binary file. Always `"rb"` for uploads. |
| the tuple's round brackets (`file=["name", f, "text/plain"]`) | May work by luck, may raise — the SDK documents a **tuple**. Don't gamble; use `(...)`. |
| the tuple order (e.g. MIME type second) | The server records a nonsense filename and rejects or misreads the content type. |
| printing `uploaded` instead of `uploaded.id` | You print a whole object repr; the checker's `file_id: file_` test fails even though the upload worked. |
| `"source": {"type": "file", ...}` → `"type": "base64"` | The API expects inline data that isn't there → `BadRequestError`. The `source.type` is what selects reference-vs-inline mode. |
| putting `file_id` on the outer dict instead of inside `source` | `BadRequestError: unexpected field` — or the document is silently treated as empty and the summary is generic waffle. |
| `next(... if b.type == "text")` → `response.content[0].text` | `AttributeError: 'ThinkingBlock' object has no attribute 'text'` on thinking-capable models. |
| re-uploading the file on every question instead of reusing the ID | It works, but you pay the transfer cost every time — you've thrown away the entire benefit of this step. |
| deleting nothing, ever | You'll drift toward the 1 TB org quota. `client.files.delete(file_id)` is free; use it for throwaway uploads. |

---

### 🏋️ Exercise

1. Create a new file at `exercises/practice18_files_api.py`.

2. Set up the client exactly like previous steps (`load_dotenv()`,
   `ICA_API_KEY`, `base_url=`).

3. Write a small local text file, upload it with `client.files.upload()`,
   and print its ID:

```python
with open("upload_notes.txt", "w") as f:
    f.write("Claude is an AI model made by Anthropic. It can read text, images, and PDFs.")

with open("upload_notes.txt", "rb") as f:
    uploaded = client.files.upload(file=("upload_notes.txt", f, "text/plain"))

print("file_id:", uploaded.id)
```

4. Reference `uploaded.id` in a `messages.create()` call using a
   `document` content block, and print Claude's summary:

```python
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Summarize this document in one sentence."},
            {"type": "document", "source": {"type": "file", "file_id": uploaded.id}},
        ],
    }],
)
summary = next(b.text for b in response.content if b.type == "text")
print("summary:", summary)
```

Your complete script should look like this:

```python
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ["ICA_API_KEY"],
    base_url="https://api.servicesessentials.ibm.com",
)

# 1. Create something real to upload.
with open("upload_notes.txt", "w") as f:
    f.write("Claude is an AI model made by Anthropic. It can read text, images, and PDFs.")

# 2. Upload it once and keep the ID.
with open("upload_notes.txt", "rb") as f:
    uploaded = client.files.upload(file=("upload_notes.txt", f, "text/plain"))

print("file_id:", uploaded.id)

# 3. Reference the file by ID instead of re-sending its bytes.
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Summarize this document in one sentence."},
            {"type": "document", "source": {"type": "file", "file_id": uploaded.id}},
        ],
    }],
)

summary = next(b.text for b in response.content if b.type == "text")
print("summary:", summary)
```

✅ What should happen: you'll see a `file_id:` line starting with `file_`,
followed by a `summary:` line containing a one-sentence description that
reflects the uploaded file's content (mentioning Claude/Anthropic).

Roughly:

```
file_id: file_011CNha8iCJcU1wXNR6q4V8w
summary: Claude is an Anthropic AI model capable of reading text, images, and PDFs.
```

5. Run it with `python exercises/practice18_files_api.py`.

✅ What should happen: both lines print with no errors. This proves the
file was uploaded, referenced by ID (not re-pasted as text), and Claude
successfully read it.

6. Commit and push your file to `main`. The workflow will run the
   checker, comment on this issue, and open Step 19.

<details>
<summary>Having trouble?</summary>

**Expected beginner errors**

- `FileNotFoundError: [Errno 2] No such file or directory: 'upload_notes.txt'` —
  the read block ran before the write block, or you ran `python` from a different
  directory than you expect. The path is relative to your **current working
  directory**, not to the script's location.
- `ValueError: I/O operation on closed file` — you moved `client.files.upload(...)`
  *outside* the `with` block. The upload must happen while the handle is open,
  i.e. indented inside it.
- `TypeError: a bytes-like object is required, not 'str'` (or the reverse) — mode
  mix-up: `"w"`/`"r"` are text, `"rb"`/`"wb"` are bytes. Upload needs `"rb"`.
- Empty or generic `summary:` — you likely uploaded an empty file. Check
  `upload_notes.txt` actually has content (`cat upload_notes.txt`); if it's
  empty, your write block is missing its `with` and never flushed.
- `AttributeError: 'Files' object has no attribute 'uploads'` — the method is
  singular: `client.files.upload(...)`.
- `IndentationError: expected an indented block after 'with' statement` — the
  body of every `with` must be indented.
- If you see `AttributeError: 'ThinkingBlock' object has no attribute
  'text'` or `StopIteration`, some models return a thinking block before
  the text block — use `next(b.text for b in response.content if b.type
  == "text")` instead of indexing `content[0]` directly.
- `StopIteration` even with the generator — the response contained no text block
  at all (rare). Use the defaulted form `next(..., "")` to see what happened
  instead of crashing.

**Course-specific gotchas**

- If `client.files.upload()` raises a 404 or "not supported" error on this
  project's gateway, that's a known limitation noted above — try again with
  a direct `anthropic.Anthropic()` client (no `base_url=` override) using
  your own `ANTHROPIC_API_KEY` if you have one, or ask in the course
  discussion for the current gateway status.
- If the `file_id:` line is missing, double check you printed
  `uploaded.id` (not `uploaded` itself).
- If `summary:` doesn't reflect the file content, make sure the
  `document` content block's `source` dict uses `"type": "file"` and
  `"file_id": uploaded.id` exactly — a typo here silently falls back to an
  empty/invalid reference.
- Keep `load_dotenv()`, `ICA_API_KEY`, and `base_url=` in your client setup
  — the checker verifies your script still uses this project's real client
  pattern.
- The checker also greps your source for `files.upload` and `file_id`, and
  requires the printed value to begin with `file_`. Keep both labels exactly
  `file_id:` and `summary:`.
- Whole script must finish within 60 seconds — one upload plus one short
  summary is well inside that.

</details>

<details>
<summary>Stuck? Reveal the solution</summary>

Give it a real attempt first — debugging your own code is where the learning
happens. If you're properly stuck, the complete working reference is here:

**[`solutions/practice18_files_api.py`](../../solutions/practice18_files_api.py)**

Copy it to `exercises/practice18_files_api.py`, run it, then read it line by line and make
sure you can explain *why* each part is there.

</details>
