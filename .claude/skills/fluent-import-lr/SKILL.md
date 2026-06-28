---
name: fluent-import-lr
description: Import vocabulary from a Language Reactor export (zip or CSV) into the Fluent spaced-repetition database. Triggered when the learner types /fluent-import-lr or asks to import from Language Reactor. Parses the export, deduplicates against existing items, spreads due dates to avoid flooding the queue, and writes atomically with a backup.
allowed-tools: Read, Bash
---

# Language Reactor Import

## Overview

Language Reactor can export saved vocabulary and phrases as a zip file containing `items.csv`. This skill parses that export and injects new items into the Fluent spaced-repetition database for the matching language. Items already in the database are skipped — re-running is safe.

Due dates are spread at 20 items/day by default so a large import doesn't flood the review queue all at once.

## When to Use

Trigger when the learner:
- Types `/fluent-import-lr`
- Asks to import from Language Reactor
- Provides a path to a Language Reactor zip or CSV file

## Instructions

### 1. Get the file path

Ask the learner for the path if they haven't provided one:

```
Where is your Language Reactor export file? (e.g. ~/Downloads/Language Reactor Saved Items Jun 28 2026.zip)
```

### 2. Run a dry-run first

Always preview before writing:

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-.}}/.claude/hooks/import-lr.py" \
  "<file_path>" --dry-run
```

Show the learner the summary (items found, new vs. already-known, schedule range).

### 3. Confirm with the learner

```markdown
**Import preview:**

- **File:** {filename}
- **Language:** {lang_code} ({language_name})
- **New items:** {N} (spread at {daily_limit}/day through {last_date})
- **Already known:** {M} (will be skipped)

Ready to import?
```

### 4. Run the actual import

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-.}}/.claude/hooks/import-lr.py" \
  "<file_path>"
```

**Optional flags:**

| Flag | Default | Purpose |
|------|---------|---------|
| `--lang CODE` | auto-detect | Force a specific language code (e.g. `--lang de`) |
| `--daily-limit N` | 20 | Max new items due per day |
| `--data-dir PATH` | registry | Override the Fluent data directory |

Example with flags:

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-.}}/.claude/hooks/import-lr.py" \
  "<file_path>" --lang de --daily-limit 10
```

### 5. Report results

Relay the script output to the learner, then add:

```markdown
**Done!** {N} new items are now in your spaced-repetition queue.

The first items will appear in tomorrow's `/fluent-review` session.
New items will drip in at {daily_limit}/day so your queue stays manageable.

**Tips:**
- Run `/fluent-review` daily as usual — Language Reactor items appear automatically.
- You can re-run `/fluent-import-lr` at any time; items already imported are skipped.
- To see your updated item count: `/fluent-progress`
```

### 6. Language not registered error

If the script exits with "language not registered":

```markdown
**Language Reactor export contains {lang_code} items, but {lang_code} isn't set up in Fluent yet.**

To add it:
1. Register the language: `python3 ~/.claude/plugins/.../hooks/fluent-lang.py add {lang_code} "{Language Name}" ~/.claude/fluent-data-{lang_code}`
2. Run `/fluent-setup` to initialise the databases for {Language Name}.
3. Then re-run `/fluent-import-lr`.
```

## Language Reactor CSV Format (reference)

Tab-separated, no header row. Key columns:

| Col | Content |
|-----|---------|
| 0 | Item ID (`WORD\|lemma\|lang` or `PHRASE-YT\|lang\|hash`) |
| 1 | Type: `Word` or `Phrase` |
| 2 | Source sentence (target language) |
| 3 | Translated sentence (native language) |
| 5 | Lemma (dictionary/base form) |
| 6 | Part of speech |
| 8 | Translations (comma-separated) |
| 10 | Language code (`de`, `es`, etc.) |
| 16 | Video / show title |

## Critical Rules

- **Always dry-run first.** Large imports can add hundreds of items; confirm the count before writing.
- **Never auto-invoke.** Writing to the SR database is a mutating operation; only run on explicit request.
- **Re-import is safe.** Existing items are never overwritten — skipped by `item_id`.
- **Backup is automatic.** Written to `<data_dir>/.backups/pre-lr-import-<date>/` before any write.
- **Does not call update-db.py.** This is a bulk import, not a study session — only `spaced-repetition.json` is modified.
