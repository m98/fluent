---
description: Practice target language vocabulary with flashcard-style drills
allowed-tools: Read, Write
---

# target language Vocabulary Practice

Start a vocabulary drill session with the learner using spaced repetition principles.

## Protocol

### 1. Load Vocabulary Data

```
data/spaced-repetition.json
data/mistakes-db.json
data/mastery-db.json
```

**Note:** If any of these files don't exist in `/data`, check the `data-examples/` directory for template files (e.g., `spaced-repetition-template.json`). You may need to copy them to `/data` and initialize them.

### 2. Select Words to Practice

**Priority Order:**
1. Items in `spaced-repetition.json` → `review_queue.today` (due for review)
2. Words from `mistakes-db.json` where category = "Vocabulary" and `mastery_level` <= 2
3. New high-frequency words from the learner's focus areas

**Limit:** 20 words max per session (from `spaced-repetition.json` → `daily_limits.review_items_per_day`)

### 3. Drill Format (ONE AT A TIME!)

**Mode 1: target language → English (Recognition)**
```markdown
## Word {N}/20

**target language:** {word}

**Context:** {example_sentence_in_dutch}

**What does it mean in English?**

**Type your answer:**
```

**Mode 2: English → target language (Production)**
```markdown
## Word {N}/20

**English:** {word}

**Use it in a sentence:** (Optional)

**How do you say this in target language?**

**Type your answer:**
```

**Mode 3: Fill in the blank**
```markdown
## Word {N}/20

**Complete the sentence:**

{target language_sentence_with_____}

**Type the missing word:**
```

### 4. After Each Answer

Give immediate feedback:

```markdown
{✅ Correct! or ❌ Not quite...}

**Answer:** {correct_word}
**Meaning:** {meaning}
**Example:** {example_sentence}

{If incorrect: **Common mistake:** {explain why they might have made this error}}

**Score: {X}/10**

---
```

Then **UPDATE** `spaced-repetition.json` using SM-2 algorithm:
- Calculate quality score from performance
- Update interval, easiness factor, next review date
- Update mastery level if needed

### 5. Session Summary

After all words reviewed:

```markdown
## 📚 Vocabulary Session Complete!

**Words Reviewed:** {N}
**Accuracy:** {X}%
**New Words Learned:** {Y}
**Words Mastered:** {Z} (moved to mastery level 5)

**Strong Words:** (mastery 4-5)
- {word1}, {word2}, {word3}...

**Need More Practice:** (mastery 0-2)
- {word1}, {word2}, {word3}...

**Next Review:**
- Tomorrow: {N} words
- This week: {M} words

Goed gedaan! 🌟
```

### 6. Update Databases

- **spaced-repetition.json**: Update all reviewed items
- **mastery-db.json**: Update vocabulary category mastery
- **progress-db.json**: Update vocabulary skill stats
- **session-log.json**: Add vocabulary session entry

## Tips for the learner

- **Review daily** for best retention (spaced repetition works!)
- **Focus on weak words** (mastery 0-2) more than strong ones
- **Use words in sentences** to build contextual memory
- **Pronunciation matters** - try saying them out loud!

Ready to boost your vocabulary! 💪
