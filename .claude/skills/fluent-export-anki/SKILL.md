---
name: fluent-export-anki
description: Export all Fluent vocabulary and grammar items as an Anki-importable TSV file. Triggered when the learner types /fluent-export-anki. Runs export-anki.py, reports the output path, and gives import instructions. Read-only — does not modify any Fluent databases.
allowed-tools: Read, Bash
---

# Anki Export

## Overview

Writes a plain-text TSV file that Anki's built-in importer understands directly — no extra Python packages required. One Basic card per item: front = target-language content (script + romanisation), back = English answer + category + level. Items are tagged so you can filter in Anki by language, type, category, and mastery level.

## When to Use

Trigger only when the learner explicitly types `/fluent-export-anki`. Read-only — safe to run at any time. Does not modify Fluent databases.

## Instructions

### 1. Run the export script

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-.}}/.claude/hooks/export-anki.py"
```

To write to a custom path (if the learner specifies one):

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-.}}/.claude/hooks/export-anki.py" ~/path/to/output.txt
```

### 2. Relay the output to the learner

The script prints a one-line summary. Show it, then add import instructions:

```markdown
## ✅ Anki Export Complete

**{script output line}**

### How to import into Anki

1. Open Anki desktop
2. **File → Import**
3. Select the exported file
4. Deck and note type are pre-set in the file header — confirm in the dialog:
   - Deck: **Fluent {Language}**
   - Note type: **Basic**
5. Click **Import**

### Card format

| Field | Content |
|-------|---------|
| Front | Target-language word / prompt (script + romanisation for Tibetan) |
| Back  | English answer · category · level |

### Tags on every card

- `fluent::{language}` — filter all your Fluent cards
- `type::vocabulary` / `type::grammar_rule` / `type::error_pattern`
- `category::*` — e.g. `category::greetings`
- `mastery::0–5` — mirror of your Fluent mastery level

### Re-running

`/fluent-export-anki` is safe to run again at any time. Anki deduplicates by front field, so re-importing adds new cards without creating duplicates.
```

## Critical Rules

- **Read-only.** Never modify Fluent databases.
- **Never auto-invoke.** File is written to disk; only run on explicit `/fluent-export-anki`.
- **No extra packages needed.** Plain TSV — Anki's built-in importer handles it (Anki 2.1.54+).
- **Re-import is safe.** Anki deduplicates by front field; running again adds new cards only.
