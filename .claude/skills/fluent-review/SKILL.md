---
name: fluent-review
description: Run today's spaced-repetition review queue — items scheduled by SM-2 that need reinforcement before the learner forgets them. Triggered only when the learner types /fluent-review. Pulls due items from spaced-repetition.review_queue.today, generates a targeted exercise for each, evaluates the response, updates SM-2 parameters, and reshelves items into the correct future queue.
allowed-tools: Read, Write, Bash
disable-model-invocation: true
---

# Spaced-Repetition Review Session

## Overview

Replay items the learner learned before, timed so they hit just before the forgetting curve drops them. This is the single most effective session type — the system depends on it running daily. Items the learner gets right get pushed further into the future; items they miss come back tomorrow.

## When to Use

Trigger this skill only when the learner types `/fluent-review`. The skill is gated with `disable-model-invocation: true` — mutating SM-2 state from a misread prompt would cascade through every future session.

Skip this skill when the queue is empty — suggest `/fluent-vocab` or `/fluent-learn` instead.

## Instructions

### 1. Load and select a diverse review queue

```bash
snapshot=$(mktemp "${TMPDIR:-/tmp}/fluent-review.XXXXXX")
trap 'rm -f "$snapshot"' EXIT
if ! python3 "${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-.}}/.claude/hooks/read-db.py" > "$snapshot"; then
  printf '%s\n' '[Fluent] Unable to load all learner databases; run /fluent-setup.' >&2
  exit 1
fi
python3 "${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-.}}/.claude/hooks/review_selector.py" < "$snapshot"
```

Read `spaced-repetition.review_queue.today`, `spaced-repetition.items`, and
`daily_limits.review_items_per_day`. The selector uses
`computed.due_review_items` when available so items whose due dates rolled over
since the last queue rebuild are not lost; it falls back to `queue.today` for
legacy snapshots. Use the selector output as the session plan instead of
simply taking the first N IDs. Its `selected_items` and `selected_patterns`
fields provide the item and grading context for the questions.

The selector is read-only and deterministic:

1. Remove duplicate IDs and ignore IDs missing from `items`.
2. Sort by `priority` (`critical → high → medium → low`), then overdue days,
   due date, mastery, last review, and item ID as stable tie-breakers.
3. Group by `concept_id`. For legacy items without a concept ID, use the
   compatibility map in `.claude/references/review-concepts.json`; if no map
   exists, use `legacy:<item_id>` and do not guess a merge from text.
4. First pass: select at most one item per concept, round-robin across
   concepts, until the daily limit is reached.
5. If the number of concepts is smaller than the limit, make a second pass and
   select at most one additional item per concept. Do not force a third item
   merely to reach 20.

The selector reserves up to two slots for adaptive variants when the due
pool is larger than the daily limit. Therefore `selected_count` may initially
be `limit - 2`; show the learner the primary count, the reserved slots, and the
number of distinct concepts covered. If no difficult answer needs a variant,
use the reserved slots at the end for the next unasked candidates, preferring
new concepts. Never exceed the limit.

The selector's `omitted_due_item_ids` are deferred, not completed: do not
submit them in `review_results[]`, and do not remove them from the queue. When
there are reserved slots, use `reserved_fill_item_ids` to fill unused capacity
with unasked items (prefer a new concept); a difficult answer may instead
replace one reserved fill with an unasked item from that primary item's
`variant_candidates` list (or the equivalent result of `choose_variant`).

If the queue is empty:

```markdown
🎉 No reviews due today! Your spaced repetition is up to date.

Want to practice something new? Try:
- `/fluent-learn` — adaptive mixed practice
- `/fluent-vocab` — learn new words
- `/fluent-progress` — see your stats
```

### 2. Opening

```markdown
# 🔄 Today's Spaced Repetition Review

Hallo {name}! Time to review items your brain is about to forget. This keeps everything fresh. 🧠

**Items Due Today:** {count}
**Primary Items:** {selected_count} across {unique_concepts} concepts
**Reserved Variant Slots:** {variant_slots}
**Estimated Time:** ~{minutes} min

Why review? Spaced repetition prevents forgetting, moves items into long-term memory, and builds automaticity.

**Ready? Let's start!** 💪
```

### 3. Generate exercise per item

Each item has:

```json
{
  "id": "...",
  "type": "error_pattern | vocabulary | grammar_rule",
  "concept_id": "optional stable concept slug",
  "easiness_factor": 2.5,
  "interval_days": 6,
  "repetitions": 2,
  "due_date": "YYYY-MM-DD",
  "priority": "critical | high | medium | low",
  "content": "...",
  "answer": "..."
}
```

`concept_id` is for selection only; it is not an answer key. Do not mark a
reasonable answer wrong merely because it differs from another item in the
same concept family.

Generate an exercise matched to `type` (fall back to legacy `item_type`):

- **error_pattern**: load the pattern from `mistakes-db`, create a scenario that forces the correct form. E.g. `formal_informal_confusion` → ask the learner to complete a formal email opening.
- **vocabulary**: recognition (target → native), production (native → target), or cloze — rotate modes.
- **grammar_rule**: a fill-in or error-correction exercise that tests the rule.

