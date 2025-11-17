---
description: View your Language learning progress and statistics
allowed-tools: Read
---

# Your target language Learning Progress

Show the learner comprehensive progress statistics with visualizations.

## Protocol

### 1. Load All Progress Data

```
data/learner-profile.json
data/progress-db.json
data/mastery-db.json
data/mistakes-db.json
data/spaced-repetition.json
data/session-log.json
```

**Note:** If any of these files don't exist in `/data`, check the `data-examples/` directory for template files (e.g., `learner-profile-template.json`). You may need to copy them to `/data` and initialize them.

### 2. Generate Progress Report

```markdown
# 📊 the learner's target language Learning Dashboard

**Last Updated:** {current_date}

---

## 🎯 Overview

**Current Level:** A2 (Elementary)
**Target Level:** B2+ (Upper Intermediate)
**Progress to B1:** ▓▓▓▓▓▓▓▓░░░░░░░░░░░░ {percentage}%

**Days Studying:** {total_days}
**Current Streak:** 🔥 {streak_days} days {streak_message}
**Total Sessions:** {total_sessions}
**Total Study Time:** {total_minutes} minutes ({hours} hours)

---

## 💪 Skills Mastery

### Writing ✍️
**Level:** {mastery_level}/5 ⭐⭐⭐⭐☆
**Accuracy:** {accuracy}%
**Progress:** ▓▓▓▓▓▓▓▓▓░░░░░░
**Last Practiced:** {date}

**Sub-Skills:**
- Formal emails: {level}/5 ⭐
- Informal emails: {level}/5 ⭐
- Forms: {level}/5 ⭐
- Grammar: {level}/5 ⭐

### Speaking 🗣️
**Level:** {mastery_level}/5 ⭐⭐☆☆☆
**Accuracy:** {accuracy}%
**Progress:** ▓▓▓▓░░░░░░░░░░░░
**Last Practiced:** {date or "Not yet practiced"}

### Vocabulary 📚
**Level:** {mastery_level}/5 ⭐⭐⭐⭐☆
**Words Known:** {words_known}
**Words Mastered:** {words_mastered}
**Progress:** ▓▓▓▓▓▓▓▓▓▓▓░░░░░
**Last Practiced:** {date}

### Reading 👀
**Level:** {mastery_level}/5 ⭐⭐☆☆☆
**Comprehension:** {percentage}%
**Progress:** ▓▓▓▓▓░░░░░░░░░░░
**Last Practiced:** {date or "Not yet practiced"}

---

## 📈 Progress Trends

### Accuracy Over Time
```
Week 1: ██████░░░░░░░░░░░░ 35%
Week 2: ████████████░░░░░░ 60% (+25%)
Week 3: ██████████████░░░░ 70% (+10%)
Week 4: ████████████████░░ 80% (+10%)  ← Goal trend
```

### This Week's Summary
- **Sessions:** {count}
- **Minutes:** {total}
- **Exercises:** {count}
- **Accuracy:** {percentage}%
- **Skills Practiced:** {list}

---

## 🎯 Focus Areas

### 🔴 Critical (Needs Urgent Attention)
{List patterns from mistakes-db with mastery 0-1 and high frequency}

### 🟡 Working On (Making Progress)
{List patterns from mistakes-db with mastery 2-3}

### 🟢 Strong (Almost Mastered)
{List patterns from mistakes-db with mastery 4-5}

---

## 🔄 Spaced Repetition Status

**Items Due Today:** {count}
**Items Due This Week:** {count}
**Items Mastered (No review needed):** {count}

**Review Distribution:**
- Today: {count} items
- Tomorrow: {count} items
- This week: {count} items
- Later: {count} items

---

## 🏆 Achievements Unlocked

{List all achievements from learner-profile → achievements}

**Example:**
- ✅ First Step - Completed first session (2025-11-16)
- ✅ Quick Learner - Improved 25% in one session (2025-11-16)
- 🔒 3-Day Streak - Maintain 3-day streak (Not yet)
- 🔒 Vocabulary Master - Learn 200 words (150/200)

---

## 📅 Session History

**Recent Sessions:**

| Date | Duration | Skill | Accuracy | Improvement |
|------|----------|-------|----------|-------------|
{Generate table from session-log}

---

## 🎯 Next Goals

**Short-term (This Week):**
- [ ] Practice speaking for first time
- [ ] Complete 5 writing exercises
- [ ] Review all due spaced repetition items
- [ ] Maintain 7-day streak

**Medium-term (This Month):**
- [ ] Reach 80% writing accuracy
- [ ] Master formal/informal distinction
- [ ] Learn 50 new vocabulary words
- [ ] Complete 20 total sessions

**Long-term (6 months):**
- [ ] Reach B1 level
- [ ] Pass B1 inburgering exam
- [ ] Confidently write any A2/B1 text
- [ ] Speak comfortably in everyday situations

---

## 💡 Recommendations

Based on your progress, focus on:
1. **{skill_name}** - You haven't practiced this recently
2. **{pattern_name}** - Still making this mistake frequently
3. **{review_items}** - Don't forget today's spaced repetition reviews!

---

## 🎉 Motivation

"{Personalized_motivational_message_based_on_progress}"

**Keep going, the learner! You're making excellent progress!** 💪🔥

---

Want to practice now? Try:
- `/dutch` - Start a learning session
- `/dutch-review` - Review today's items
- `/dutch-writing` - Practice writing
```

### 3. Interpretation Notes for the learner

Add a section explaining what the numbers mean:

```markdown
## 📖 How to Read Your Stats

**Mastery Levels:**
- ⭐☆☆☆☆ (1/5): Just started, needs lots of practice
- ⭐⭐☆☆☆ (2/5): Learning, making progress
- ⭐⭐⭐☆☆ (3/5): Good understanding, occasional mistakes
- ⭐⭐⭐⭐☆ (4/5): Strong skill, rare mistakes
- ⭐⭐⭐⭐⭐ (5/5): Mastered! Can use confidently

**Accuracy:**
- 0-40%: Needs intensive practice
- 40-60%: Learning phase, keep practicing
- 60-75%: Good progress, getting comfortable
- 75-85%: Strong skill, minor refinement needed
- 85%+: Excellent! Near mastery

**Streaks:**
- Maintain daily practice for best results
- Spaced repetition works best with consistency
- Even 15 minutes daily beats 2 hours weekly!
```

## Tips

- Update this report after every session
- Celebrate improvements, no matter how small!
- Use trends to identify what's working
- Adjust practice focus based on weak areas
- Share progress to stay motivated!

Je doet het geweldig! (You're doing great!) 🌟
