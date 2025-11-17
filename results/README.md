# Session Results Directory

This directory contains detailed logs from your practice sessions.

## 🚀 Getting Started

**This directory is empty by design!**

After each practice session, the system automatically creates a detailed result file here:

- `session-001.md` - Your first session
- `session-002.md` - Your second session
- `session-003.md` - And so on...

## 📝 What's in a Session Result File?

Each file contains comprehensive tracking of your practice session:

### Example Structure:

```markdown
# Language Learning Session - 001

**Date:** 2025-11-17
**Duration:** 30 minutes
**Skill:** Writing Practice
**Language:** Spanish

## Session Summary
- Questions: 10
- Correct: 8
- Accuracy: 80%
- Improvement: +15% from last session

## Questions & Answers

### Question 1: Past Tense Translation
**Your answer:** "Yo fue al mercado ayer"
**Correct answer:** "Yo fui al mercado ayer"
**Score:** 8/10
**Feedback:** Good attempt! Just need the correct conjugation of "ir"...

[... all 10 questions ...]

## Error Analysis

| Pattern | Category | Frequency | Mastery Level |
|---------|----------|-----------|---------------|
| Irregular verbs (past) | Grammar | 2 times | ⭐⭐⭐☆☆ (3) |
| Article agreement | Grammar | 1 time | ⭐⭐⭐⭐☆ (4) |

## Progress Tracking

**Improvements:**
- Past tense accuracy: 60% → 80%
- Vocabulary recall getting faster

**Focus Areas:**
- Practice irregular verb conjugations
- Review ser vs estar

**Next Session:**
- More past tense practice
- Introduce present perfect
```

## 🔒 Privacy

**All files in this directory are private!**

- ✅ Listed in `.gitignore` - Won't be committed to git
- ✅ Stays on your machine - No external sync
- ✅ Human-readable Markdown - Easy to read and review
- ✅ Automatically backed up - See `.backups/` directory

## 📊 Why Keep Session Results?

These files help you:

1. **Review your progress** - See exactly what you practiced
2. **Track patterns** - Identify recurring mistakes
3. **Measure improvement** - Compare sessions over time
4. **Study specific areas** - Review explanations for mistakes
5. **Motivate yourself** - See how far you've come!

## 🔍 How to Use

**Reading your results:**
```bash
# View your latest session
cat results/session-001.md

# Search for specific topics
grep "past tense" results/*.md

# Count total sessions
ls results/*.md | wc -l
```

**Analyzing patterns:**
- Look for recurring errors across multiple sessions
- Notice improvements in accuracy over time
- Identify which skills need more practice

## 📁 File Format

Files are in **Markdown format** (`.md`):
- Easy to read in any text editor
- Can be opened in VS Code, Obsidian, etc.
- Contains tables, formatted text, emojis
- Supports code blocks and formatting

## ⚠️ Important Notes

- **Don't delete these files** - They're your learning history!
- **Don't edit manually** - Let the system create them
- **Review regularly** - Check your progress weekly
- **Backup if needed** - Copy entire `/results` directory

## 🎯 Tips

**Weekly review routine:**
1. Read your last 5 session files
2. Note common error patterns
3. Celebrate improvements
4. Adjust your practice focus

**Monthly milestone:**
1. Compare first session vs latest
2. Calculate improvement percentage
3. Unlock achievements based on progress
4. Set new goals for next month

---

**Ready to practice?** Run `/learn` to create your first session result! 🚀

*Session results are created automatically at the end of each practice session.*
