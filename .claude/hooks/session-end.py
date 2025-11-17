#!/usr/bin/env python3
"""
Fluent Session End Hook
Creates daily backups and displays session summary
"""
import json
import sys
import os
import shutil
from datetime import datetime
from pathlib import Path

def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        pass  # Input might be empty for SessionEnd

    # Create dated backup directory
    backup_dir = Path(".backups") / datetime.now().strftime("%Y%m%d")
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Backup all data files
    data_dir = Path("data")
    if data_dir.exists():
        backed_up = []
        for json_file in data_dir.glob("*.json"):
            try:
                shutil.copy2(json_file, backup_dir / json_file.name)
                backed_up.append(json_file.name)
            except Exception as e:
                print(f"[Fluent] Warning: Could not backup {json_file}: {e}", file=sys.stderr)

        if backed_up:
            print(f"[Fluent] 📦 Session backup created: {backup_dir}/")
            print(f"[Fluent] 💾 Files backed up: {', '.join(backed_up)}")

    # Display learner stats if available
    profile_path = Path("data/learner-profile.json")
    if profile_path.exists():
        try:
            with open(profile_path, 'r') as f:
                profile = json.load(f)

            stats = profile.get("stats", {})
            streak = stats.get("streak_days", 0)
            total_sessions = stats.get("total_practice_sessions", 0)

            print(f"[Fluent] 🔥 Current streak: {streak} days")
            print(f"[Fluent] 📊 Total sessions: {total_sessions}")
            print(f"[Fluent] 👋 Great work today!")

        except Exception as e:
            print(f"[Fluent] Could not read stats: {e}", file=sys.stderr)

    sys.exit(0)

if __name__ == "__main__":
    main()
