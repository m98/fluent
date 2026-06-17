---
name: fluent-lang
description: Switch the active study language mid-session by writing a language code to ~/.claude/fluent-active-lang. Invoke when the learner types /fluent-lang, /fluent-lang <code> (e.g. /fluent-lang fr, /fluent-lang es), or says anything like "switch to French", "quiero estudiar español", "change language", "study French now", "cambiar idioma". Shows current language if no code given. Takes effect immediately — no restart required. Never auto-invoke from general conversation.
allowed-tools: Read, Write, Bash
disable-model-invocation: true
---

# Language Switcher

## Overview

Fluent keeps all learner data in a language-specific directory (e.g. `~/.claude/fluent-data/es/` for Spanish, `~/.claude/fluent-data/fr/` for French). The active language is stored in a single line in `~/.claude/fluent-active-lang`. This skill writes that file, which takes effect immediately — every subsequent `read-db.py` call, exercise, and database update in this session will use the new language's data.

## When to Use

Trigger only when the learner explicitly switches languages — `/fluent-lang fr`, "switch to French", "quiero estudiar español now", or similar. Do not auto-invoke from general practice prompts.

## Instructions

### 1. Determine the requested language

The learner either typed `/fluent-lang <code>` or said something like "switch to French".

Map natural language to a code:

| Phrase | Code |
|--------|------|
| Spanish / español | `es` |
| French / français / francés | `fr` |
| German / deutsch / alemán | `de` |
| Portuguese / português | `pt` |
| Italian / italiano | `it` |
| Japanese / 日本語 / japonés | `ja` |
| Chinese / 中文 / chino | `zh` |
| Korean / 한국어 / coreano | `ko` |
| Dutch / nederlands / holandés | `nl` |
| Arabic / عربي / árabe | `ar` |

If no language was given (bare `/fluent-lang`), jump to **Show current language** below.

If the learner named a language not in this list, use the standard two-letter ISO 639-1 code (lowercase). Unknown codes are fine — the user can run `/fluent-setup` to create a profile for any language.

### 2. Write the config file

Write **only the language code** (lowercase, single line) to `~/.claude/fluent-active-lang` using the Write tool:

```
~/.claude/fluent-active-lang
---
<code>
```

For example, switching to French writes exactly:
```
fr
```

Nothing else — no quotes, no newlines, no JSON.

### 3. Verify and load the new context

Run `read-db.py` to confirm the switch worked and load the new language's profile:

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-.}}/.claude/hooks/read-db.py"
```

Check `computed.results_dir` in the output — it should now point to the new language's subdirectory (e.g. `.../results/fr/`).

### 4. Respond based on profile state

**Profile found** (`databases.learner_profile` is populated):

Welcome the learner back with a brief status snapshot:

```
🇫🇷 Switched to French!

Welcome back, {name}. Here's where you left off:
- Level: {current_level} → {target_level}
- Streak: {current_streak_days} days 🔥
- Due reviews: {due_reviews_count} items

{if due_reviews_count > 0: "Start with /fluent-review to clear your queue."}
{else: "Ready to practice? Try /fluent-learn or /fluent-vocab."}
```

Use the flag emoji matching the language (see table in step 1).

**No profile found** (`databases.learner_profile` is empty or missing):

```
🇫🇷 Switched to French!

No French profile found yet. Run /fluent-setup to create your French learner profile — it only takes a minute.
```

---

### Show current language (no argument given)

Read `~/.claude/fluent-active-lang` to get the current code.

If the file does not exist or is empty, fall back to the `target_language` field from `read-db.py`'s learner profile output.

Reply with something like:

```
Currently studying: Spanish 🇪🇸 (es)

To switch, type /fluent-lang <code> — e.g. /fluent-lang fr for French.
```

## Critical Rules

- Write **only** the language code to `~/.claude/fluent-active-lang` — no other files touched.
- The session-start greeting at the top of the session still shows the old language; that is expected. The switch affects all operations from this point forward.
- Never reset or modify any learner database files — this skill only writes the config file.
