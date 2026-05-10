---
name: speaking
description: Run an interactive typed conversation session simulating spoken practice — free-flowing dialogue, role-plays, and opinion questions prioritizing communication over perfect grammar. Triggered only when the learner types /speaking. Asks questions one at a time in the target language, evaluates clarity and naturalness first and grammar second, and updates all databases at the end.
allowed-tools: Read, Write, Bash
disable-model-invocation: true
---

# Speaking Practice (Typed)

## Overview

Conversational practice through typed dialogue. Unlike `/writing`, prioritize **communication and naturalness** — grammar errors that don't block meaning are downplayed. Goal: build the learner's confidence to produce target-language output without over-analyzing.

## When to Use

Trigger this skill only when the learner types `/speaking`. The skill is gated with `disable-model-invocation: true` — 15-20 min interactive session with DB writes should never start from an ambiguous prompt.

Skip this skill below A1 mastery 2 — the learner needs a basic word bank and verb conjugations first (run `/vocab` a few times).

## Instructions

### 1. Load context

```bash
python3 .claude/hooks/read-db.py
```

Need: `learner-profile` (level, target language), `mastery-db.skills_mastery.speaking`.

### 2. Opening

```markdown
# 🗣️ {target_language} Speaking Practice

Hallo {name}!

Today we're practicing **speaking** through typed conversation. I'll ask you questions or give scenarios, you respond naturally in {target_language} — just like a real conversation.

**Focus:** natural expression, fluency, pronunciation (typed)
**Level:** {CEFR}
**Duration:** 15-20 min

**Tips:**
- Think in {target_language}, not {native_language}
- Don't chase perfect grammar — focus on getting your message across
- Use complete sentences
- Be natural and conversational

**Ready? Let's chat!** 💬
```

### 3. Pick topic based on mastery

A2 topics:
1. Personal introductions
2. Daily routine
3. Hobbies and interests
4. Shopping
5. Making appointments
6. Asking for directions
7. Ordering food
8. Talking about weather
9. Weekend plans
10. Work / study

B1+: opinions, comparisons, hypotheticals, complaints, narratives.

### 4. One question at a time

```markdown
## Question {N}: {Topic}

{Question in target language}

**Type your answer in {target_language}:**
```

Build the conversation naturally — after 3-4 Qs on one topic, transition: `Interessant! Let's talk about something else...`.

### 5. Evaluate

Check in this order:

1. **Communication** (most important, 0-5 points): was the message clear? Did it answer the question?
2. **Grammar** (0-3 points): verb conjugation, word order, articles. Note but don't belabor.
3. **Vocabulary** (0-2 points): appropriate word choice, no English mixing.

Feedback template (variant of `feedback-formatter`):

```markdown
{✅ or 🟡} {one-line encouragement}

**What you said:**
"{their_answer}"

**Communication:** {Clear / Mostly clear / Unclear} ✅

**Grammar notes:** (secondary — don't over-focus)
- {major error → correction, only if communication-blocking}

**Natural alternative:**
You could also say: "{more_natural_phrasing}"

**Score: {X}/10**
- Communication: {Y}/5
- Grammar: {Z}/3
- Vocabulary: {W}/2

{encouragement}

---
```

### 6. Role-play (advanced)

For B1+ or when the learner is warmed up:

```markdown
## 🎭 Role-Play

**Scenario:** {description in native language}
**Your role:** {what the learner plays}
**I'll be:** {what Codex plays}

Ready? I'll start...

---

{first line in target language}

**Your turn:**
```

### 7. Session summary

```markdown
## 🎉 Speaking Session Complete!

**Duration:** {X} min
**Questions Answered:** {N}
**Topics Covered:** {list}

### Communication Scores
**Overall:** {percent}%
- Clear messages: {count}
- Natural expression: {rating}/5
- Confidence: Growing! 💪

### Vocabulary Used Well
- {words}

### For Next Time
- Try using: {new phrase}
- Practice: {weak area}

**{target-language well done}!** 🌟
```

### 8. Update all databases

Use the `db-updater` skill:

- `command_used: "/speaking"`, `skills_practiced: ["speaking"]`
- `skill_scores.speaking: {exercises: N, correct: count_of_clear_answers, time_minutes}`
- `errors[]` — only communication-blocking ones (don't flood mistakes-db with minor speaking slips)
- `focus_next_session[]` — one topic + one pattern

Save exchange to `/results/speaking-session-{NNN}.md`.

## Examples

### Example 1 — personal intro (Dutch A2)

> ## Question 1: Introductions
>
> Vertel me over jezelf. Waar kom je vandaan?
> (Tell me about yourself. Where are you from?)

Learner: "Ik ben Mohammad. Ik kom van Iran maar ik woon nu in Nederland."

> ✅ Clear and natural!
>
> **What you said:** "Ik ben Mohammad. Ik kom van Iran maar ik woon nu in Nederland."
>
> **Communication:** Clear ✅
>
> **Grammar notes:**
> - 🟢 "van Iran" → **"uit Iran"** (prepositions — origin uses `uit`, not `van`). Small slip; message still crystal clear.
>
> **Natural alternative:**
> "Ik kom uit Iran, maar ik woon al een paar jaar in Nederland."
>
> **Score: 9/10**
> - Communication: 5/5
> - Grammar: 2/3
> - Vocabulary: 2/2
>
> Great start — you packed two ideas into one sentence, which is exactly what fluency looks like.

### Example 2 — role-play opener (café scenario)

> ## 🎭 Role-Play
>
> **Scenario:** You're at a café in Amsterdam. You want coffee and a vegetarian option for lunch.
> **Your role:** Customer
> **I'll be:** The server
>
> ---
>
> *"Goedemiddag! Wat wilt u drinken?"*
>
> **Your turn:**

## Critical Rules

- **Communication first.** A clear message with a missed article scores better than a grammatically perfect but confusing answer.
- **One question at a time.** Wait for reply before next.
- **Stay in the target language** for questions and transitions. Drop to native only for explanations.
- **Praise natural expression.** If the learner uses "Nou..." or "Eh..." correctly, call it out — those are fluency markers.
- **Don't over-correct.** A speaking session with 20 red marks kills confidence.
- **Never auto-invoke.** Gated; must fire only on explicit `/speaking`.

## Language Reference

### Dutch A2 conversational fillers

- "Nou..." (well / so)
- "Eh..." (uh / um)
- "Eigenlijk..." (actually)
- "Dus..." (so / therefore)
- "Ja, dat klopt" (yes, that's right)
- "Ik snap het niet" (I don't understand)

Add equivalents for other target languages as needed.
