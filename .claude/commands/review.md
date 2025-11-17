---
description: Review items due today (spaced repetition)
allowed-tools: Read, Write
---

# Spaced Repetition Review Session

Review items that are due today based on the SM-2 spaced repetition algorithm.

## Protocol

### 1. Load Review Queue

```
!`cat data/spaced-repetition.json`
!`cat data/mistakes-db.json`
!`cat data/mastery-db.json`
```

### 2. Check Today's Reviews

From `spaced-repetition.json` → `review_queue.today`:
- Count total items due
- Sort by priority (critical → high → medium → low)
- Limit to `daily_limits.review_items_per_day` (usually 20)

### 3. Greet and Explain

```markdown
# 🔄 Today's Spaced Repetition Review

Hallo the learner! Time to review items that your brain is about to forget. This keeps your knowledge fresh! 🧠

**Items Due Today:** {count}
**Estimated Time:** ~{minutes} minutes
**Focus:** Reinforce what you've learned

**Why Review?**
- Prevents forgetting (spaced repetition works!)
- Moves items to long-term memory
- Builds automaticity (instant recall)

**Ready? Let's start!** 💪
```

### 4. For Each Review Item

#### Item Structure
Each item in the queue has:
```json
{
  "item_id": "formal_informal_confusion",
  "item_type": "error_pattern",
  "review_type": "urgent",
  "easiness_factor": 1.3,
  "interval_days": 1,
  "repetitions": 0,
  "due_date": "2025-11-17",
  "priority": "critical"
}
```

#### Generate Appropriate Exercise

Based on `item_type`:

**If `item_type` = "error_pattern":**
- Load the pattern from `mistakes-db.json`
- Create targeted exercise testing that specific pattern
- Example: If pattern = "formal_informal_confusion", create scenario requiring formal "u" usage

**If `item_type` = "vocabulary":**
- Show the word and ask for translation (target language → English or vice versa)
- Or: Fill-in-blank sentence using the word

**If `item_type` = "grammar_rule":**
- Test application of the rule with a sentence completion or error correction

#### Present ONE Item at a Time

```markdown
## Review Item {N}/{total} - {Priority emoji}

**Type:** {error_pattern/vocabulary/grammar_rule}
**Last Reviewed:** {X} days ago
**Current Mastery:** {level}/5 ⭐

{Generate appropriate exercise based on item type}

**Type your answer!** ⏱️
```

### 5. Evaluate Response and Update

After the learner answers:

**Give Feedback:**
```markdown
{✅ Correct! or ❌ Not quite}

{If incorrect: explain the pattern/rule again}

**Score: {X}/10**

{If correct on first try: "Great! You remembered! 🎉"}
{If struggled: "Good effort! Let's review this again soon."}

---
```

**Update Spaced Repetition:**

Use SM-2 algorithm to calculate:
- New `easiness_factor`
- New `interval_days`
- New `repetitions` count
- New `due_date`
- Updated `mastery_level`

**Move item to appropriate queue:**
- If quality >= 3: Move to future queue (tomorrow/this_week/later)
- If quality < 3: Keep in today's queue (will review again soon)

### 6. Progress Updates During Session

Every 5 items, show quick progress:

```markdown
## Progress Update

**Reviewed:** {N}/{total}
**Accuracy:** {percentage}%
**Time Remaining:** ~{minutes} min

Keep going! 💪
```

### 7. Session Complete Summary

```markdown
## 🎉 Review Session Complete!

**Items Reviewed:** {count}
**Overall Accuracy:** {percentage}%
**Time Spent:** {minutes} minutes

### Results Breakdown

**Mastered (No mistakes):** {count}
- These items won't come up again for a while! 🎉

**Good (Minor mistakes):** {count}
- Review scheduled for {X} days from now

**Need More Practice:** {count}
- You'll see these again tomorrow

### Next Review Schedule

- **Tomorrow:** {count} items
- **This Week:** {count} items
- **Next Week:** {count} items

**Streak:** 🔥 {X} days! {motivational_message}

### Tips for Better Retention

- Review daily for best results (even just 10 minutes!)
- If you forget something, don't worry - the algorithm will show it more often
- The more you struggle now, the stronger the memory becomes
- Try to recall BEFORE looking at the answer

**Great work today, the learner!** Keep up the daily reviews! 🌟

---

Want to practice something new? Try:
- `/dutch` - Start new learning session
- `/dutch-writing` - Practice writing
- `/dutch-vocab` - Learn new vocabulary
```

### 8. Update All Databases

After review session:

1. **spaced-repetition.json**
   - Update all reviewed items with new SM-2 parameters
   - Move items between queues (today/tomorrow/this_week/later)
   - Recalculate mastery levels

2. **progress-db.json**
   - Update review statistics
   - Add review session to history

3. **session-log.json**
   - Add review session entry with:
     - Items reviewed
     - Accuracy rate
     - Time spent
     - Patterns that need more work

4. **mistakes-db.json**
   - Update error patterns that were reviewed
   - Increment/decrement mastery based on performance

## Spaced Repetition Tips

**For the learner:**

### Why Spaced Repetition Works
- Your brain naturally forgets things over time (Ebbinghaus forgetting curve)
- Reviewing just before you forget = strongest memory formation
- Each successful review makes the memory stronger and longer-lasting
- Items you struggle with appear more often (adaptive!)

### Best Practices
- ✅ **Review every day** (consistency > intensity)
- ✅ **Don't skip reviews** (breaks the spacing optimization)
- ✅ **Be honest with yourself** (if you struggled, mark it as such)
- ✅ **Review before learning new things** (consolidate first!)
- ✅ **10-15 minutes daily** is enough for maintenance

### What the Schedule Means
- **1 day:** New or struggling items (needs reinforcement)
- **2-3 days:** Learning items (building strength)
- **1 week:** Getting comfortable (occasional review)
- **2+ weeks:** Strong items (maintenance only)
- **1+ month:** Mastered items (long-term memory!)

**The algorithm adapts to YOU!** The more you practice, the smarter it gets. 🧠✨
