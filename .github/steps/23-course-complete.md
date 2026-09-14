## 🎉 Course complete!

You finished all **22 steps**. Not skimmed — you wrote and pushed working code
for every one of them, and a grader confirmed each one actually ran.

That's worth sitting with for a second. Twenty-two steps ago, `pip install
anthropic` was a command you hadn't run. You've now built, from scratch, a
program that holds a conversation with a large language model, hands it a tool
it can call, feeds the result back, and stays standing when the network doesn't.

### 🗺️ What you covered

**Phase 1 · Foundations** — installing the SDK, your first `messages.create()`
call, reading every field on the response (`id`, `model`, `stop_reason`,
`usage`), and multi-turn conversations built from the `role`/`content` list.

**Phase 2 · Richer input & output** — images as content blocks, streaming
token-by-token, structured JSON output, tool use, and extended thinking.

**Phase 3 · Documents & vision at scale** — multiple images in one request and
PDF support.

**Phase 4 · Production concerns** — prompt caching, counting tokens *before*
you spend them, the Batch API, the async client, and error handling with
specific exception types.

**Phase 5 · Scale & deployment** — comparing models, the Files API, the
server-side code-execution and web-search tools, and the Bedrock/Vertex client
variants.

**Capstone (Step 22)** — you assembled the conversation loop, a real tool round
trip, defensive error handling, and safe text extraction into one working
application, from a requirements brief rather than a code listing.

### 🧠 The four habits worth keeping

Everything else in this course was API surface — details you can look up. These
four are the parts that make the difference between code that demos and code
that ships:

1. **Never index blindly into `content`.** Loop over the blocks and check
   `block.type == "text"`. The moment you enable tools or thinking, the first
   block stops being text — and `content[0].text` becomes a crash in
   production.
2. **Catch specific exceptions.** `anthropic.RateLimitError` means *wait and
   retry*. `anthropic.AuthenticationError` means *your key is wrong, retrying
   will never help*. A bare `except Exception` throws that distinction away.
3. **Append every turn to the same list.** The API is stateless. The
   conversation exists only because you keep sending the whole history back —
   including the assistant's own `tool_use` block and your `tool_result`.
4. **Count tokens and cache before you scale.** A prompt that costs a fraction
   of a cent once costs real money at a hundred thousand calls.

### 🚀 Where to go from here

- **Extend your capstone.** Add a second tool. Give it a `--verbose` flag that
  prints token usage per turn. Stream the responses so it feels instant. Make
  the tool something you'd actually use — a lookup against a CSV you own, or a
  wrapper around an internal API.
- **Wrap it in something real.** The same loop drives a Slack bot, a FastAPI
  endpoint, or a scheduled report — the only thing that changes is where the
  input comes from and where the text goes.
- **Read the official docs with new eyes.** [Anthropic API
  documentation](https://docs.anthropic.com/) will read very differently now
  that you recognise the shape of everything in it.
- **Re-read your own step files.** The lessons in `.github/steps/` and the
  reference answers in `solutions/` are yours to keep — they make a decent
  cheatsheet when you're building something a month from now.

### 💬 One last thing

If a step was confusing, the step was confusing — not you. Open an issue in
this repo with what tripped you up while it's still fresh; that feedback is how
this course gets better for the next person.

Thanks for learning with us. Now go build something. ⭐
