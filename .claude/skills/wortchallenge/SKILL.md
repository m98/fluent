---
name: wortchallenge
description: Run an interactive German vocabulary challenge sourced only from the configured Obsidian words folder. Triggered only when the learner types /wortchallenge. Unknown or weakly answered words are added to Fluent as normal vocabulary items so /vocab can review them later.
allowed-tools: Read, Write, Bash
disable-model-invocation: true
---

# Wörter Challenge Session

## Overview

Challenge the learner on German vocabulary notes from the Obsidian `words/` folder. This is not a spaced-repetition review session by itself. It is a discovery gate: words scored below 7/10 are saved as Fluent vocabulary items so `/vocab` can ask them later.

## When to Use

Trigger only when the learner types `/wortchallenge`.

## Instructions

### 1. Load learner and words context

Run from the Fluent repo root:

```bash
python3 .claude/hooks/read-db.py
python3 .claude/hooks/wortchallenge_words.py
```

If `wortchallenge_words.py` fails because no source is configured, ask the learner to create `data/wortchallenge-source.json`:

```json
{
  "words_dir": "/Users/necatifurkancolak/Desktop/wörter/words",
  "daily_limit": 20
}
```

The helper returns parsed notes from `words_dir`. It excludes `Hub` and `Big-Hub` notes and includes normal `Noun`, `Verb`, `Adjective`, `Phrase`, and `Expression` notes.

### 2. Select words

Use up to `daily_limit` words from the helper output. Default to 20 if no limit is configured.

Each word object has:

- `item_id`
- `content`
- `answer`
- `note_type`
- `turkish`
- `english`
- `common_patterns`
- `example_sentences`
- `first_example`
- `source.note_path`
- `source.obsidian_link`

### 3. Present one word at a time

Rotate prompt modes:

**Production** (Turkish to German):

```markdown
## Wortchallenge {N}/{total}

**Türkçe:** {main Turkish meaning}

**Almanca nasıl söylenir?**

Type your answer:
```

**Recognition** (German to Turkish):

```markdown
## Wortchallenge {N}/{total}

**Deutsch:** {content}

**Türkçe anlamı nedir?**

Type your answer:
```

**Cloze** (example sentence):

```markdown
## Wortchallenge {N}/{total}

**Complete the sentence:**

{first_example with the target word replaced by _____}

Type the missing word:
```

If no example sentence exists, use production mode.

### 4. Feedback after each answer

Use `feedback-formatter`. Score out of 10 and tag severity.

Stage answer data in memory:

- Scores `7-10`: mark as known for the summary only.
- Scores `<7`: mark as unknown and stage for `new_vocabulary[]` and `errors[]`.

Do not call `update-db.py` after each answer.

### 5. Session end and DB update

At the end, call `db-updater` with one payload:

- `command_used: "/wortchallenge"`
- `skills_practiced: ["vocabulary"]`
- `skill_scores.vocabulary`: `{exercises, correct, time_minutes}` where correct means score `>=7`
- `new_vocabulary[]`: only unknown words scored `<7`
- `errors[]`: one matching vocabulary error for each unknown word
- no `review_results[]`

For each unknown word, send a complete `new_vocabulary` item:

```json
{
  "item_id": "{item_id}",
  "item_type": "vocabulary",
  "content": "{content}",
  "answer": "{answer}",
  "category": "{category}",
  "difficulty": "{learner current level or empty}",
  "due_date": "{today}",
  "initial_quality": 2,
  "priority": "high",
  "source": {
    "type": "wortchallenge",
    "note_path": "{source.note_path}",
    "obsidian_link": "{source.obsidian_link}"
  }
}
```

Create a result file:

```text
results/wortchallenge-session-{NNN}.md
```

Include the Q&A table, scores, unknown words added to `/vocab`, known words, and note source paths.

## Critical Rules

- Source words only from the configured `words/` folder.
- Never import all words automatically.
- Only words scored `<7/10` become Fluent vocabulary items.
- Do not mutate Obsidian notes.
- One question at a time.
- Batch DB updates at session end.
