---
name: session-analyzer
description: Parse Fluent `/results/*.md` session files to extract error patterns, strengths, accuracy trends, and focus areas for the next session. Use when the tutor needs to analyze the learner's recent performance — planning the next lesson, recommending focus areas, or answering "what should I practice next?".
---

# Session Analyzer

## Overview

Every practice session writes a markdown report to `/results/{skill}-session-{ID}.md` (e.g. `writing-session-012.md`). This skill describes how to read those files to plan adaptive follow-up practice. Use it when the tutor needs narrative context the JSON databases don't capture — the exact sentence the learner wrote, the scenario, the feedback they received.

## When to Use

Load this skill whenever the tutor:

- Plans today's focus before `/learn`, `/writing`, etc.
- Answers the learner's question "what's my weakest area" or "what should I work on".
- Generates the next session plan.

Skip this skill when aggregated JSON numbers are enough — prefer `read-db.py` for counts, trends, and mastery levels. Use this skill only when the textual context matters.

## Instructions

### 1. Find recent session files

```
/results/{skill}-session-{ID}.md
```

File naming: `{skill}-session-{NNN}.md` keeps files grouped by skill + chronological by ID. Read the most recent 3-5 files of the relevant skill; don't re-read the entire history.

### 2. Extract error patterns

Scan for `❌` markers. Each correction has:

- The wrong form ("Your answer")
- The correct form
- A category (grammar, formal_informal, vocabulary, prepositions, articles, spelling, missing)
- A severity (🔴 critical, 🟡 moderate, 🟢 minor)

Count frequency per pattern across recent files:

- **1 occurrence** — possibly a typo, ignore
- **2-3** — emerging pattern, worth drilling
- **4+** — critical weakness, highest priority

### 3. Extract strengths

Scan for `✅` markers and scores ≥ 7/10. Note consistent correct usage — these are reinforcement targets, not drill targets.

### 4. Track trajectory

Across sessions, track:

- Overall accuracy per session
- Critical vs moderate vs minor error counts
- Writing speed (words per minute, if tracked)

### 5. Plan the next session

Based on the analysis:

1. **Top 3 critical weaknesses** (highest frequency + severity) → 50% of session time.
2. **Top 2 moderate patterns** → 30% of session time.
3. **One full integration scenario** → 20% of session time.

Plan template:

```markdown
## Session {N} Plan ({X} min)

**Top 3 Weaknesses:**
1. {pattern} — {count} occurrences, severity {emoji}
2. ...

**Strengths to Reinforce:**
- {skill}

**Drill Sequence:**
1. Warm-up ({x} min) — quick wins on known patterns
2. Targeted drill 1 ({y} min) — focus on weakness #1
3. Targeted drill 2 ({y} min) — focus on weakness #2
4. Mixed integration ({z} min) — combine all patterns
5. Full scenario ({w} min) — exam-style task
```

### 6. Tune difficulty

Use recent session accuracy to tune today's difficulty:

- **<50%** → simplify, add scaffolding, smaller chunks
- **50-70%** → correct zone, keep going
- **>70%** → raise difficulty, introduce new patterns

## Examples

### Example 1 — error summary table

```markdown
## Error Pattern Summary (last 3 sessions)

| Category | Pattern | Session Count | Total Count | Severity | Example |
|----------|---------|---------------|-------------|----------|---------|
| formal_informal | Using "je" in formal context | 2 | 5 | 🔴 | "Ik schrijf je" → "Ik schrijf u" |
| grammar | Wrong "omdat" clause order | 1 | 3 | 🟡 | "omdat ik kan niet" → "omdat ik niet kan" |
| prepositions | "om" vs "op" | 2 | 4 | 🟡 | "op 10:00 uur" → "om 10:00 uur" |
```

### Example 2 — trajectory + plan

```markdown
## Trajectory (writing, last 3)

| Session | Date | Accuracy | Critical | Moderate | Minor |
|---------|------|----------|----------|----------|-------|
| 010 | 2026-04-20 | 60% | 3 | 4 | 2 |
| 011 | 2026-04-22 | 68% | 2 | 3 | 3 |
| 012 | 2026-04-23 | 74% | 1 | 2 | 3 |

Trend: accuracy rising ~7% per session. Critical errors halving each session — keep the focus on formal_informal + omdat clauses.

## Next Session Plan (20 min)

**Top weaknesses:** formal_informal (5 occurrences total), omdat word order (3).
**Strength:** vocabulary recall on household nouns.

1. Warm-up (3 min) — 5 quick household-noun recognition drills.
2. Targeted drill 1 (7 min) — 5 formal-email sentence completions forcing "u".
3. Targeted drill 2 (5 min) — 4 omdat-clause reorderings.
4. Integration (5 min) — write a 40-word formal email combining both patterns.
```

## Critical Rules

- **Read `/results/` markdown for context.** Use `read-db.py` for numerical summaries — don't reimplement counts by re-parsing markdown when the DB already has them.
- **Cap the look-back window.** 3-5 recent sessions for the relevant skill. Older data is already baked into `mistakes-db.json` mastery levels.
- **Never alter `/results/` files.** They are immutable records. Planning only.

## Why This Matters

Pattern analysis turns raw session records into an adaptive curriculum. Without it, every session looks the same regardless of progress. With it, tomorrow's drills target yesterday's weakest spots — that's the whole point of the system.
