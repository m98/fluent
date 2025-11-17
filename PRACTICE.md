# AI Guide: Dutch Writing Practice Methodology

**Purpose:** This document instructs Claude AI on how to analyze practice session results, track student progress, and deliver adaptive lessons for A2 Dutch writing exam preparation.

---

## 📁 File Structure You Will Work With

### Result Files Location
- **Path:** `/results/writing-session-[ID].md`
- **Format:** Markdown with structured sections
- **Created:** One per practice session
- **Naming:** Sequential IDs (001, 002, 003...)

### Result File Required Structure

Every result file MUST contain these sections:

```markdown
# Writing Practice Session [ID]
**Date:** YYYY-MM-DD
**Exam Date:** YYYY-MM-DD
**Duration:** X minutes
**Focus:** [Topic/skill area]

---

## Session Goals
- [ ] Goal 1
- [ ] Goal 2

---

## Drill [N]: [Name] ([X] questions)
**Time:** X-Y minutes

### Question [N]: [English prompt]
**Your answer:** [Student's Dutch answer]
**Correct answer:** [Correct Dutch answer]

**Analysis:**
- ❌ Error description with correction
- ✅ What was correct

**Score: X/10** [emoji + comment]

---

## Drill [N] Summary
**Total Score: X/Y (Z%)**

### 🚨 CRITICAL PATTERNS TO FIX NOW:
1. Pattern name + explanation
2. ...

### 💪 STRENGTHS:
- What student did well

---

## Next Steps
[What to practice next]

---

**Session Progress:** X/Y minutes
```

---

## 🔍 How to Analyze Result Files

### Step 1: Read the Latest Session File
Always start by reading `/results/writing-session-[latest].md`

### Step 2: Extract Error Patterns
Categorize every ❌ error into:
- **Grammar** (word order, verb conjugation, clause structure)
- **Vocabulary** (wrong word choice, missing words)
- **Spelling** (minor - not critical for exam!)
- **Formal/Informal** (u vs je, uw vs jouw)
- **Prepositions** (om/op/in/bij/naar/etc)
- **English Mixing** (using English words)

### Step 3: Count Frequency
Track how many times each pattern appears:
- 1 occurrence = might be a typo
- 2-3 occurrences = emerging pattern
- 4+ occurrences = **CRITICAL WEAKNESS** ⚠️

### Step 4: Identify Strengths
Look for ✅ marks and high scores (7+/10). Note what the student:
- Does consistently well
- Shows improvement on
- Has intuition for

### Step 5: Build Pattern Database (in your memory for the session)
Create a mental table:
```
| Error Type | Pattern | Count | Severity | Example |
```

---

## 📊 Tracking Tables to Maintain in Result Files

### Mistake Tracking Table
Include this in each session summary:

```markdown
## Error Pattern Summary

| Category | Specific Pattern | Count This Session | Total Count | Severity | Example |
|----------|------------------|-------------------|-------------|----------|---------|
| Formal/Informal | Using "je" in formal context | 2 | 5 | 🔴 CRITICAL | "Ik schrijf je" → "Ik schrijf u" |
| Word Order | Wrong "omdat" clause order | 1 | 3 | 🟡 MODERATE | "omdat ik kan niet" → "omdat ik niet kan" |
```

### Strength Tracking Table

```markdown
## Strengths Identified

| Skill | Evidence | Confidence Level | Notes |
|-------|----------|------------------|-------|
| Vocabulary recall | Correctly used "afspraak", "dokter" | ⭐⭐⭐⭐☆ | Flashcards working! |
| Writing speed | Completed all questions quickly | ⭐⭐⭐⭐⭐ | Good for timed exam |
```

### Progress Over Time Table

```markdown
## Progress Metrics

| Session | Date | Overall Score | Critical Errors | Moderate Errors | Spelling Errors |
|---------|------|---------------|-----------------|-----------------|-----------------|
| 001 | 2025-11-16 | 35% | 5 | 4 | 3 |
| 002 | ... | ... | ... | ... | ... |
```

---

## 🎯 Spaced Repetition Strategy

### Mastery Levels
Assign each error pattern a mastery level:
- **0 stars:** New error, seen once
- **1 star:** Seen 2-3 times, not corrected
- **2 stars:** Student corrected once, but still makes mistake
- **3 stars:** Student corrects most times, occasional slip
- **4 stars:** Rarely makes this mistake
- **5 stars:** Mastered, no errors in last 5 attempts

### Review Scheduling
Based on mastery level:
- **0-1 stars:** Review EVERY session
- **2 stars:** Review every 2 sessions
- **3 stars:** Review every 3-5 sessions
- **4-5 stars:** Spot check only

### Drill Priority
In each session, allocate time:
- **50%** on 0-1 star patterns (critical weaknesses)
- **30%** on 2-3 star patterns (consolidation)
- **20%** on full scenarios (integration)

---

## 🧠 Educational Principles to Apply

### 1. Immediate Feedback
- Correct EVERY error instantly
- Explain WHY it's wrong
- Show the correct version
- Have student rewrite correctly

### 2. Pattern Recognition Over Memorization
- Help student see the SYSTEM (e.g., "all time expressions use 'om'")
- Group similar errors together
- Create rules they can remember

