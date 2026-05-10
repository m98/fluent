---
name: sm2-calculator
description: SM-2 spaced-repetition algorithm reference for the Fluent language learning system. Use whenever the tutor schedules the next review of a vocabulary item, grammar rule, or error pattern — i.e. after every answered review question. Defines the 0-5 quality scale, interval formula, easiness-factor update, and mastery-level transitions that keep the spaced-repetition database correct.
---

# SM-2 Calculator

## Overview

Fluent uses SM-2 (SuperMemo 2) to decide when the learner next sees an item. This skill is the single source of truth for the algorithm. Every practice skill updates `<data_dir>/spaced-repetition.json` (where `<data_dir>` is resolved by `fluent_paths.data_dir()`) through these rules after each answered question.

## When to Use

Load this skill whenever the tutor:

- Grades a review-queue item and must compute its next due date.
- Maps a 0-10 score to an SM-2 quality.
- Updates `easiness_factor`, `interval_days`, `repetitions`, or `mastery_level` on a spaced-repetition item.
- Decides which queue (`today` / `tomorrow` / `this_week` / `later`) to place an item in.

Skip this skill when the `db-updater` skill is already being used — the `update-db.py` script runs SM-2 internally.

## Instructions

### 1. Convert score to quality

| Score | Quality | Meaning |
|-------|---------|---------|
| 10/10 | 5 | Perfect, instant recall |
| 8-9   | 4 | Correct after hesitation |
| 6-7   | 3 | Correct with difficulty |
| 4-5   | 2 | Incorrect but remembered when shown |
| 2-3   | 1 | Incorrect, familiar |
| 0-1   | 0 | Complete blackout |

Rule: `quality = floor(score / 2)`.

### 2. Update interval

```
if quality >= 3:   # correct
    if repetitions == 0:
        interval = 1
    elif repetitions == 1:
        interval = 6
    else:
        interval = round(previous_interval * easiness_factor)
    repetitions += 1
else:              # incorrect
    interval = 1
    repetitions = 0
```

### 3. Update easiness factor

Apply after every answer:

```
EF_new = EF + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
EF_new = max(1.3, EF_new)
```

### 4. Update mastery level

Track `consecutive_correct` and `consecutive_incorrect` per item:

```
if consecutive_correct >= 5:
    mastery_level = min(5, mastery_level + 1)
    consecutive_correct = 0
elif consecutive_incorrect >= 3:
    mastery_level = max(0, mastery_level - 1)
    consecutive_incorrect = 0
```

### 5. Update per-item fields

After each answer, the item in `spaced-repetition.json` must have:

- `easiness_factor` — updated via formula
- `interval_days` — new interval
- `repetitions` — incremented or reset
- `consecutive_correct` / `consecutive_incorrect` — one incremented, the other reset
- `total_reviews` — incremented
- `mastery_level` — possibly changed
- `due_date` — `today + interval_days` (YYYY-MM-DD)
- `last_reviewed` — today

### 6. Route to correct queue

After updating:

- `interval_days == 1` → `review_queue.tomorrow`
- `interval_days <= 7` → `review_queue.this_week`
- `interval_days > 7` → `review_queue.later`

If the learner got it wrong (quality < 3), keep the item in `review_queue.today` so it reappears in the same session.

### 7. Preferred implementation

Do not hand-edit `spaced-repetition.json`. Call `.claude/hooks/update-db.py` with a `review_results` array — the script runs SM-2 atomically and rebuilds the queue. Only do manual math when the script is unavailable. See the `db-updater` skill for the payload schema.

```bash
python3 .claude/hooks/update-db.py <<'EOF'
{
  "session_id": "session-NNN",
  "date": "YYYY-MM-DD",
  "review_results": [
    { "item_id": "vocab_huis", "quality": 4 }
  ]
}
EOF
```

## Examples

See `.claude/references/sm2-worked-examples.md` for 4 worked examples covering: correct answer (regular case), wrong answer (reset + EF drop), 5th consecutive correct (mastery bump), 3rd consecutive wrong (mastery drop). Each example shows the full before/after state.

Quick version:

- Correct, q=4: `interval = round(prev * EF)`, `repetitions += 1`, EF barely moves.
- Wrong, q<3: `interval = 1`, `repetitions = 0`, EF drops sharply, item stays in today's queue.

## Critical Rules

- **Floor EF at 1.3.** Never let the easiness factor drop lower — rounds to infinite daily reviews.
- **Reset repetitions on wrong answer.** The item returns to the start of the learning sequence.
- **Do not hand-tune intervals.** Trust the algorithm. Shortcuts break long-term retention.
- **Prefer `update-db.py`.** Only reimplement this math when the script is unavailable.

## Why This Matters

SM-2 reviews items just before the learner forgets them, maximizing long-term retention per minute of practice. Wrong scheduling means wasted reviews (too early) or forgotten items (too late). The whole Fluent system rests on these numbers being correct.
