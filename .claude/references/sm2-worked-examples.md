# SM-2 Worked Examples

Reference for the `fluent-sm2-calculator` skill. Each example shows input state, score, computed output. Useful for implementing SM-2 by hand when `.claude/hooks/update-db.py` is unavailable.

## Formula (quick)

```
quality = floor(score / 2)

if quality >= 3:
    repetitions += 1
    if repetitions == 1: interval = 1
    elif repetitions == 2: interval = 6
    else: interval = round(previous_interval * easiness_factor)
else:
    repetitions = 0
    interval = 1

EF_new = EF + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
EF_new = max(1.3, EF_new)
```

Mastery transitions use `consecutive_correct >= 5` → +1 level, `consecutive_incorrect >= 3` → -1 level.

## Score → Quality mapping

| Score | Quality |
|-------|---------|
| 10    | 5       |
| 8-9   | 4       |
| 6-7   | 3       |
| 4-5   | 2       |
| 2-3   | 1       |
| 0-1   | 0       |

## Example 1 — correct answer, existing item

**Item:** "het huis" vocabulary.
**Learner score:** 9/10 → quality = 4.

Before:
- `interval_days = 6`
- `repetitions = 2`
- `easiness_factor = 2.5`
- `consecutive_correct = 1`

After:
- `repetitions = 3`
- `interval_days = round(6 * 2.5) = 15`
- `EF = 2.5 + (0.1 - 1 * (0.08 + 1 * 0.02)) = 2.5 + 0 = 2.5`
- `consecutive_correct = 2` (no mastery change yet)
- `due_date = today + 15`
- Queue: `later` (interval > 7)

## Example 2 — wrong answer, existing item

**Item:** "het gebouw" (learner wrote "de gebouw").
**Score:** 3/10 → quality = 1.

Before:
- `interval_days = 6`
- `repetitions = 2`
- `easiness_factor = 2.3`
- `consecutive_correct = 1`
- `consecutive_incorrect = 0`

After:
- `repetitions = 0`
- `interval_days = 1`
- `EF = 2.3 + (0.1 - 4 * (0.08 + 4 * 0.02)) = 2.3 - 0.54 = 1.76`
- `consecutive_correct = 0`
- `consecutive_incorrect = 1`
- `due_date = today + 1`
- Queue: stays in `today` for immediate re-practice

## Example 3 — fifth consecutive correct, mastery bump

**Item:** "omdat word order" grammar rule.
**Score:** 10/10 → quality = 5.

Before:
- `interval_days = 14`
- `repetitions = 4`
- `easiness_factor = 2.8`
- `consecutive_correct = 4`
- `mastery_level = 3`

After:
- `repetitions = 5`
- `interval_days = round(14 * 2.8) = 39`
- `EF = 2.8 + (0.1 - 0 * ...) = 2.9`
- `consecutive_correct = 5` → **mastery_level = 4**, `consecutive_correct` resets to 0
- `due_date = today + 39`
- Queue: `later`

## Example 4 — third consecutive wrong, mastery drop

**Item:** `formal_informal_confusion` error pattern.
**Score:** 2/10 → quality = 1.

Before:
- `interval_days = 4`
- `repetitions = 1`
- `easiness_factor = 1.6`
- `consecutive_incorrect = 2`
- `mastery_level = 2`

After:
- `repetitions = 0`
- `interval_days = 1`
- `EF = 1.6 + (0.1 - 4 * 0.16) = 1.6 - 0.54 = 1.3` (floored)
- `consecutive_incorrect = 3` → **mastery_level = 1**, `consecutive_incorrect` resets to 0
- `due_date = today + 1`
- Queue: `tomorrow` (the review skill may select a distinct same-concept variant today)

## Queue routing rules

After computing the new `interval_days`:

- `quality < 3` or wrong answer → `review_queue.tomorrow` after `due_date = today + 1`
- `interval_days == 1` (day after wrong) → `review_queue.tomorrow`
- `2 <= interval_days <= 7` → `review_queue.this_week`
- `interval_days > 7` → `review_queue.later`

The `update-db.py` script rebuilds `review_queue` from scratch on every call. Do not hand-edit it.
