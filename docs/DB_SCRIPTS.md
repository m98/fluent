# Database Helper Scripts

Two Python scripts under `.claude/hooks/` manage the six learner databases:

| Script | Purpose |
|--------|---------|
| `read-db.py` | Load all 6 databases (+ computed fields) in one call |
| `update-db.py` | Apply a session report to all 6 databases atomically |

Both scripts resolve the data directory internally (see `fluent_paths.data_dir()`)
and produce identical output regardless of CWD. Always invoke them with the
`${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-.}}` prefix so the script path
itself resolves whether Fluent is installed as a plugin (CWD is the data
directory) or cloned (CWD is the repo root).

## Reading

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-.}}/.claude/hooks/read-db.py"
```

Outputs a single JSON object:

```json
{
  "databases": {
    "learner_profile": { ... },
    "progress_db": { ... },
    "mistakes_db": { ... },
    "mastery_db": { ... },
    "spaced_repetition": { ... },
    "session_log": { ... }
  },
  "computed": {
    "today": "2026-04-24",
    "due_reviews_count": 3,
    "due_review_items": ["vocab_dag", ...],
    "next_session_id": "session-005",
    "streak_active": true,
    "days_since_last_session": 1
  }
}
```

Exit codes: `0` OK, `1` one or more files missing (partial result with
`_warnings`), `2` critical error.

## Writing

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-.}}/.claude/hooks/update-db.py" <<'EOF'
{
  "session_id": "session-005",
  "date": "2026-04-24",
  "duration_minutes": 20,
  "command_used": "/fluent-learn",
  "skills_practiced": ["vocabulary", "writing"],
  "skill_scores": {
    "vocabulary": { "exercises": 5, "correct": 4, "time_minutes": 10 },
    "writing":    { "exercises": 3, "correct": 3, "time_minutes": 10 }
  },
  "errors": [
    {
      "pattern_id": "verb_conjugation_3rd_person",
      "category": "grammar",
      "subcategory": "verb_conjugation",
      "your_answer": "Hij spreek",
      "correct_answer": "Hij spreekt",
      "context": "3rd person singular",
      "difficulty_score": 0.7,
      "severity": "critical",
      "notes": "optional free text"
    }
  ],
  "new_vocabulary": [
    {
      "item_id": "het_huis",
      "item_type": "vocabulary",
      "content": "het huis",
      "answer": "the house",
      "category": "essential_nouns",
      "difficulty": "A1",
      "initial_quality": 4,
      "priority": "medium"
    }
  ],
  "review_results": [
    { "item_id": "vocab_dag", "quality": 4 }
  ],
  "topics_covered": ["articles", "house_vocabulary"],
  "breakthroughs": ["First correct use of 'het' vs 'de'"],
  "focus_next_session": ["Drill de/het article gender"],
  "session_notes": "Strong session. Article gender still tricky.",
  "achievements_earned": [],
  "milestones": [
    { "milestone": "Reached 100 words learned", "date": "2026-04-24" },
    "Completed first full conversation"
  ]
}
EOF
```

### Required fields
- `session_id` (string, conventionally `session-NNN`)
- `date` (YYYY-MM-DD)

Everything else is optional; omitted fields do not update.

### Side effects
- Backs up `data/*.json` to `.backups/pre-update-<session_id>/` *before*
  writing. If that directory already exists (e.g. a retry of the same
  session_id), a numbered sibling (`pre-update-<session_id>-2`, `-3`, …) is
  created instead — an earlier backup is never overwritten.
- Writes all six databases with a two-phase commit: every file is staged to a
  `.tmp` (with `fsync`) first, then all are swapped in via `rename`. A
  serialization or encoding error therefore aborts before any real database
  is touched — the six files never end up mutually inconsistent.
- Rebuilds `spaced-repetition.review_queue` from scratch each run — any manual
  edits there will be overwritten.

### Exit codes
- `0` success
- `1` validation error (bad/missing JSON, missing required field)
- `2` I/O or logic error (full traceback on stderr; no files were modified)

## Data model notes

- `learner-profile.json` stores `confidence` per skill as an integer 0–100.
- `progress-db.json` stores `accuracy` values as floats 0.0–1.0.
- `session-log.json` sessions use `skills_practiced` (array), `score_breakdown`
  (per-skill float accuracy), `topics_covered`, `breakthroughs`,
  `focus_next_session`, `achievements_earned`. Session IDs are
  `session-NNN`.
- `spaced-repetition.json` items preserve `consecutive_correct/incorrect`,
  `mastery_level`, `total_reviews`, `priority`, `content`, `answer`,
  `category`, `difficulty` — supply these in `new_vocabulary` payloads so new
  items are fully populated.
- `milestones[]` accepts **either** a bare string **or** an object
  `{ "milestone": <required non-empty string>, "date": <optional YYYY-MM-DD,
  defaults to the session date> }`. A nested `session_id` is ignored — the
  script always stamps each milestone with the authoritative top-level
  `session_id`. An entry that is neither a string nor an object, or an object
  whose `milestone` is missing/empty/non-string, is a validation error (exit
  `1`, no files written). A present-but-unparseable `date` silently falls back
  to the session date.
