#!/usr/bin/env python3
"""
Fluent Session Start Hook
Displays welcome message with learner stats and due reviews
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

def main():
    # Read hook input from stdin (optional for SessionStart)
    try:
        hook_input = json.load(sys.stdin)
    except:
        pass

    profile_path = Path("data/learner-profile.json")

    # Check if learner has set up their profile
    if not profile_path.exists():
        print("[Fluent] 🌍 Welcome to Fluent - The AI Language Learning Kit!")
        print("[Fluent] 📝 Run /setup to create your personalized learning profile")
        sys.exit(0)

    # Load and display learner stats
    try:
        with open(profile_path, 'r') as f:
            profile = json.load(f)

        learner = profile.get("learner", {})
        stats = profile.get("stats", {})

        name = learner.get("name", "Learner")
        target_lang = learner.get("target_language", "your target language")
        current_level = learner.get("current_level", "...")
        target_level = learner.get("target_level", "...")
        streak = stats.get("streak_days", 0)

        print(f"[Fluent] 🌍 Welcome back, {name}!")
        print(f"[Fluent] 📚 Learning: {target_lang}")
        print(f"[Fluent] 🎯 Level: {current_level} → {target_level}")
        print(f"[Fluent] 🔥 Streak: {streak} days")

        # Check for due reviews (optional - requires spaced-repetition.json)
        sr_path = Path("data/spaced-repetition.json")
        if sr_path.exists():
            try:
                with open(sr_path, 'r') as f:
                    sr_data = json.load(f)

                today = datetime.now().strftime("%Y-%m-%d")
                due_count = 0

                for item in sr_data.get("items", []):
                    if item.get("next_review_date", "") <= today:
                        due_count += 1

                if due_count > 0:
                    print(f"[Fluent] 📅 {due_count} items due for review today - Run /review!")

            except Exception:
                pass  # Silently fail if SR data is malformed

    except Exception as e:
        print(f"[Fluent] Error loading profile: {e}", file=sys.stderr)

    sys.exit(0)

if __name__ == "__main__":
    main()
