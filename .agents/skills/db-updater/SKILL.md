---
name: db-updater
description: Atomically update all 6 Fluent learner databases (learner-profile, progress, mistakes, mastery, spaced-repetition, session-log) at session end by calling .claude/hooks/update-db.py with a single JSON payload. Use at the end of every practice session — writing, vocab, speaking, reading, review, learn — to persist the session's errors, review results, new vocabulary, and session metadata.
---

# DB Updater

## Overview

Every practice skill ends with a DB update. Instead of hand-editing 6 JSON files (error-prone, racy, easy to desync), pipe one JSON report to `update-db.py`. The script runs pre-write backups, validates the payload, applies all changes atomically via `.tmp + fsync + rename`, and rebuilds the spaced-repetition queue.

## When to Use

Load this skill whenever the tutor:

- Finishes a practice session and needs to persist results.
- Needs to add new vocabulary to the spaced-repetition queue.
- Needs to record new errors, review results, or mastery changes.
- Needs to bump `total_sessions`, `current_streak_days`, or `total_study_minutes`.

Skip this skill for read-only operations (use the `progress` skill or `read-db.py` directly) and during session setup (use `setup` skill instead — `update-db.py` is for session deltas, not bootstrap).

## Instructions

### 1. Call the script

Run from the repo root:

```bash
python3 .claude/hooks/update-db.py <<'EOF'
{ ...payload... }
EOF
```

Exit codes: `0` success, `1` validation error, `2` I/O error.

### 2. Fill the payload

**Required fields**

- `session_id` — string, convention `session-NNN`. Use `computed.next_session_id` from `read-db.py`.
- `date` — YYYY-MM-DD.

**Optional fields** — omit to skip. Full canonical example (copy-paste this and fill in):

```
${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-.}}/.claude/references/db-updater-payload.example.json
```

Key blocks the example covers: `skill_scores`, `errors[]`, `new_vocabulary[]`, `review_results[]`, `topics_covered`, `breakthroughs`, `focus_next_session`, `session_notes`, `achievements_earned`, `milestones`.

### 3. Field notes

- `errors[]` — one entry per distinct mistake this session. Collapse duplicates (same `pattern_id`) before sending; `frequency` is bumped by the script.
- `new_vocabulary[]` — items the learner met for the first time. Fill every field; incomplete entries yield incomplete spaced-repetition records.
- `review_results[]` — items already in the queue that were reviewed. The script runs SM-2 on each. See the `sm2-calculator` skill. Mapping: `quality = floor(score / 2)`.
- `skill_scores[].correct` counts correct exercises, not a percentage. Accuracy is derived.
- `confidence` in `learner-profile.skills` is 0–100 integer; `accuracy` in `progress-db` is 0.0–1.0 float. The script handles the conversion.

### 4. Read before writing

Always call `read-db.py` at session start to get current state + `next_session_id`. Don't read each JSON file separately:

```bash
python3 .claude/hooks/read-db.py
```

Returns all 6 databases plus computed fields (`due_reviews_count`, `next_session_id`, `streak_active`, `days_since_last_session`).

## Examples

### Example 1 — /review session with 5 items

```bash
python3 .claude/hooks/update-db.py <<'EOF'
{
  "session_id": "session-012",
  "date": "2026-04-24",
  "duration_minutes": 12,
  "command_used": "/review",
  "skills_practiced": ["vocabulary", "grammar"],
  "skill_scores": {
    "vocabulary": { "exercises": 3, "correct": 3, "time_minutes": 7 },
    "grammar":    { "exercises": 2, "correct": 1, "time_minutes": 5 }
  },
  "review_results": [
    { "item_id": "vocab_huis", "quality": 5 },
    { "item_id": "vocab_deur", "quality": 4 },
    { "item_id": "vocab_raam", "quality": 5 },
    { "item_id": "grammar_omdat_word_order", "quality": 2 },
    { "item_id": "grammar_past_tense", "quality": 4 }
  ],
  "errors": [
    {
      "pattern_id": "grammar_omdat_word_order",
      "category": "grammar",
      "your_answer": "omdat ik ben moe",
      "correct_answer": "omdat ik moe ben",
      "context": "subordinate clause word order",
      "severity": "critical"
    }
  ],
  "focus_next_session": ["Drill 'omdat' word order"]
}
EOF
```

### Example 2 — /vocab session with a new word

```bash
python3 .claude/hooks/update-db.py <<'EOF'
{
  "session_id": "session-013",
  "date": "2026-04-25",
  "command_used": "/vocab",
  "skills_practiced": ["vocabulary"],
  "new_vocabulary": [
    {
      "item_id": "vocab_keuken",
      "item_type": "vocabulary",
      "content": "de keuken",
      "answer": "the kitchen",
      "category": "household_rooms",
      "difficulty": "A1",
      "initial_quality": 4,
      "priority": "medium"
    }
  ]
}
EOF
```

## Critical Rules

- **Call once per session, at the end.** The script rebuilds the review queue each run — partial updates risk inconsistency.
- **Never hand-edit `spaced-repetition.review_queue`.** It's regenerated from scratch on every run.
- **Same `session_id` replaces.** Sending the same ID twice overwrites the first call. Useful for corrections, dangerous if unintentional.
- **Backups are automatic.** Written to `.backups/pre-update-<session_id>/` before any change. Check there to roll back.
- **Exit code 1 means validation failed, no files touched.** Fix the payload and retry.
- **Exit code 2 means I/O failure, no files touched.** Check disk space, permissions, then retry.

## Why This Matters

Six interdependent JSON files must agree: a new `session-log` entry, a bumped `total_sessions`, updated SM-2 params, new mistake patterns, recalculated accuracy, refreshed streak. Hand-editing causes silent desync — streak says 7 days but session-log has 6 entries, mastery says 4 stars but accuracy says 45%. The script is the single source of truth.
