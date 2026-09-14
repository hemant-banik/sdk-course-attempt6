## 📘 Step 10 — Vision: multiple images in one request

<!-- pedagogy-header:begin -->
**Phase 2: Input & output types** · Step 10 of 22 · ~15 min · ~$0.005 in API calls

> **Why this matters:** Before-and-after photos, a chart next to its source table, two versions of a design — real comparison tasks need several images in one request, not several requests.
<!-- pedagogy-header:end -->

### 🎯 What you'll learn

- How to put **more than one image** in a single message so Claude can compare them
- Why **block order inside `content`** is what makes "first image" and "second image" meaningful
- What **base64** actually is and why images must be encoded before they travel over an API
- How to write and call your **own function** to avoid copy-pasting the encoding logic
- Python constructs used here: **`def` (function definition)**, **parameters**, **`return`**, **tuple**, **in-memory buffer (`io.BytesIO`)**, **method chaining**, **list of dicts**, **comments**

---

### 🧠 Theory — one message, several pictures

In Step 5 you sent a single base64 image. Nothing stops you from sending
several. A user message's `content` can be a **list**, and you can put as
many `image` blocks in that list as you like, followed by a `text` block
asking about them.

Claude reads the list **top to bottom**. So the first `image` block *is*
"the first image". That's the entire trick — there's no numbering field, no
label; position in the list is the identity.

```python
message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=300,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image1_b64}},
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image2_b64}},
                {"type": "text", "text": "What color is the first image, and what color is the second?"},
            ],
        }
    ],
)
```

#### How the content list maps to what Claude "sees"

```
messages = [                                 What Claude perceives
  {                                          ─────────────────────
    "role": "user",
    "content": [
      ┌────────────────────────────────┐
      │ {"type": "image", ...red...}   │ ───►  🟥  "this is the 1st thing shown"
      └────────────────────────────────┘
      ┌────────────────────────────────┐
      │ {"type": "image", ...blue...}  │ ───►  🟦  "this is the 2nd thing shown"
      └────────────────────────────────┘
      ┌────────────────────────────────┐
      │ {"type": "text",  "What color  │ ───►  ❓  the question, asked LAST
      │  is the first / the second?"}  │
      └────────────────────────────────┘
    ]
  }
]

Reorder the list  ➜  "first" and "second" swap meaning. Nothing else changes.
```

**When to use this:** Comparing before/after images, matching a reference
photo against candidates, or asking Claude to reconcile info spread across
several images.

---

### 🖼️ What base64 is, in one paragraph

An API request is text (JSON). A PNG file is raw bytes, many of which are
not valid text characters. **Base64** is a standard scheme that rewrites
arbitrary bytes using only 64 safe characters (`A–Z`, `a–z`, `0–9`, `+`,
`/`). It makes binary data survive a text channel. The cost is about 33%
extra size. You encode before sending; the API decodes on arrival. That's
all — it is *not* encryption and offers no secrecy.

```
  PNG bytes            base64 text                      what you send
  89 50 4E 47 ...  ──► "iVBORw0KGgoAAAANSUhEUg..."  ──►  "data": "iVBORw0..."
     (binary)            (safe ASCII characters)
```

---

### 🐍 Python concepts, defined as they appear

**`def` — defining your own function.** `def` starts a reusable named block
of code. Everything indented under it is the **body**. The names in
parentheses are **parameters** — placeholders filled in when you call it.

```python
def double(n):        # 'n' is a parameter
    return n * 2      # 'return' hands a value back to the caller

double(21)            # 42  — '21' is the argument
```

**`return`** — ends the function immediately and sends a value back. A
function without `return` gives back `None`.

**A tuple** — like a list but written with round brackets and immutable.
`(220, 20, 20)` is a 3-tuple representing an RGB colour: 220 red, 20 green,
20 blue → a strong red. Pillow accepts colours as tuples.

```python
point = (3, 4)        # tuple — cannot be changed after creation
colors = [3, 4]       # list  — can be changed
```

**`io.BytesIO()` — an in-memory file.** Pillow's `img.save()` normally
writes to disk. `BytesIO` gives it a fake file that lives in RAM, so we
never touch the filesystem. Afterwards `buf.getvalue()` retrieves the bytes
that were "written".

```python
buf = io.BytesIO()          # an empty in-memory file
img.save(buf, format="PNG") # write PNG bytes into it
raw = buf.getvalue()        # get those bytes back out
```

**Method chaining** — calling a method on the result of another call, left
to right:

```python
base64.standard_b64encode(buf.getvalue()).decode("utf-8")
#      └─ step 2: encode bytes → base64 bytes ──┘ └ step 3: bytes → str ┘
#         └─ step 1: get raw PNG bytes ─┘
```

Step 3 is needed because `standard_b64encode` returns **bytes**
(`b"iVBOR..."`), and JSON needs a **string** (`"iVBOR..."`). `.decode("utf-8")`
converts bytes to text.

**A comment** — anything after `#` on a line is ignored by Python. We use
`# red` and `# blue` to document which colour tuple is which, since
`(220, 20, 20)` isn't self-explanatory.

