#!/usr/bin/env python3
"""
Fluent Answer-Leak Guard

Stop hook: blocks when the assistant's last message poses an exercise but leaks
the answer key, including a bare answer line after "**Type your answer:**".

UserPromptSubmit hook: injects a one-line reminder before the assistant drafts
its next message. CLAUDE.md sits far away in a long session; this sits adjacent.

A Stop hook fires AFTER the message is displayed, so it cannot unsend a leak. It
voids the item instead — which keeps a compromised answer out of the SM-2
databases, where it would otherwise register as genuine mastery.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fluent_paths import force_utf8_io  # noqa: E402

force_utf8_io()

REMINDER = (
    "[Fluent guard] If your next message poses an exercise, it must END at the "
    "prompt line (**Type your answer:**). No answer key, no scratch note, "
    "nothing after it."
)

# The line that hands control to the learner. Every skill uses a variant:
# "**Type your answer:**", "**Type the missing word:**", "**Type a, b, or c:**",
# "**Answer in {lang}:**", "**Write your {type} below:**", "**Type your answer!** ⏱️".
# The bold span must be the whole line (trailing emoji ok) — that excludes the
# feedback template's "**Answer:** {correct_answer}", which carries content after
# the bold span and is legitimate.
TERMINATOR = re.compile(r"^[ \t]*\*\*(?:Type|Write|Answer)\b[^*\n]*\*\*[^\w\n]*$", re.M)

# Navigation prompts, not exercises: "Type a number or skill name:" (the /fluent-learn
# menu), "Type 1, 2, 3, or 4:" (setup). They have no answer to leak and legitimately
# carry a tip line underneath. Must not swallow "Type a, b, or c:" — that IS an exercise.
MENU = re.compile(r"\bType\s+(?:a\s+number|\d)", re.I)

HEADING = re.compile(r"^#{1,6} ", re.M)

# An explicit answer-key line inside the question block.
ANSWER_KEY = re.compile(
    r"^[ \t]*\**[ \t]*(?:answer|correct answer|answer key|expected|答案|正确答案)"
    r"[ \t]*\**[ \t]*[:：]",
    re.I | re.M,
)

# "**Type:** vocabulary" is a legitimate metadata header;
# "**Type:** vocabulary — \"perks\"" smuggles the tested word into it.
TYPE_HEADER_QUOTED = re.compile(r"^[ \t]*\*\*Type:\*\*[^\n]*[\"'“”‘’「」]", re.M)


def find_leak(text):
    """Return a violation description, or None if the message is clean."""
    terms = [m for m in TERMINATOR.finditer(text) if not MENU.search(m.group(0))]
    if not terms:
        return None  # not an exercise message — nothing to guard
    term = terms[-1]

    tail = text[term.end():].strip()
    if tail:
        return (
            "content appears AFTER the prompt line %r — the learner can see it: %r"
            % (term.group(0).strip(), tail[:120])
        )

    # Only the question block is in scope. Feedback on the PREVIOUS item often
    # shares the message and legitimately states the answer; the question starts
    # at the last heading above the prompt line.
    headings = [h for h in HEADING.finditer(text) if h.start() < term.start()]
    q_start = headings[-1].start() if headings else 0
    question = text[q_start:term.start()]

    hit = ANSWER_KEY.search(question)
    if hit:
        line = question[hit.start():].splitlines()[0].strip()
        return "an answer-key line sits inside the question: %r" % line[:120]

    hit = TYPE_HEADER_QUOTED.search(question)
    if hit:
        return "the **Type:** header quotes the tested item: %r" % hit.group(0).strip()[:120]

    # Structural checks cannot catch an answer paraphrased into the stem without
    # storing the expected answer as ground truth before posing the exercise.
    return None


BLOCK_REASON = (
    "ANSWER LEAK — you posed an exercise and %s\n\n"
    "That item is burned: the learner has already seen the answer, so grading it "
    "would write a false mastery signal into spaced-repetition.json.\n\n"
    "Do this now:\n"
    "1. Tell the learner briefly that the item is void (no long apology).\n"
    "2. Discard it — do NOT grade it, do NOT record it.\n"
    "3. Re-pose a DIFFERENT item.\n"
    "4. End that message exactly at the prompt line. Nothing after it — not the "
    "answer, not a scratch note, not a blank marker. Keep the answer in your "
    "reasoning only."
)


def last_assistant_text(transcript_path):
    text = ""
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if entry.get("type") != "assistant":
                    continue
                blocks = entry.get("message", {}).get("content", [])
                chunk = "".join(
                    b.get("text", "")
                    for b in blocks
                    if isinstance(b, dict) and b.get("type") == "text"
                )
                if chunk.strip():
                    text = chunk
    except OSError:
        return ""
    return text


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}

    event = payload.get("hook_event_name", "")

    if event == "UserPromptSubmit":
        print(REMINDER)
        sys.exit(0)

    if event != "Stop" or payload.get("stop_hook_active"):
        sys.exit(0)  # already re-prompted once; never loop

    transcript = payload.get("transcript_path")
    if not transcript:
        sys.exit(0)

    leak = find_leak(last_assistant_text(transcript))
    if leak:
        print(json.dumps({"decision": "block", "reason": BLOCK_REASON % leak}))

    sys.exit(0)


def selftest():
    leaked = (
        "## Word 3/10\n\n**English:** _____ growth\n\n"
        "**Type your answer:**\n\nphenomenon"
    )
    assert find_leak(leaked), "trailing answer key must be caught"

    clean = "## Word 3/10\n\n**English:** _____ growth\n\n**Type your answer:**"
    assert find_leak(clean) is None, "clean exercise must pass"

    clean_emoji = "## Question 1: Grammar\n\nRewrite this.\n\n**Type your answer!** ⏱️"
    assert find_leak(clean_emoji) is None, "emoji terminator variant must pass"

    # Feedback for the previous item + the next question in one message.
    combined = (
        "## Feedback\n\n**Answer:** phenomenon\n\n**Correct version:** \"a rare phenomenon\"\n\n"
        "Score: 8/10\n\n---\n\n## Word 4/10\n\n**Complete:** I need an _____.\n\n"
        "**Type the missing word:**"
    )
    assert find_leak(combined) is None, "feedback above the question must not false-positive"

    key_in_stem = (
        "## Review 2/8\n\n**Type:** vocabulary\n\nWhat does 'perk' mean?\n\n"
        "Answer: 福利\n\n**Type your answer:**"
    )
    assert find_leak(key_in_stem), "answer-key line inside the question must be caught"

    type_ok = "## Review 2/8\n\n**Type:** vocabulary\n\nDefine it.\n\n**Type your answer:**"
    assert find_leak(type_ok) is None, "plain Type: header must pass"

    type_leak = (
        "## Review 2/8\n\n**Type:** vocabulary — \"perks\"\n\nDefine it.\n\n"
        "**Type your answer:**"
    )
    assert find_leak(type_leak), "quoted word in Type: header must be caught"

    reading_type = (
        "## Reading\n\n**Type:** news article\n\nText here.\n\n"
        "## Vraag 1\n\na) x\nb) y\n\n**Type a, b, or c:**"
    )
    assert find_leak(reading_type) is None, "free-form reading Type: header must pass"

    not_exercise = "Great work today! Your streak is 4 days. 🔥"
    assert find_leak(not_exercise) is None, "non-exercise message must pass"

    menu = (
        "## What shall we practice?\n\n1. Vocab\n2. Writing\n\n"
        "**Type a number or skill name:** 👇\n\n> 💡 My pick: vocab — 39 items are due."
    )
    assert find_leak(menu) is None, "menu prompt with a tip below must not false-positive"

    mcq = "## Vraag 1\n\nWhat does it mean?\n\na) x\nb) y\nc) z\n\n**Type a, b, or c:**\n\nb"
    assert find_leak(mcq), "an MCQ is an exercise — trailing key must still be caught"

    print("selftest: all assertions passed")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
