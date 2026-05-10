---
name: progress
description: Show the learner's language learning progress, statistics, mastery levels, streak, and achievements. Use when the learner asks "how am I doing", "show my progress", "stats", "dashboard", "what's my streak", "how many words have I learned", or invokes /progress. Read-only — safe to auto-invoke.
allowed-tools: Read, Bash
---

# Progress Dashboard

## Overview

Show the learner a comprehensive, personalized progress report with visual statistics, skill mastery levels, trends, and next goals. This is read-only: do not modify any database files.

## When to Use

Trigger this skill when:

- Learner types `/progress`.
- Learner asks about their progress, statistics, streak, mastery, achievements, or how they're improving.
- Learner asks "how am I doing", "show me my stats", "am I getting better".
- After a session ends, if the learner wants a broader view than the session summary.

Skip this skill when the learner is mid-practice — the ongoing session skill already shows per-turn feedback, and opening the full dashboard interrupts the flow.

## Instructions

### 1. Load all 6 databases

Prefer the helper script over manual Read calls:

```bash
python3 .claude/hooks/read-db.py
```

This returns a single JSON with all 6 databases + computed fields (`due_reviews_count`, `next_session_id`, `streak_active`, `days_since_last_session`).

If the helper is unavailable, fall back to reading each file directly. Resolve the data directory via `fluent_paths.data_dir()` first — do NOT hardcode `data/` (plugin installs store data under `~/.codex/fluent-data/`):

- `<data_dir>/learner-profile.json`
- `<data_dir>/progress-db.json`
- `<data_dir>/mastery-db.json`
- `<data_dir>/mistakes-db.json`
- `<data_dir>/spaced-repetition.json`
- `<data_dir>/session-log.json`

If any are missing, point the learner at `/setup` and stop.

### 2. Generate the report

Use this exact structure. Fill in values from the databases; compute percentages and progress bars yourself.

```markdown
# 📊 {learner_name}'s {target_language} Learning Dashboard

**Last Updated:** {today}

---

## 🎯 Overview

**Current Level:** {current_level}
**Target Level:** {target_level}
**Progress to {next_level}:** {progress_bar} {percentage}%

**Days Studying:** {total_days}
**Current Streak:** 🔥 {streak_days} {day_or_days} {streak_message}
**Total Sessions:** {total_sessions}
**Total Study Time:** {total_minutes} minutes ({hours} hours)

---

## 💪 Skills Mastery

### Writing ✍️
**Level:** {n}/5 {stars}
**Accuracy:** {percent}%
**Progress:** {progress_bar}
**Last Practiced:** {date_or_never}

### Speaking 🗣️
**Level:** {n}/5 {stars}
**Accuracy:** {percent}%
**Progress:** {progress_bar}
**Last Practiced:** {date_or_never}

### Vocabulary 📚
**Level:** {n}/5 {stars}
**Words Known:** {count}
**Words Mastered:** {count}
**Progress:** {progress_bar}
**Last Practiced:** {date_or_never}

### Reading 👀
**Level:** {n}/5 {stars}
**Comprehension:** {percent}%
**Progress:** {progress_bar}
**Last Practiced:** {date_or_never}

---

## 📈 Progress Trends

### Accuracy Over Time
{generate ASCII chart from progress-db weekly_summary}

### This Week's Summary
- **Sessions:** {count}
- **Minutes:** {total}
- **Exercises:** {count}
- **Accuracy:** {percent}%
- **Skills Practiced:** {list}

---

## 🎯 Focus Areas

### 🔴 Critical (Needs Urgent Attention)
{patterns from mistakes-db with mastery 0-1 and high frequency}

### 🟡 Working On (Making Progress)
{patterns from mistakes-db with mastery 2-3}

### 🟢 Strong (Almost Mastered)
{patterns from mistakes-db with mastery 4-5}

---

## 🔄 Spaced Repetition Status

**Items Due Today:** {count}
**Items Due This Week:** {count}
**Items Mastered:** {count}

---

## 🏆 Achievements Unlocked

{list from learner-profile → achievements, show locked ones with 🔒}

---

## 📅 Session History

| Date | Duration | Skill | Accuracy |
|------|----------|-------|----------|
{most recent 5-10 sessions from session-log}

---

## 🎯 Next Goals

**Short-term (This Week):**
{derive from weak patterns + due reviews}

**Medium-term (This Month):**
{derive from skill mastery gaps}

**Long-term:**
{derive from target level gap}

---

## 💡 Recommendations

1. {top weak area from mistakes-db}
2. {skill not practiced recently}
3. {due review count if > 0}

---

"{personalized motivational message}"
```

### 3. Optional interpretation footer

Append this only if the learner seems new or asks what the numbers mean:

```markdown
## 📖 How to Read Your Stats

**Mastery Levels:**
- ⭐☆☆☆☆ (1/5): Just started
- ⭐⭐☆☆☆ (2/5): Learning
- ⭐⭐⭐☆☆ (3/5): Good
- ⭐⭐⭐⭐☆ (4/5): Strong
- ⭐⭐⭐⭐⭐ (5/5): Mastered

**Accuracy bands:** 0-40% intensive, 40-60% learning, 60-75% good, 75-85% strong, 85%+ excellent.
```

## Examples

### Example 1 — minimal (A1 learner, week 1)

> # 📊 Mohammad's Dutch Learning Dashboard
>
> **Current Level:** A1 → A2 (4% to A2)
> **Current Streak:** 🔥 3 days
> **Total Sessions:** 3 · 45 min
>
> ### Vocabulary 📚
> **Level:** 1/5 ⭐☆☆☆☆ · 12 words known · 0 mastered
>
> Speaking / Writing / Reading: Not yet practiced.
>
> **Items Due Today:** 6 — run `/review` first.
>
> "Three days in a row — momentum matters. Keep going!"

### Example 2 — trigger on natural-language question

Learner: "how am I doing on Dutch?" → auto-invoke this skill, render the full dashboard.

## Critical Rules

- **Read-only.** Never call `update-db.py` or edit any JSON in `data/`.
- **Use the current streak value** from `learner-profile.json`. Never guess or increment.
- **Use `day` vs `days`** correctly (1 = day, else days).
- **Skip sections with no data.** If speaking hasn't been practiced, show "Not yet practiced" — don't fabricate numbers.
- **Cite the learner by name** from `learner-profile.json`.
- **Use target-language greetings** where natural (e.g. "Goed gedaan!" for Dutch).

## Why This Skill Auto-Invokes

Unlike session commands, this is a pure read. A false-positive (Codex opens the dashboard when the learner asked something else) costs only a few tokens — no DB corruption, no interrupted practice. Worth the lower trigger bar.