**Blank lines around a `def`** — PEP 8 (Python's style guide) asks for two
blank lines before and after a top-level function definition. Purely
cosmetic; Python doesn't care.

---

### 🏋️ Exercise

1. In this repo, create a new file at
   **`exercises/practice10_vision.py`** with exactly this content:

   ```python
   import base64
   import io
   import os

   from dotenv import load_dotenv
   from PIL import Image
   from anthropic import Anthropic

   load_dotenv()
   config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}

   client = Anthropic(
       api_key=config["ICA_API_KEY"],
       base_url="https://api.servicesessentials.ibm.com",
   )


   def make_image_b64(color):
       img = Image.new("RGB", (32, 32), color=color)
       buf = io.BytesIO()
       img.save(buf, format="PNG")
       return base64.standard_b64encode(buf.getvalue()).decode("utf-8")


   image1_b64 = make_image_b64((220, 20, 20))   # red
   image2_b64 = make_image_b64((20, 80, 220))   # blue

   message = client.messages.create(
       model="claude-sonnet-5",
       max_tokens=300,
       messages=[
           {
               "role": "user",
               "content": [
                   {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image1_b64}},
                   {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image2_b64}},
                   {"type": "text", "text": "What color is the first image, and what color is the second? Answer in the form 'first: <color>, second: <color>'."},
               ],
           }
       ],
   )

   for block in message.content:
       if block.type == "text":
           print("answer:", block.text)
           break
   ```

---

### 🔍 Line-by-line walkthrough

| Code | What it does, in plain English |
| --- | --- |
| `import base64` | Standard library encoder/decoder for base64. |
| `import io` | Standard library tools for streams — we want `io.BytesIO`, the in-memory file. |
| `import os` | For reading environment variables. |
| `from dotenv import load_dotenv` | One function from the `python-dotenv` package. |
| `from PIL import Image` | Pillow, the image library. Confusingly the *package* is `pillow` but the *import* is `PIL` (a historical name). We only need the `Image` class. |
| `from anthropic import Anthropic` | The SDK client class. |
| `load_dotenv()` | Loads `.env` into the environment so `os.environ` can see your key. |
| `config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}` | A **dict** with the key. `.get()` returns `None` rather than crashing if unset. |
| `client = Anthropic(api_key=..., base_url=...)` | Builds the client. `base_url` sends traffic through this course's gateway. |
| `def make_image_b64(color):` | Defines a function with one **parameter**, `color`. We call it twice, which is exactly why it's a function — write the encoding logic once, reuse it. |
| `img = Image.new("RGB", (32, 32), color=color)` | Creates a brand-new image. `"RGB"` is the colour mode; `(32, 32)` is a **tuple** giving width and height in pixels; `color=color` is a **keyword argument** whose value is the parameter we received. Tiny 32×32 images keep the base64 payload small. |
| `buf = io.BytesIO()` | An empty in-memory file to write into. |
| `img.save(buf, format="PNG")` | Encodes the image as PNG into that buffer. `format=` is required because `buf` has no filename for Pillow to infer from. |
| `return base64.standard_b64encode(buf.getvalue()).decode("utf-8")` | Three chained steps: pull the raw bytes out of the buffer, base64-encode them, then convert the resulting bytes to a `str`. `return` hands that string back. |
| `image1_b64 = make_image_b64((220, 20, 20))   # red` | Calls our function. Note the **double parentheses**: the outer pair is the function call, the inner pair is the tuple. `make_image_b64(220, 20, 20)` would be an error — that's three arguments, not one tuple. |
| `image2_b64 = make_image_b64((20, 80, 220))   # blue` | Same again for blue. |
| `message = client.messages.create(` | The API call. |
| `model="claude-sonnet-5",` | Sonnet handles this easily and costs far less than larger models. |
| `max_tokens=300,` | Ceiling on the reply length. A short colour description needs nowhere near this. |
| `messages=[{...}]` | A **list** with one user turn. |
| `"content": [` | Here `content` is a **list of blocks**, not a plain string — that's what lets one message hold two images plus text. |
| `{"type": "image", "source": {...}}` (first) | The red image. `"source"` is a **nested dict** saying *how* the data arrives: `"type": "base64"` (inline, as opposed to a URL or a Files API id), `"media_type": "image/png"` (the MIME type, so the API knows how to decode), and `"data"` (the base64 string). |
| `{"type": "image", "source": {...}}` (second) | The blue image. Being second in the list is the *only* thing that makes it "the second image". |
| `{"type": "text", "text": "What color is the first image, ..."}` | The question, placed **after** both images so Claude has already seen them. We also request a fixed output shape so the reply is easy to check. |
| `for block in message.content:` | Loop over the response blocks. |
| `if block.type == "text":` | Find the text block, ignoring any other block type. |
| `print("answer:", block.text)` | Print it with the label the checker looks for. |
| `break` | Stop after the first text block — we have what we need. |

---

### ⚠️ What happens if you skip this

**Put the text block *before* the images** → Claude is being asked "which is
first?" before it has seen anything, and often answers vaguely or hedges.
The checker then fails on the missing `red`/`blue` words. **Images first,
question last.**

**Send only one image block** → the checker fails immediately with *"Your
script needs at least two image content blocks in the same message."* It
literally counts occurrences of `"type": "image"` in your source.

**Swap the red and blue images** → Claude correctly reports blue first, but
the exercise's whole point is that the *order* is the mapping. Keep
red-then-blue.

**Skip `.decode("utf-8")`** →

```
TypeError: Object of type bytes is not JSON serializable
```

`standard_b64encode` gives back bytes; JSON only holds strings.

**Skip `format="PNG"` in `img.save(buf, ...)`** →

```
ValueError: unknown file extension:
```

Pillow normally guesses the format from the filename, and a `BytesIO` has
no filename, so you must say it explicitly.

**Set the wrong `media_type`** (e.g. `"image/jpeg"` for PNG bytes) → a 400
error from the API about invalid image data. The declared type must match
the actual bytes.

**Index `message.content[0].text` instead of looping** →
`AttributeError: 'ThinkingBlock' object has no attribute 'text'` if a
thinking block arrives first. Same lesson as Steps 8 and 9: filter by
`.type`.

**Forget `return` in `make_image_b64`** → the function returns `None`,
`image1_b64` is `None`, and the API rejects the request because `"data"`
must be a string.

---

2. Run it locally:

   ```bash
   pip install anthropic python-dotenv pillow
   python exercises/practice10_vision.py
   ```

   ✅ **What should happen:** An `answer:` line prints, mentioning **red**
   for the first image and **blue** for the second. Roughly:

   ```
   answer: first: red, second: blue
   ```

   The exact wording varies between runs; the checker only needs the words
   `red` and `blue` to appear (case-insensitively) after an `answer:` label.

3. Commit and push your file to `main`:

   ```bash
   git add exercises/practice10_vision.py
   git commit -m "Step 10: vision with multiple images"
   git push
   ```

4. Watch the **Actions** tab. The **"Step 10 — Vision Multiple Images"**
   check runs automatically. On success this issue closes and **Step 11**
   opens. If it fails, read the error in the Action's log, fix your file,
   and push again.

<details>
<summary>Having trouble?</summary>

**Setup problems**

- Double-check the file path is exactly `exercises/practice10_vision.py`.
- If `pillow` isn't installed you'll get `ModuleNotFoundError: No module
  named 'PIL'` — install it with `pip install pillow`. Yes, you install
  `pillow` but import `PIL`; that mismatch is expected.
- `ModuleNotFoundError: No module named 'dotenv'` — install
  `python-dotenv`.
- 401 / authentication error — check `.env` is in the directory you run
  `python` from and that `load_dotenv()` runs before `Anthropic(...)`.

**Errors specific to this step**

- `TypeError: make_image_b64() takes 1 positional argument but 3 were
  given` — you wrote `make_image_b64(220, 20, 20)`. It needs the double
  parentheses: `make_image_b64((220, 20, 20))`.
- `TypeError: Object of type bytes is not JSON serializable` — you dropped
  `.decode("utf-8")` after `standard_b64encode(...)`.
- `ValueError: unknown file extension` — you dropped `format="PNG"` from
  `img.save(buf, format="PNG")`.
- `AttributeError: 'ThinkingBlock' object has no attribute 'text'` — loop
  over `message.content` and check `block.type == "text"` instead of
  indexing `content[0]` directly — some models return a thinking block
  first.
- `400 ... could not process image` — the `"data"` string is empty or
  truncated. Print `len(image1_b64)` to confirm it's a few hundred
  characters.
- Make sure both `image` content blocks come **before** the `text` block in
  the `content` list, and in the order red-then-blue — the checker expects
  Claude to say "first" = red and "second" = blue.
- Claude replies about only one image — you probably nested the second
  image inside a *second message* instead of adding it to the same
  `content` list. Both image blocks belong to one user turn.
- `IndentationError: expected an indented block` — the body of
  `make_image_b64` must be indented under the `def` line.

**Checker specifics**

- The checker looks for `load_dotenv()`, `ICA_API_KEY`, and `base_url=` in
  your script — make sure all three are present.
- It counts occurrences of the exact source text `"type": "image"` and
  requires **at least two**. Keep that spacing (colon, one space) and the
  double quotes.
- It requires the label `answer:` in stdout, plus `red` and `blue`
  somewhere in the output. Don't rename the printed label.
- If the check fails complaining about `ICA_API_KEY`, make sure it's set as
  a repo secret (Settings → Secrets and variables → Actions).

</details>

<details>
<summary>Stuck? Reveal the solution</summary>

Give it a real attempt first — debugging your own code is where the learning
happens. If you're properly stuck, the complete working reference is here:

**[`solutions/practice10_vision.py`](../../solutions/practice10_vision.py)**

Copy it to `exercises/practice10_vision.py`, run it, then read it line by line and make
sure you can explain *why* each part is there.

</details>