Present one at a time:

```markdown
## Review {N}/{total} — {priority emoji}

**Type:** {type or legacy item_type}
**Last reviewed:** {X} days ago
**Current mastery:** {stars}

{exercise}

**Type your answer:**
```

### 4. Evaluate, add limited variants, and update SM-2

Use the `fluent-feedback-formatter` skill for per-answer feedback.

The selector output is the primary plan. Track `seen_item_ids` and
`seen_concept_ids` for the whole session. Grade each answer against that
item's own content, target, context, and accepted meanings; concept membership
is for scheduling only and must never replace item-specific grading.

If a learner answers with quality `< 3`, you may add at most one unasked
variant from the same concept family. The variant must have a different
`item_id`, and each concept may receive at most one variant in a session. A
variant consumes an available daily slot and must not push the total above
`daily_limits.review_items_per_day`. If no same-concept variant exists, do not
invent a second review of the same item. Deferred items remain due for a later
session.

Stage each answered item for the end-of-session update. Do NOT hand-edit
`spaced-repetition.json` — use `review_results[]` in the `fluent-db-updater`
payload:

```json
{ "item_id": "vocab_huis", "quality": 4 }
```

The `update-db.py` script runs the SM-2 math (see `fluent-sm2-calculator` skill) and rebuilds the queue. Mapping: `quality = floor(score / 2)`.

### 5. Progress pulse every 5 items

```markdown
## Progress Update

**Reviewed:** {N}/{total}
**Accuracy:** {percent}%
**Time Remaining:** ~{min} min

Keep going! 💪
```

### 6. Session summary

```markdown
## 🎉 Review Session Complete!

**Reviewed:** {count}
**Accuracy:** {percent}%
**Time:** {min} min

### Breakdown

**Mastered (no mistakes):** {count} — won't appear again for a while 🎉
**Good (minor slips):** {count} — next in {X} days
**Need more practice:** {count} — tomorrow again

### Next Review Schedule
- Tomorrow: {count}
- This week: {count}
- Next week: {count}

**Streak:** 🔥 {X} {day/days} 🔥

**Tip:** {one line of advice based on accuracy}

{target-language well done}! 🌟
```

### 7. Update all databases

Use the `fluent-db-updater` skill:

- `command_used: "/fluent-review"`, `skills_practiced: [derived from reviewed items]`
- `skill_scores` — aggregate per skill touched
- `review_results[]` — every item actually answered, with `quality`; never
  submit a deferred item and never submit the same `item_id` twice
- `errors[]` — only patterns where the learner got it wrong (bumps frequency)
- `focus_next_session[]` — the 2-3 items with lowest quality this session

Save exchange to `/results/fluent-review-session-{NNN}.md` for later analysis.

## Examples

### Example 1 — vocabulary review with wrong answer

> ## Review 3/12 — 🔴
>
> **Type:** vocabulary
> **Last reviewed:** 6 days ago
> **Current mastery:** ⭐⭐⭐☆☆
>
> **Dutch:** het raam
>
> **What does it mean in English?**

Learner: "the door"

> ❌ Close — those are both openings in a wall, but not the same.
>
> **Corrections:**
> - 🟡 "the door" → **"the window"** (vocabulary — `het raam` is window; `de deur` is door)
>
> **Correct version:**
> "het raam" = the window.
>
> **Score: 3/10** 💪 Easy to mix — we'll review this again soon.
>
> (Logged: `review_results[]` item quality=1 → `interval_days=1, repetitions=0`; the updater schedules it for tomorrow, while the review skill may use a distinct same-concept variant in the current session.)

### Example 2 — correct answer with mastery bump

> ## Review 7/12 — 🟡
>
> **Type:** grammar_rule
> **Last reviewed:** 14 days ago
> **Current mastery:** ⭐⭐⭐⭐☆
>
> **Complete:** "Ik schrijf u omdat ik ____ kan komen." (reason: can't come)

Learner: "niet"

> ✅ Perfect — omdat-clause word order locked in.
>
> **Answer:** "Ik schrijf u omdat ik niet kan komen."
>
> **Score: 10/10** 🎯
>
> (Logged: quality=5 → `interval_days = round(14 * EF)`, queue: `later`. `consecutive_correct` = 5, mastery → 5 ⭐⭐⭐⭐⭐.)

## Critical Rules

- **Daily.** The whole system assumes the learner runs `/fluent-review` every day. Missing a day breaks the intended spacing.
- **Never auto-invoke.** Gated; must fire only on explicit `/fluent-review`. Long interactive + SM-2 mutation.
- **One item at a time.** Rushing = false positives.
- **Let the learner struggle.** If they don't remember, that's useful data (quality 0-2). The algorithm needs honest signals.
- **Never hand-edit `spaced-repetition.json`.** Queue is rebuilt on every `update-db.py` call.

## What the Schedule Means

Tell the learner if they ask:

- 1 day — new or struggling items
- 2-3 days — learning, building strength
- 1 week — getting comfortable
- 2+ weeks — strong, maintenance only
- 1+ month — mastered, long-term memory
