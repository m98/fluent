# Fluent Hooks System

This directory contains automated hooks that manage data integrity, backups, and user feedback for the Fluent language learning system.

## 🎯 Purpose

Hooks ensure your learning data is:
- ✅ **Always backed up** - Multiple backup strategies prevent data loss
- ✅ **Validated** - JSON structure checked on every save
- ✅ **Tracked** - Session stats displayed automatically
- ✅ **Safe** - Backups created before risky operations (compaction)

## 📋 Hook Scripts

### 1. `validate-data.py` (PostToolUse)

**Triggered:** After every Write/Edit operation on data files

**What it does:**
1. Checks if the modified file is in `data/*.json`
2. Validates JSON structure using Python's JSON parser
3. Creates timestamped backup: `data/file.json.backup-20231117-143022`
4. Shows success message or warning if JSON is invalid

**Example output:**
```
[Fluent] ✓ Data saved and validated: data/learner-profile.json
[Fluent] 💾 Backup created: data/learner-profile.json.backup-20231117-143022
```

**Error handling:**
- Invalid JSON triggers exit code 2, blocking the operation and alerting Claude
- Error message shown: `[Fluent] ⚠️ WARNING: Invalid JSON in data/file.json`

---

### 2. `session-end.py` (SessionEnd)

**Triggered:** When practice session ends (user exits Claude Code)

**What it does:**
1. Creates daily backup directory: `.backups/YYYYMMDD/`
2. Copies all `data/*.json` files to the backup folder
3. Reads `learner-profile.json` to display session summary
4. Shows current streak and total sessions

**Example output:**
```
[Fluent] 📦 Session backup created: .backups/20231117/
[Fluent] 💾 Files backed up: learner-profile.json, progress-db.json, mistakes-db.json
[Fluent] 🔥 Current streak: 7 days
[Fluent] 📊 Total sessions: 42
[Fluent] 👋 Great work today!
```

**Backup location:** `.backups/YYYYMMDD/` (excluded from git)

---

### 3. `session-start.py` (SessionStart)

**Triggered:** When Claude Code starts a new session

**What it does:**
1. Checks if `data/learner-profile.json` exists
2. If not found, prompts user to run `/setup`
3. If found, displays:
   - Welcome message with learner's name
   - Target language and current/target level
   - Current streak
4. Checks `spaced-repetition.json` for due reviews
5. Alerts user if reviews are due today

**Example output (first time):**
```
[Fluent] 🌍 Welcome to Fluent - The AI Language Learning Kit!
[Fluent] 📝 Run /setup to create your personalized learning profile
```

**Example output (returning user):**
```
[Fluent] 🌍 Welcome back, Mohammad!
[Fluent] 📚 Learning: Spanish
[Fluent] 🎯 Level: A2 → B1
[Fluent] 🔥 Streak: 12 days
[Fluent] 📅 15 items due for review today - Run /review!
```

---

### 4. PreCompact Hook (inline bash)

**Triggered:** Before conversation is compacted (manual `/compact` or auto-compact)

**What it does:**
1. Creates safety backup directory: `.backups/precompact/`
2. Copies all `data/*.json` files
3. Shows confirmation message

**Example output:**
```
[Fluent] 🔒 Pre-compact backup saved
```

**Purpose:** Ensures data safety before potentially destructive operations

---

## 🔧 How It Works

### Hook Configuration

