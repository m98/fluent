#!/usr/bin/env python3
"""
Fluent DB Reader Script
Loads all 6 learning databases and outputs a single JSON object to stdout.

Usage:
    python3 .claude/hooks/read-db.py

Exit codes: 0=success, 1=partial (some files missing), 2=critical error
"""
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path("data")

FILES = {
    "learner_profile": DATA_DIR / "learner-profile.json",
    "progress_db": DATA_DIR / "progress-db.json",
    "mistakes_db": DATA_DIR / "mistakes-db.json",
    "mastery_db": DATA_DIR / "mastery-db.json",
    "spaced_repetition": DATA_DIR / "spaced-repetition.json",
    "session_log": DATA_DIR / "session-log.json",
}


def load_json(path: Path):
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def next_session_id(sessions: list) -> str:
    """Produce 'session-NNN' matching existing id convention.
    Falls back to 'session-001' on empty log or unparseable last id."""
    if not sessions:
        return "session-001"
    last_id = sessions[-1].get("session_id", "")
    m = re.search(r'(\d+)', last_id)
    if m:
        return f"session-{int(m.group(1)) + 1:03d}"
    return f"session-{len(sessions) + 1:03d}"


def main():
    databases = {}
    missing = []

    for key, path in FILES.items():
        data = load_json(path)
        if data is None:
            missing.append(str(path))
            databases[key] = {}
        else:
            databases[key] = data

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    sr = databases.get("spaced_repetition", {})
    items = sr.get("items", {})
    due_items = [iid for iid, item in items.items() if item.get("due_date", "") <= today]

    log = databases.get("session_log", {})
    sessions = log.get("sessions", [])

    profile = databases.get("learner_profile", {})
    last_updated = profile.get("last_updated", "")
    streak_active = last_updated in (today, yesterday)
    try:
        days_since = (now - datetime.strptime(last_updated, "%Y-%m-%d")).days if last_updated else None
    except ValueError:
        days_since = None

    result = {
        "databases": databases,
        "computed": {
            "today": today,
            "due_reviews_count": len(due_items),
            "due_review_items": due_items,
            "next_session_id": next_session_id(sessions),
            "streak_active": streak_active,
            "days_since_last_session": days_since,
        },
    }

    if missing:
        result["_warnings"] = [f"Missing file: {m}" for m in missing]

    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    print()

    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
