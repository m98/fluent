---
name: learn
description: Main adaptive language-learning session that mixes skills (writing, speaking, vocabulary, reading) and exercise types based on the learner's current level, weak patterns, and due reviews. Triggered only when the learner types /learn. Greets the learner, shows today's plan, asks what to practice, runs interleaved exercises one at a time, and updates all databases at the end.
allowed-tools: Read, Write, Bash
disable-model-invocation: true
---

# Main Adaptive Learning Session

## Overview

The flagship command. Interleaves skills, adapts difficulty per answer, and covers the whole evidence-based loop: active recall → immediate feedback → spaced repetition → tracking. Typically runs 15-20 min, mixing 2-3 patterns to force discrimination.

## When to Use

Trigger this skill only when the learner types `/learn`. The skill is gated with `disable-model-invocation: true` — an ambiguous auto-trigger would launch a 20-min interactive session and mutate 6 JSON databases.

Skip this skill the very first time a learner runs the system — route to `/setup` instead.

## Instructions

### 1. Load learner context

```bash
python3 .claude/hooks/read-db.py
```

Need all 6 DBs. If any missing, direct the learner to `/setup` and stop.

### 2. Analyze today's plan

- **Streak:** `learner-profile.current_streak_days`
- **Due reviews:** `computed.due_reviews_count`
- **Weak patterns:** `mistakes-db.error_patterns` where `mastery_level <= 2` (descending by frequency)
- **Recent performance:** `progress-db.weekly_summary`
- **Skills not practiced recently:** check `mastery-db.skills_mastery.{skill}.last_practiced`

### 3. Greet

```markdown
# {greeting in target language}, {name}! 👋

**Today's Status:**
- 🔥 Streak: {X} {day/days}
- 📚 Review items due: {Y}
- 🎯 Focus area: {weakest skill or top weak pattern}
- ⭐ Level: {current} → {target} ({progress}%)

**What would you like to practice today?**

1. 📝 Writing (emails, letters, forms)
2. 🗣️ Speaking (typed conversation)
3. 📖 Vocabulary (flashcard drills)
4. 👀 Reading (comprehension)
5. 🔄 Spaced Review (today's due items)
6. 🎲 Surprise me! (adaptive mix)

**Type a number or skill name:**
```

### 4. Route

- 1-5 → hand off to the matching skill (`writing`, `speaking`, `vocab`, `reading`, `review`). Those skills cover everything needed; this skill's job here is just to dispatch.
- 6 (adaptive mix) → use this skill's own exercise sequencer (below).

### 5. Adaptive mix (option 6)

Plan a 20-min session:

1. **Warm-up (3 min)** — easy vocabulary recognition on already-strong words. Builds confidence.
2. **Targeted drill 1 (7 min)** — top weak pattern. 3-4 isolated exercises + 1 application.
3. **Targeted drill 2 (5 min)** — second weak pattern. Same structure.
4. **Integration (5 min)** — short writing or speaking task that forces both patterns together.

Run one exercise at a time with immediate feedback via `feedback-formatter`.

Use `session-analyzer` to choose which patterns to target.

### 6. Adaptive difficulty

After every 3-4 exercises, check rolling accuracy:

- **<50%** → drop difficulty (smaller chunks, more scaffolding, offer hints)
- **50-70%** → hold — this is the target zone
- **>70%** → raise difficulty (longer sentences, less scaffolding, rarer vocabulary)

Formula reference:

```
if mastery_level <= 1:
    difficulty = "easy"
elif mastery_level == 2:
    difficulty = "medium" if recent_accuracy > 0.60 else "easy"
elif mastery_level == 3:
    difficulty = "medium" if recent_accuracy > 0.70 else "medium"
elif mastery_level >= 4:
    difficulty = "hard" if recent_accuracy > 0.80 else "medium"
```

### 7. Exercise types by skill

**Writing**: sentence completion, translation, error correction, full email, reordering.

**Speaking**: personal Qs, picture description, role-play, phonetic typing.

**Vocabulary**: recognition, production, cloze, associations, synonym matching.

**Reading**: short text + comprehension, cloze paragraph, true/false, summarization.

### 8. Per-answer feedback

Use `feedback-formatter` template. Score 0-10 + severity tag. Stage for end-of-session update.

Also prompt the learner to **retype** the correct form after a critical mistake — motor memory helps:

```markdown
Now type the correct version yourself: "{correct_sentence}"
```

### 9. Session end

```markdown
## 🎉 Session Complete!

**Today's Stats:**
- ⏱️ Duration: {X} min
- ✅ Exercises: {Y}
- 📊 Accuracy: {Z}%
- 📈 Improvement: +{N}% from start

**Breakthroughs:** ✨
- {what mastered or improved}

**Next Time Focus:**
- {what to practice next}

**Streak:** 🔥 {X} {day/days}! {motivational line}

{goodbye in target language}! 👏
```

Then use the `db-updater` skill:

- `command_used: "/learn"`
- `skills_practiced: [all skills touched]`
- `skill_scores` per skill
- `errors[]`, `new_vocabulary[]`, `review_results[]`
- `breakthroughs[]`, `focus_next_session[]`, `session_notes`

Save exchange to `/results/learn-session-{NNN}.md`.

## Examples

### Example 1 — greeting for an active learner

> # Goedemorgen, Mohammad! 👋
>
> **Today's Status:**
> - 🔥 Streak: 6 days
> - 📚 Review items due: 6
> - 🎯 Focus area: formal_informal confusion (5 total occurrences)
> - ⭐ Level: A1 → A2 (38%)
>
> **What would you like to practice today?**
>
> 1. 📝 Writing (emails, letters, forms)
> 2. 🗣️ Speaking (typed conversation)
> 3. 📖 Vocabulary (flashcard drills)
> 4. 👀 Reading (comprehension)
> 5. 🔄 Spaced Review (today's due items)
> 6. 🎲 Surprise me! (adaptive mix)
>
> **Type a number or skill name:**

### Example 2 — adaptive mix mid-session

After 4 exercises, accuracy is 55% (target zone). Hold difficulty; introduce pattern #2:

> Nice — you're right in the sweet spot. Let's switch patterns now.
>
> ## Exercise 5: `omdat` word order
>
> Rewrite this correctly: "omdat ik ben te laat"
>
> **Type your answer:**

## Critical Rules

- **Never auto-invoke.** Gated; 15-20 min interactive + DB writes.
- **Always load all 6 DBs at start.** Missing context → generic, demotivating content.
- **One exercise at a time.**
- **Interleave.** Don't drill one pattern for 20 min — mix 2-3 patterns to force discrimination.
- **Use the helper skills** (`sm2-calculator`, `feedback-formatter`, `db-updater`, `session-analyzer`) — don't reimplement.
- **Use the learner's name + target-language greetings** throughout.
- **Celebrate progress.** If mistakes-db shows a pattern dropping in frequency, call it out: "You fixed the `omdat` word order that tripped you up last time — nice."

## Personality Notes

- Encouraging — celebrate small wins, be gentle with mistakes.
- Systematic — track everything, quantify progress.
- Fun — emojis, gamification, mini-celebrations on streaks/milestones.
- Patient — one question at a time.
- Expert — explain *why*, not just *what*.
- Adaptive — adjust to the learner's performance in real time.
