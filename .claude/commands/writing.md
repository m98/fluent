---
description: Practice target language writing (emails, letters, forms)
allowed-tools: Read, Write
---

# target language Writing Practice

Practice writing emails, letters, and forms at A2 level.

## Protocol

### 1. Load Writing Context

```
!`cat data/learner-profile.json`
!`cat data/mistakes-db.json`
!`cat data/mastery-db.json`
```

Check the learner's weak patterns related to writing:
- Formal/informal distinction
- Email structure
- Common phrases
- Word order issues

### 2. Select Scenario Type

Based on `mastery-db.json` → `skills_mastery`:
- **Formal email** (if mastery < 4)
- **Informal email** (if mastery < 4)
- **Form filling** (if mastery < 4)
- **Newsletter/personal text** (if mastery < 3)
- **Mixed scenarios** (if all mastery >= 4)

### 3. Present Writing Task

```markdown
## ✍️ Writing Exercise

**Scenario:** {clear_description_in_English}

**Task:** Write a {type_of_text} in target language.

**Requirements:**
- Length: {X-Y} words/sentences
- Include: {must_include_elements}
- Level: A2 (keep it simple!)

**Example structure:** (optional, for difficult tasks)
{show_template_if_needed}

**Write your {text_type} below:**
```

### 4. Wait for the learner's Response

Let him write the complete text before giving feedback.

### 5. Analyze Response (Systematic!)

Check for these error categories:
1. **Grammar errors** (word order, verb conjugation, articles)
2. **Formal/Informal mixing** (u vs je confusion)
3. **Vocabulary errors** (wrong words, English mixing)
4. **Missing elements** (forgot greeting, closing, etc.)
5. **Spelling** (mark as minor - allowed in A2 exam)
6. **Structure issues** (organization, flow)

### 6. Provide Detailed Feedback

```markdown
## Feedback

### ✅ What You Did Well
- {strength1}
- {strength2}
- {strength3}

### ❌ Areas to Improve

**Critical Issues:** 🔴
- {issue1}: **Example:** "{wrong}" → **Should be:** "{correct}"
  - **Why:** {explanation}

**Moderate Issues:** 🟡
- {issue2}: {explanation}

**Minor Issues:** 🟢 (Low priority for exam)
- {spelling_errors}

### 📝 Corrected Version

```
{Fully corrected text with all improvements}
```

**Overall Score: {X}/10**

**Breakdown:**
- Grammar: {Y}/10
- Vocabulary: {Z}/10
- Structure: {W}/10
- Communication: {V}/10

---
```

### 7. Update Databases After Feedback

For each error found:
- **mistakes-db.json**: Add/update error pattern
  - Increment frequency
  - Add example
  - Recalculate mastery_level
  - Schedule next review (spaced repetition)

- **mastery-db.json**: Update writing skill mastery
  - Update sub-skills (greeting, body, closing, etc.)
  - Recalculate overall writing mastery

- **progress-db.json**: Update writing stats
  - Increment exercises_completed
  - Update accuracy metrics
  - Add to accuracy_trend array

### 8. Optional: Rewrite Exercise

If score < 7/10, offer:

```markdown
**Want to try again?** 💪

You can rewrite the {text_type} now with the corrections in mind.
This will help solidify the patterns!

Type "rewrite" to try again, or "next" to continue.
```

### 9. Session Summary

```markdown
## 📊 Writing Session Summary

**Text Type:** {formal_email/informal_email/form/etc}
**Score:** {X}/10
**Strong Points:** {Y}
**Areas Improved:** {Z}

**Key Takeaways:**
- {learning_point_1}
- {learning_point_2}
- {learning_point_3}

**For Next Practice:**
- Focus on: {specific_weakness}
- Review: {relevant_flashcards_or_patterns}

Goed gedaan! Keep practicing! ✍️
```

## Writing Tips for the learner

**Formal Emails:**
- Always use "u" (not "je")
- Start: "Beste meneer/mevrouw {NAME},"
- Open: "Ik schrijf u omdat..."
- Close: "Met vriendelijke groet," + name

**Informal Emails:**
- Use "je" (not "u")
- Start: "Hallo {NAME},"
- More casual language OK
- Close: "Groetjes," or "Tot snel,"

**Common Mistakes to Avoid:**
- ❌ Don't mix formal/informal in same text
- ❌ Watch word order in "omdat" clauses
- ❌ Remember: "om 10:00 uur" (at time), "op dinsdag" (on day)
- ❌ Don't forget "u" after "Ik schrijf" in formal contexts

Let's improve your writing! 🚀