### 3. Interleaving (Mixed Practice)
- DON'T drill one topic for 20 minutes
- Mix formal email + informal email + time expressions
- Forces brain to discriminate (key exam skill!)

### 4. Desirable Difficulty
- Start easy (fill in blanks)
- Progress to medium (complete sentences)
- End hard (full scenarios)
- Adjust based on success rate (aim for 60-70% correct)

### 5. Confidence Building
- Always start with 1-2 easy wins
- Celebrate improvements ("Last time you got this wrong, now you got it right!")
- Frame errors as "patterns to fix" not personal failures

### 6. Exam Simulation
- Use authentic exam scenarios
- Enforce time limits
- Practice ALL 4 task types (formal, informal, personal, form)

---

## 🎓 How to Generate Next Session Plan

### Read Previous Session Results
1. Identify TOP 3 critical errors (highest frequency + severity)
2. Identify 1-2 strengths to reinforce
3. Note overall score trend

### Design Adaptive Drill Sequence

**Template:**
```markdown
## Session [N] Plan (X minutes)

**Top 3 Weaknesses from Last Session:**
1. [Pattern] - occurred [N] times
2. [Pattern] - occurred [N] times
3. [Pattern] - occurred [N] times

**Strengths to Reinforce:**
- [Skill]

**Drill Sequence:**
1. **Warm-up (5 min):** Quick wins on known patterns
2. **Targeted Drill 1 (10 min):** Focus on weakness #1
   - 5 isolated practice questions
   - 2 application questions
3. **Targeted Drill 2 (10 min):** Focus on weakness #2
   - [similar structure]
4. **Mixed Integration (10 min):** Combine all patterns
5. **Full Scenario (10 min):** Complete exam-style task
6. **Review (5 min):** Student self-corrects, AI gives feedback
```

### Adapt Difficulty Based on Performance
- If student scores <50%: Simplify, add more scaffolding
- If student scores 50-70%: Perfect difficulty, continue
- If student scores >70%: Increase difficulty, introduce new patterns

---

## 📝 Question Types to Use

### Isolated Pattern Drill
**Example:** "Fill in: Ik schrijf ___ omdat... (formal context)"
- Tests one specific skill
- Immediate feedback

### Sentence Completion
**Example:** "Complete: Ik kan morgen niet komen omdat... (reason: sick)"
- Tests structure + vocabulary
- Medium difficulty

### Translation
**Example:** "Write in Dutch: I am writing to you because I have a question"
- Tests full production
- High difficulty

### Error Correction
**Example:** "Fix this: Ik scrift je omdat ik kan niet komen vandag"
- Builds editing skill
- Shows pattern awareness

### Full Scenario
**Example:** "Write an email to your boss requesting Thursday off (40 words)"
- Exam simulation
- Integrates all skills

---

## 🚨 Red Flags to Watch For

### Critical Issues (Must Fix Before Exam)
- **Formal/Informal confusion** → Will lose major points
- **Wrong word order in clauses** → Incomprehensible Dutch
- **English mixing** → Shows lack of vocabulary depth

### Moderate Issues (Work On These)
- **Preposition errors** → Can usually be understood from context
- **Missing articles (de/het)** → Minor point deduction
- **Verb conjugation slips** → Depends on context

### Minor Issues (Don't Worry)
- **Spelling mistakes** → Exam allows some errors
- **Punctuation** → Not heavily penalized at A2
- **Accent marks** → Usually optional

---

## 💬 How to Give Feedback

### Format for Each Answer
```markdown
**Your answer:** [exactly what student wrote]
**Correct answer:** [ideal version]

**Analysis:**
- ❌ [Specific error] → [Correction] (Category: [type])
- ✅ [What was good]

**Score: X/10** [Emoji + encouraging/corrective comment]
```

### Tone Guidelines
- **Be direct** but encouraging
- **Explain WHY** something is wrong
- **Show the pattern** not just the correction
- **Celebrate progress** ("You didn't make this mistake this time!")
- **Be honest** about severity (critical vs minor)

---

## 🎯 Session Goals Template

Every session should have:
1. **Skill goal:** Master [specific pattern]
2. **Accuracy goal:** Score X% or higher
3. **Speed goal:** Complete in Y minutes
4. **Application goal:** Use in full scenario successfully

---

## 📈 Success Metrics

### Track These Over Time
- Overall accuracy % (target: 70%+)
- Critical error count (target: <2 per session)
- Moderate error count (target: <5 per session)
- Speed (words per minute written)
- Confidence (self-reported 1-5 scale)

### Session Success =
- Student improved on at least 1 weakness from last session
- Student maintained strengths
- Student completed all planned drills
- Student understands what to practice next

---

## 🔄 Continuous Improvement Loop

```
Read latest session file
↓
Identify patterns (errors + strengths)
↓
Update mental tracking tables
↓
Design adaptive drill plan
↓
Run session, record results
↓
Write new session file
↓
[REPEAT]
```

---

**Last Updated:** 2025-11-16
**Version:** 1.0
**Methodology:** Evidence-based learning (spaced repetition, immediate feedback, interleaving, adaptive difficulty)