Hooks are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/validate-data.py"
          }
        ]
      }
    ]
  }
}
```

### Hook Execution Flow

1. **Event occurs** (e.g., file is written)
2. **Claude Code triggers hook** based on matcher pattern
3. **Script receives JSON input via stdin**:
   ```json
   {
     "session_id": "abc123",
     "tool_name": "Write",
     "tool_input": {
       "file_path": "data/learner-profile.json",
       "content": "..."
     }
   }
   ```
4. **Script processes input** and performs actions
5. **Script exits with status code**:
   - `0` = Success (stdout shown in verbose mode)
   - `2` = Blocking error (stderr shown to Claude)
   - Other = Non-blocking error (logged)

### Exit Code Behavior

| Exit Code | Behavior | When to Use |
|-----------|----------|-------------|
| `0` | Success, continue normally | Validation passed, backup created |
| `2` | Block operation, show stderr to Claude | Invalid JSON, critical error |
| Other | Log error, continue anyway | Non-critical warning |

---

## 📂 Backup Strategy

Fluent uses a multi-layered backup system:

### Layer 1: Individual File Backups (PostToolUse)
- **Location:** `data/*.json.backup-YYYYMMDD-HHMMSS`
- **Created:** Every time a data file is modified
- **Retention:** Manual cleanup (keeps all versions)
- **Purpose:** Granular version history

### Layer 2: Daily Snapshots (SessionEnd)
- **Location:** `.backups/YYYYMMDD/`
- **Created:** When session ends
- **Retention:** Manual cleanup (one snapshot per day)
- **Purpose:** Daily checkpoints

### Layer 3: Pre-Compaction Safety (PreCompact)
- **Location:** `.backups/precompact/`
- **Created:** Before conversation compaction
- **Retention:** Overwritten on each compact
- **Purpose:** Rollback point for risky operations

**All backup directories are excluded from git via `.gitignore`**

---

## 🛠️ Customization

### Adding Custom Validation

Edit `validate-data.py` to add custom validation logic:

```python
# Example: Validate specific field exists
if file_path == "data/learner-profile.json":
    if "learner" not in data or "target_language" not in data["learner"]:
        print("[Fluent] ⚠️ Missing required field: target_language", file=sys.stderr)
        sys.exit(2)  # Block operation
```

### Adding Session Analytics

Edit `session-end.py` to add custom analytics:

```python
# Example: Calculate accuracy trend
progress_path = Path("data/progress-db.json")
if progress_path.exists():
    with open(progress_path, 'r') as f:
        progress = json.load(f)

    accuracy = progress.get("overall_stats", {}).get("accuracy_rate", 0)
    print(f"[Fluent] 📈 Overall accuracy: {accuracy:.1%}")
```

### Adding New Hooks

To add a new hook type:

1. **Create script** in `.claude/hooks/your-hook.py`
2. **Make it executable**: `chmod +x .claude/hooks/your-hook.py`
3. **Add to settings.json**:
   ```json
   {
     "hooks": {
       "YourHookEvent": [
         {
           "hooks": [
             {
               "type": "command",
               "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/your-hook.py"
             }
           ]
         }
       ]
     }
   }
   ```

---

## 🔍 Debugging Hooks

### Enable Debug Mode

Run Claude Code with debug flag:
```bash
claude --debug
```

This shows detailed hook execution logs:
```
[DEBUG] Executing hooks for PostToolUse:Write
[DEBUG] Hook command: .claude/hooks/validate-data.py
[DEBUG] Hook completed with status 0
```

### View Hook Output

Enable verbose mode during session:
- Press **Ctrl+O** to toggle transcript mode
- Shows all hook stdout/stderr output

### Test Hooks Manually

You can test hooks directly:

```bash
# Test validate-data hook
echo '{"tool_name":"Write","tool_input":{"file_path":"data/test.json"}}' | .claude/hooks/validate-data.py

# Test session-start hook
echo '{}' | .claude/hooks/session-start.py
```

---

## 📊 Hook Events Reference

| Hook Event | When It Fires | Use Case |
|------------|---------------|----------|
| `PostToolUse` | After Write/Edit/Read/etc | Data validation, backups |
| `SessionEnd` | When session ends | Cleanup, summaries, backups |
| `SessionStart` | When session starts | Welcome messages, stats |
| `PreCompact` | Before compaction | Safety backups |
| `UserPromptSubmit` | Before processing user input | Prompt validation |
| `PreToolUse` | Before tool execution | Permission checks |

---

## 🚨 Troubleshooting

### Hook Not Running

**Problem:** Hook doesn't execute
**Solution:**
1. Check hook is registered: `cat .claude/settings.json | grep hooks`
2. Verify script is executable: `ls -la .claude/hooks/`
3. Test script manually (see "Test Hooks Manually" above)

### Invalid JSON Error

**Problem:** `[Fluent] ⚠️ WARNING: Invalid JSON`
**Solution:**
1. Check the last backup: `ls -t data/*.backup-* | head -1`
2. Validate JSON: `python3 -m json.tool data/file.json`
3. Restore from backup if needed: `cp data/file.json.backup-XXXXXX data/file.json`

### Permission Denied

**Problem:** `Permission denied` when running hook
**Solution:**
```bash
chmod +x .claude/hooks/*.py
```

### Hook Timeout

**Problem:** Hook times out (default 60s)
**Solution:** Increase timeout in settings.json:
```json
{
  "type": "command",
  "command": "...",
  "timeout": 120
}
```

---

## 📚 Additional Resources

- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks-guide)
- [Hooks Reference](https://code.claude.com/docs/en/hooks-reference)
- [Fluent Main README](../../README.md)
- [Learning System Guide](../../LEARNING_SYSTEM.md)


