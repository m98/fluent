---
name: writing
description: Run an interactive writing practice session (emails, letters, forms, short texts) with systematic error analysis, category-tagged corrections, and detailed feedback. Triggered only when the learner types /writing. Selects a scenario matched to mastery, lets the learner compose, then analyzes grammar, register, vocabulary, structure, and spelling before updating all databases.
allowed-tools: Read, Write, Bash
disable-model-invocation: true
---

# Writing Practice Session

## Overview

Full-text writing practice with systematic correction. One scenario per session, detailed feedback broken down by severity and category, DB update at end. Mastery-driven scenario selection keeps the task at the right level — challenging, not frustrating.

## When to Use

Trigger this skill only when the learner types `/writing`. The skill is gated with `disable-model-invocation: true` — a 15-20 min interactive session with DB writes should never start from an ambiguous prompt.

Skip this skill in favor of `/vocab` if the learner has not yet hit mastery 2 in basic vocabulary — writing needs a minimum word bank.

## Instructions

### 1. Load context

```bash
python3 .claude/hooks/read-db.py
```

Need: `learner-profile` (level, target language, focus areas), `mistakes-db` (weak writing patterns), `mastery-db` (writing sub-skills).

### 2. Pick scenario type

From `mastery-db.skills_mastery`:

- Formal email (if `writing_formal_email` mastery < 4)
- Informal email (if `writing_informal_email` < 4)
- Form filling (if `writing_forms` < 4)
- Newsletter / personal text (if overall writing < 3)
- Mixed scenarios (if all ≥ 4)

Scenarios must match the learner's CEFR level — A2 uses everyday situations, B1+ adds opinion / complaint / inquiry.

### 3. Present the task

```markdown
## ✍️ Writing Exercise

**Scenario:** {clear description in native language}

**Task:** Write a {type} in {target_language}.

**Requirements:**
- Length: {X-Y} words
- Include: {must-include elements}
- Register: {formal / informal}
- Level: {CEFR}

{Optional: example structure for harder tasks}

**Write your {text_type} below:**
```

### 4. Wait for the full text

Don't correct mid-composition. Let the learner finish.

### 5. Systematic error analysis

Check every sentence for these categories:

1. **Grammar** — word order, conjugation, clause structure, articles
2. **Formal/informal** — register consistency
3. **Vocabulary** — wrong word, English mixing, register-wrong synonyms
4. **Missing elements** — greeting, closing, required fields
5. **Spelling** — minor at A2, weightier at B2+
6. **Structure** — organization, flow, paragraphing

Tag each finding with a severity: 🔴 critical, 🟡 moderate, 🟢 minor.

### 6. Detailed feedback

Diverges slightly from the standard `feedback-formatter` template because writing answers are multi-sentence. Use this variant:

```markdown
## Feedback

### ✅ What You Did Well
- {strength 1}
- {strength 2}

### ❌ Areas to Improve

**Critical:** 🔴
- {issue}: "{wrong}" → **"{correct}"** — {why}

**Moderate:** 🟡
- {issue}: {explanation}

**Minor:** 🟢
- {spelling / punctuation}

### 📝 Corrected Version

```
{fully corrected text}
```

**Score: {X}/10**

**Breakdown:**
- Grammar: {Y}/10
- Vocabulary: {Z}/10
- Structure: {W}/10
- Communication: {V}/10

---
```

### 7. Optional rewrite

If score < 7, offer:

```markdown
**Want to try again?** Rewriting with the corrections locks in the patterns.

Type "rewrite" to try again, or "next" to continue.
```

### 8. Session summary

```markdown
## 📊 Writing Session Summary

**Text Type:** {type}
**Score:** {X}/10
**Key Takeaways:**
- {learning 1}
- {learning 2}
- {learning 3}

**Next Time:**
- Focus on: {weak pattern}
- Review: {relevant flashcards}

{target-language "well done"}! ✍️
```

### 9. Update all databases

Use the `db-updater` skill:

- `command_used: "/writing"`, `skills_practiced: ["writing"]`
- `skill_scores.writing: {exercises: 1, correct: 1_if_score_≥_7_else_0, time_minutes}`
- `errors[]` — one per distinct pattern found (dedupe; the script bumps frequency)
- `focus_next_session[]` — top 2 patterns to drill

Also save the exchange as `/results/writing-session-{NNN}.md` with the full task, the learner's original text, the corrected version, and the error table. The `session-analyzer` skill depends on this format.

## Examples

### Example 1 — formal email task (Dutch A2)

> ## ✍️ Writing Exercise
>
> **Scenario:** You need to cancel a doctor's appointment you have on Thursday.
>
> **Task:** Write a formal email to the doctor's office in Dutch.
>
> **Requirements:**
> - Length: 40-60 words
> - Include: greeting, reason, request for new appointment, closing
> - Register: formal
> - Level: A2
>
> **Write your email below:**

Learner: "Hallo, Ik schrijf je omdat ik kan niet komen op donderdag. Ik ben ziek. Kunnen we een andere dag afspreken? Bedankt, Mohammad"

> ## Feedback
>
> ### ✅ What You Did Well
> - Clear reason for cancellation.
> - Correct request structure.
>
> ### ❌ Areas to Improve
>
> **Critical:** 🔴
> - `formal_informal`: "Hallo" + "je" — formal email needs "Beste meneer/mevrouw" + "u". Mixed registers cost exam points.
> - `grammar`: "ik kan niet komen" is OK standalone, but after "omdat" Dutch word order flips: **"omdat ik niet kan komen"**.
>
> **Moderate:** 🟡
> - `missing`: no formal closing. Use "Met vriendelijke groet,".
>
> **Minor:** 🟢
> - Capitalize "Donderdag"? Actually no — Dutch doesn't capitalize weekdays. You were right.
>
> ### 📝 Corrected Version
>
> ```
> Beste meneer/mevrouw,
>
> Ik schrijf u omdat ik niet kan komen op donderdag. Ik ben ziek.
> Kunnen we een andere dag afspreken?
>
> Met vriendelijke groet,
> Mohammad
> ```
>
> **Score: 6/10**
> - Grammar: 6/10 — omdat word order tripped you up.
> - Vocabulary: 8/10 — solid word choice.
> - Structure: 5/10 — missing proper opening + closing.
> - Communication: 7/10 — message was clear despite issues.

## Critical Rules

- **One scenario per session.** Don't chain multiple writing tasks — depth over breadth.
- **Wait for the full answer** before correcting.
- **Severity tagging is mandatory.** Fed into `mistakes-db` and drives spaced repetition priority.
- **Always save the session file** in `/results/` for later analysis by `session-analyzer`.
- **Never auto-invoke.** This skill is gated; must fire only on explicit `/writing`.

## Language Reference

### Dutch A2 patterns

**Formal emails:** always "u" (not "je"); open `Beste meneer/mevrouw {NAME},`; closing `Met vriendelijke groet,` + name.

**Informal emails:** "je" not "u"; open `Hallo {NAME},`; closing `Groetjes,` or `Tot snel,`.

**Common mistakes:** mixing formal/informal in one text; word order in `omdat` clauses (verb last); time expressions (`om 10:00 uur`, `op dinsdag`).

Add similar sections for other target languages as the learner needs them.
