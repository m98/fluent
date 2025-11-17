# Data Directory

This directory contains your personal learning data in JSON format.

## 🚀 Getting Started

**This directory is empty by design!**

When you run `/setup` for the first time, the system will automatically create:

- `learner-profile.json` - Your name, target language, level, goals
- `progress-db.json` - Overall statistics and trends
- `mistakes-db.json` - Error patterns you're working on
- `mastery-db.json` - Skill mastery levels (0-5 stars)
- `spaced-repetition.json` - Review schedule (SM-2 algorithm)
- `session-log.json` - Complete session history

## 🔒 Privacy

**All files in this directory are private!**

- ✅ Listed in `.gitignore` - Won't be committed to git
- ✅ Stays on your machine - No external sync
- ✅ Automatically backed up - See `.backups/` directory
- ✅ Human-readable JSON - Easy to export/analyze

## 📊 File Structure

### learner-profile.json
Contains your basic information and preferences:
```json
{
  "learner": {
    "name": "Your Name",
    "target_language": "Spanish",
    "current_level": "A2",
    "target_level": "B2"
  },
  "current_streak_days": 0,
  "skills": {...}
}
```

### progress-db.json
Tracks your statistics over time:
```json
{
  "overall_stats": {
    "total_exercises": 0,
    "total_correct": 0,
    "accuracy_rate": 0
  },
  "accuracy_trend": []
}
```

### mistakes-db.json
Records error patterns with examples:
```json
{
  "error_patterns": {
    "pattern_name": {
      "frequency": 0,
      "mastery_level": 0,
      "examples": []
    }
  }
}
```

### mastery-db.json
Tracks mastery levels for each skill:
```json
{
  "skills": {
    "writing": {"mastery_level": 0},
    "speaking": {"mastery_level": 0},
    "vocabulary": {"mastery_level": 0}
  }
}
```

### spaced-repetition.json
Manages review scheduling (SM-2 algorithm):
```json
{
  "review_queue": {
    "today": [],
    "tomorrow": [],
    "this_week": [],
    "later": []
  }
}
```

### session-log.json
Complete history of all practice sessions:
```json
{
  "sessions": [
    {
      "id": "001",
      "date": "2025-11-17",
      "duration_minutes": 30,
      "accuracy": 0.85
    }
  ]
}
```

## 🔄 How It Works

1. **First time:** Run `/setup` to create your profile
2. **Every session:** Files update automatically as you practice
3. **Backup:** Automatic backups to `.backups/` via hooks
4. **Export:** All data is JSON - easy to analyze or migrate

## 📁 Data Examples

Want to see the structure before running `/setup`?

Check the `/data-examples` directory for template files with the complete schema.

## ⚠️ Important Notes

- **Never edit these files manually** - Let the system manage them
- **Don't delete while learning** - You'll lose your progress!
- **To reset:** Delete all `.json` files and run `/setup` again
- **To backup:** Copy entire `/data` directory

---

**Ready to start?** Run `/setup` to begin your language learning journey! 🚀
