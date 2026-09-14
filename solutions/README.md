# 💡 Solutions — reference answers for every step

This folder contains one complete, working reference solution for each of the
22 steps in the course — including the Step 22 capstone.

**Peeking is allowed.** You are not cheating, and nobody is grading you on
willpower. This folder exists because getting permanently stuck is the single
most common reason people abandon a course — and quitting teaches you nothing.
Looking at a worked answer and understanding it teaches you plenty.

That said, the order matters:

## 🧭 How to use this folder

1. **Try it yourself first.** Write the code, run it, let it break. Debugging
   your own mistake is where almost all of the learning actually happens.
2. **Read the error message.** Out loud, if it helps. Most Python errors name
   the exact line and the exact problem.
3. **Re-read the step's lesson.** The answer is nearly always in the code block
   you skimmed past.
4. **Then, if you're still stuck — open the solution.** Genuinely stuck for
   10–15 minutes is a good threshold. Grinding for an hour is not virtue.
5. **After you look, retype it — don't paste it.** Then delete it and write it
   again from memory. Typing builds recall that copying does not.
6. **Make sure you can explain *why* each line is there.** If you can't, you
   have the answer but not the lesson. Change something and see what breaks.

## 📂 What's in here

| Step | Solution | Exercise it answers |
| --- | --- | --- |
| 1 | [`practice1.py`](practice1.py) | `exercises/practice1.py` |
| 2 | [`practice_message.py`](practice_message.py) | `exercises/practice_message.py` |
| 3 | [`practice_inspect.py`](practice_inspect.py) | `exercises/practice_inspect.py` |
| 4 | [`practice4_multiturn.py`](practice4_multiturn.py) | `exercises/practice4_multiturn.py` |
| 5 | [`practice5_image.py`](practice5_image.py) | `exercises/practice5_image.py` |
| 6 | [`practice6_streaming.py`](practice6_streaming.py) | `exercises/practice6_streaming.py` |
| 7 | [`practice7_json.py`](practice7_json.py) | `exercises/practice7_json.py` |
| 8 | [`practice8_tools.py`](practice8_tools.py) | `exercises/practice8_tools.py` |
| 9 | [`practice9_thinking.py`](practice9_thinking.py) | `exercises/practice9_thinking.py` |
| 10 | [`practice10_vision.py`](practice10_vision.py) | `exercises/practice10_vision.py` |
| 11 | [`practice11_pdf.py`](practice11_pdf.py) | `exercises/practice11_pdf.py` |
| 12 | [`practice12_caching.py`](practice12_caching.py) | `exercises/practice12_caching.py` |
| 13 | [`practice13_token_counting.py`](practice13_token_counting.py) | `exercises/practice13_token_counting.py` |
| 14 | [`practice14_batch_api.py`](practice14_batch_api.py) | `exercises/practice14_batch_api.py` |
| 15 | [`practice15_async_client.py`](practice15_async_client.py) | `exercises/practice15_async_client.py` |
| 16 | [`practice16_error_handling.py`](practice16_error_handling.py) | `exercises/practice16_error_handling.py` |
| 17 | [`practice17_models_available.py`](practice17_models_available.py) | `exercises/practice17_models_available.py` |
| 18 | [`practice18_files_api.py`](practice18_files_api.py) | `exercises/practice18_files_api.py` |
| 19 | [`practice19_code_execution.py`](practice19_code_execution.py) | `exercises/practice19_code_execution.py` |
| 20 | [`practice20_web_search.py`](practice20_web_search.py) | `exercises/practice20_web_search.py` |
| 21 | [`practice21_bedrock_vertex.py`](practice21_bedrock_vertex.py) | `exercises/practice21_bedrock_vertex.py` |
| 22 | [`practice22_capstone.py`](practice22_capstone.py) | `exercises/practice22_capstone.py` |

## ▶️ Running a solution

The graders check `exercises/`, not `solutions/` — so copy the file across
before you run it:

```bash
cp solutions/practice4_multiturn.py exercises/practice4_multiturn.py
python exercises/practice4_multiturn.py
```

You still need your API key configured in `.env` (see the main
[README](../README.md)) — these are real scripts that make real API calls.

## 🔍 A note on consistency

These files are the *same code the step lessons show you*, so there are no
surprises and nothing extra to learn here — with one deliberate exception.
**Step 22 is a capstone**, so its lesson gives you requirements and a
structure rather than the finished program. `practice22_capstone.py` is
therefore *one* valid answer, not the only one; any file that meets the
brief's contract will pass the grader. Read it as a worked example after you
have attempted your own, not as the shape yours has to match:

- `claude-sonnet-5` everywhere, to keep your costs low
- `python-dotenv` + `ICA_API_KEY` + a custom `base_url` for the client
- the safe text-extraction pattern (checking `block.type == "text"` rather than
  blindly indexing `content[0]`)

Every file in this folder compiles cleanly and satisfies its corresponding
`.github/scripts/check_stepN.py` grader.

---

**Stuck on something these files don't answer?** Open an issue in your own
course repo, or re-read the relevant step — the lessons are written to be read
twice.
