---
name: feedback-formatter
description: Canonical feedback template for every learner answer in the Fluent system — celebrate correct parts, correct mistakes with category and brief explanation, show the full correct version, score out of 10, and classify severity (🔴 critical / 🟡 moderate / 🟢 minor). Use in every practice session (writing, vocab, speaking, reading, review) immediately after the learner submits an answer.
---

# Feedback Formatter

## Overview

Every practice session ends each turn with immediate feedback. Consistency matters — the learner builds mental models from the structure, and error patterns we mine from session files depend on predictable markers (❌, ✅, severity emoji). This skill defines the single feedback shape used across all Fluent practice skills.

## When to Use

Load this skill whenever the tutor:

- Grades a learner answer in any practice skill (`learn`, `vocab`, `writing`, `speaking`, `reading`, `review`).
- Needs to classify an error by severity before writing to `mistakes-db.json`.
- Needs to tag an error by category (grammar, vocabulary, prepositions, etc.).

Skip this skill for non-feedback output (greetings, summaries, progress reports).

## Instructions

### 1. Standard template

```markdown
{✅ or ❌} {one-line encouragement or gentle correction}

**Corrections:**
- ❌ "{wrong_part}" → **"{correct_part}"** ({category} — {brief_why})
- ✅ "{correct_part}" — {specific_praise}

**Correct version:**
"{full_correct_sentence}"

**Score: {X}/10** {emoji} {short_comment}

---
```

Skip the ❌ block if the answer is fully correct. Skip the ✅ block only if truly nothing was right (rare — usually at least word order or intent was right).

### 2. Tag severity on every error

| Symbol | Severity | Meaning | Example |
|--------|----------|---------|---------|
| 🔴 | Critical | Breaks communication or exam-blocker | Formal/informal mix in formal email; wrong subordinate-clause word order |
| 🟡 | Moderate | Noticeable but understandable | Preposition error, missing article |
| 🟢 | Minor | Low priority | Spelling, punctuation, accent marks |

A single answer may contain multiple errors of different severity — tag each.

### 3. Use these category labels

These feed `mistakes-db.json`:

- `grammar` — word order, conjugation, clause structure
- `formal_informal` — u/je, uw/jouw, register mismatch
- `vocabulary` — wrong word, English mixing, register-wrong synonym
- `spelling` — minor
- `prepositions` — om/op/in/bij/naar/etc.
- `articles` — de/het, definite/indefinite
- `missing` — omitted greeting, closing, required word

### 4. Tone rules

- **Encourage before correcting.** Open with a ✅ or a warm ❌ (`"Close! Let's tune one word."`), not a bare `Wrong.`.
- **Explain why, not just what.** `"Ik schrijf je" → "Ik schrijf u" (formal_informal — business emails require u)` beats `"Use u not je."`.
- **Name the pattern.** Helps the learner generalize: `"This is the omdat word-order rule: verb goes last."`.
- **Celebrate progress.** `"You didn't miss this last time — well done."` when `mistakes-db` shows improvement.
- **Emojis on.** The learner's profile has `use_emojis: true` by default. Keep them.

### 5. Hand score to SM-2

After scoring, feed the score into the SM-2 update via the `sm2-calculator` skill: `quality = floor(score / 2)`.

## Examples

See `.claude/references/feedback-template.md` for fully-rendered examples (mostly-correct answer with a minor slip; critical error with severity tagging). The reference file is the authoritative version — keep it and this skill in sync if updating.

Quick pattern:

- Fully correct: open with ✅, skip ❌ block, list 1-2 ✅ strengths, show "Correct version" for echo, score 9-10/10.
- Mistakes: open with warm ❌, list each correction with severity emoji + category + brief why, show full correct version, score with breakdown if the answer is long.

## Critical Rules

- **Always use the template exactly.** Deviations break session-file parsing downstream.
- **Severity tag is mandatory** on every ❌ line. Drives spaced-repetition priority.
- **One score per answer.** Total out of 10, with optional breakdown (grammar/vocab/structure) for long answers like writing tasks.
- **Never skip the "Correct version".** Even if perfect, echoing the target form reinforces motor memory.

## Why This Matters

Structured, consistent feedback:
1. Lets the learner scan for what to fix at a glance.
2. Makes session files parseable so `PRACTICE.md` analysis + `/results` mining work.
3. Populates `mistakes-db.json` categories cleanly — which feeds spaced repetition, which drives the whole system.
