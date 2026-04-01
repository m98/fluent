#!/usr/bin/env python3
"""
Fluent DB Update Script
Updates all 6 learning databases from a single JSON session report via stdin.

Usage:
    python3 .claude/hooks/update-db.py <<'EOF'
    { "session_id": "002", "date": "2026-04-02", ... }
    EOF

Exit codes: 0=success, 1=validation error, 2=blocking/data error
"""
import json
import sys
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path("data")
BACKUP_DIR = Path(".backups")

# --- Utility functions ---

def load_json(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path: Path, data: dict):
    tmp_path = path.with_suffix('.json.tmp')
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.rename(str(tmp_path), str(path))


def date_str(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")


def parse_date(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d")


def tomorrow(today_str: str) -> str:
    return date_str(parse_date(today_str) + timedelta(days=1))


def yesterday(today_str: str) -> str:
    return date_str(parse_date(today_str) - timedelta(days=1))


def date_plus_days(today_str: str, days: int) -> str:
    return date_str(parse_date(today_str) + timedelta(days=days))


def get_week_start(today_str: str) -> str:
    d = parse_date(today_str)
    monday = d - timedelta(days=d.weekday())
    return date_str(monday)


def backup_all(tag: str):
    backup_path = BACKUP_DIR / tag
    backup_path.mkdir(parents=True, exist_ok=True)
    for f in DATA_DIR.glob("*.json"):
        shutil.copy2(f, backup_path / f.name)


# --- SM-2 Algorithm ---

def calculate_sm2(item: dict, quality: int) -> dict:
    ef = item.get("easiness_factor", 2.5)
    interval = item.get("interval_days", 1)
    reps = item.get("repetitions", 0)

    if quality >= 3:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = round(interval * ef)
        reps += 1
    else:
        reps = 0
        interval = 1

    ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    ef = max(1.3, ef)

    return {
        "easiness_factor": round(ef, 2),
        "interval_days": interval,
        "repetitions": reps,
    }


# --- Updater functions ---

def update_learner_profile(profile: dict, session: dict):
    today = session["date"]
    last = profile.get("last_updated", "")

    if last == yesterday(today):
        profile["current_streak_days"] = profile.get("current_streak_days", 0) + 1
    elif last != today:
        profile["current_streak_days"] = 1

    profile["last_updated"] = today
    profile["total_sessions"] = profile.get("total_sessions", 0) + 1
    profile["total_study_minutes"] = profile.get("total_study_minutes", 0) + session.get("duration_minutes", 0)

    for skill, scores in session.get("skill_scores", {}).items():
        if skill in profile.get("skills", {}):
            s = profile["skills"][skill]
            s["last_practiced"] = today
            s["total_practice_time"] = s.get("total_practice_time", 0) + scores.get("time_minutes", 0)
            if scores.get("exercises", 0) > 0:
                new_acc = scores["correct"] / scores["exercises"]
                old_conf = s.get("confidence", 0)
                s["confidence"] = round(old_conf * 0.7 + new_acc * 0.3, 2)
            s["current_level"] = max(s.get("current_level", 0), 1)

    if session.get("focus_areas"):
        profile["focus_areas"] = session["focus_areas"]

    for ms in session.get("milestones", []):
        profile.setdefault("achievements", []).append({
            "id": f"session_{session['session_id']}_{ms[:20].lower().replace(' ', '_')}",
            "name": ms,
            "earned_date": today,
            "description": ms,
        })


def update_progress_db(progress: dict, session: dict):
    today = session["date"]
    skill_scores = session.get("skill_scores", {})
    total_ex = sum(s.get("exercises", 0) for s in skill_scores.values())
    total_cor = sum(s.get("correct", 0) for s in skill_scores.values())
    accuracy = round(total_cor / total_ex, 2) if total_ex > 0 else 0.0

    stats = progress["overall_stats"]
    stats["total_sessions"] = stats.get("total_sessions", 0) + 1
    stats["total_exercises"] = stats.get("total_exercises", 0) + total_ex
    stats["total_correct"] = stats.get("total_correct", 0) + total_cor
    stats["total_incorrect"] = stats.get("total_incorrect", 0) + (total_ex - total_cor)
    stats["accuracy_rate"] = round(stats["total_correct"] / stats["total_exercises"], 2) if stats["total_exercises"] > 0 else 0.0
    stats["total_study_minutes"] = stats.get("total_study_minutes", 0) + session.get("duration_minutes", 0)
    stats["average_session_duration"] = round(stats["total_study_minutes"] / stats["total_sessions"])

    progress.setdefault("accuracy_trend", []).append({
        "date": today,
        "accuracy": accuracy,
        "exercises": total_ex,
    })

    for skill, scores in skill_scores.items():
        sp = progress.setdefault("skill_progress", {}).setdefault(skill, {
            "sessions": 0, "accuracy": 0.0, "last_practiced": None
        })
        old_sessions = sp["sessions"]
        sp["sessions"] += 1
        new_acc = scores["correct"] / scores["exercises"] if scores.get("exercises", 0) > 0 else 0.0
        sp["accuracy"] = round(
            (sp["accuracy"] * old_sessions + new_acc) / sp["sessions"], 2
        )
        sp["last_practiced"] = today

    week_start = get_week_start(today)
    weekly = progress.setdefault("weekly_summary", [])
    week_entry = None
    for w in weekly:
        if w["week_start"] == week_start:
            week_entry = w
            break
    if week_entry is None:
        week_entry = {"week_start": week_start, "sessions": 0, "total_minutes": 0, "accuracy": 0.0}
        weekly.append(week_entry)

    old_s = week_entry["sessions"]
    week_entry["sessions"] += 1
    week_entry["total_minutes"] += session.get("duration_minutes", 0)
    week_entry["accuracy"] = round(
        (week_entry["accuracy"] * old_s + accuracy) / week_entry["sessions"], 2
    )

    progress["metadata"]["last_updated"] = today


def update_mistakes_db(mistakes: dict, session: dict):
    today = session["date"]

    for error in session.get("errors", []):
        pid = error["pattern_id"]
        patterns = mistakes.setdefault("error_patterns", {})

        if pid in patterns:
            pat = patterns[pid]
            pat["frequency"] = pat.get("frequency", 0) + 1
            pat["last_occurred"] = today
            pat["next_review"] = tomorrow(today)
            pat.setdefault("examples", []).append({
                "your_answer": error.get("your_answer", ""),
                "correct_answer": error.get("correct_answer", ""),
                "context": error.get("context", ""),
                "date": today,
            })
            pat["examples"] = pat["examples"][-5:]
            if error.get("notes"):
                pat["notes"] = error["notes"]
        else:
            patterns[pid] = {
                "category": error.get("category", "other"),
                "subcategory": error.get("subcategory", ""),
                "frequency": 1,
                "mastery_level": 0,
                "difficulty_score": error.get("difficulty_score", 0.5),
                "last_occurred": today,
                "next_review": tomorrow(today),
                "examples": [{
                    "your_answer": error.get("your_answer", ""),
                    "correct_answer": error.get("correct_answer", ""),
                    "context": error.get("context", ""),
                    "date": today,
                }],
                "notes": error.get("notes", ""),
            }

    mistakes["metadata"]["last_updated"] = today
    mistakes["metadata"]["total_patterns_tracked"] = len(mistakes.get("error_patterns", {}))


def update_mastery_db(mastery: dict, session: dict, progress: dict):
    today = session["date"]

    for skill, scores in session.get("skill_scores", {}).items():
        s = mastery.setdefault("skills", {}).setdefault(skill, {
            "mastery_level": 0, "confidence_score": 0.0,
            "total_practice_time": 0, "last_practiced": None,
        })
        s["last_practiced"] = today
        s["total_practice_time"] = s.get("total_practice_time", 0) + scores.get("time_minutes", 0)

        sp = progress.get("skill_progress", {}).get(skill, {})
        acc = sp.get("accuracy", 0)
        sessions = sp.get("sessions", 0)
        s["confidence_score"] = round(acc, 2)

        if sessions == 0:
            s["mastery_level"] = 0
        elif sessions < 3 or acc < 0.5:
            s["mastery_level"] = max(s.get("mastery_level", 0), 1)
        elif sessions < 5 or acc < 0.65:
            s["mastery_level"] = max(s.get("mastery_level", 0), 2)
        elif sessions < 10 or acc < 0.8:
            s["mastery_level"] = max(s.get("mastery_level", 0), 3)
        elif sessions < 20 or acc < 0.9:
            s["mastery_level"] = max(s.get("mastery_level", 0), 4)
        else:
            s["mastery_level"] = 5

    mastery["metadata"]["last_updated"] = today


def update_spaced_repetition(sr: dict, session: dict):
    today = session["date"]

    for review in session.get("review_results", []):
        item_id = review["item_id"]
        quality = review["quality"]
        if item_id in sr.get("items", {}):
            item = sr["items"][item_id]
            result = calculate_sm2(item, quality)
            item["easiness_factor"] = result["easiness_factor"]
            item["interval_days"] = result["interval_days"]
            item["repetitions"] = result["repetitions"]
            item["due_date"] = date_plus_days(today, result["interval_days"])
            item["last_reviewed"] = today
            item.setdefault("review_history", []).append({
                "date": today,
                "quality": quality,
                "score": review.get("score", 0),
            })

    for vocab in session.get("new_vocabulary", []):
        item_id = vocab["item_id"]
        if item_id not in sr.get("items", {}):
            sr.setdefault("items", {})[item_id] = {
                "item_id": item_id,
                "item_type": vocab.get("item_type", "vocabulary"),
                "easiness_factor": 2.5,
                "interval_days": 1,
                "repetitions": 0,
                "due_date": tomorrow(today),
                "last_reviewed": today,
                "review_history": [{
                    "date": today,
                    "quality": vocab.get("initial_quality", 3),
                    "score": 0,
                }],
            }

    for error in session.get("errors", []):
        item_id = error["pattern_id"]
        if item_id not in sr.get("items", {}):
            sr.setdefault("items", {})[item_id] = {
                "item_id": item_id,
                "item_type": "error_pattern",
                "easiness_factor": 2.5,
                "interval_days": 1,
                "repetitions": 0,
                "due_date": tomorrow(today),
                "last_reviewed": today,
                "review_history": [{
                    "date": today,
                    "quality": 2,
                    "score": 0,
                }],
            }

    # Rebuild review queue
    sr["review_queue"] = {"today": [], "tomorrow": [], "this_week": [], "later": []}
    tom = tomorrow(today)
    week_end = date_plus_days(today, 7)
    for item_id, item in sr.get("items", {}).items():
        due = item.get("due_date", today)
        if due <= today:
            sr["review_queue"]["today"].append(item_id)
        elif due == tom:
            sr["review_queue"]["tomorrow"].append(item_id)
        elif due <= week_end:
            sr["review_queue"]["this_week"].append(item_id)
        else:
            sr["review_queue"]["later"].append(item_id)

    sr["metadata"]["last_updated"] = today
    sr["metadata"]["total_items_tracked"] = len(sr.get("items", {}))


def update_session_log(log: dict, session: dict, streak: int):
    today = session["date"]
    skill_scores = session.get("skill_scores", {})
    total_ex = sum(s.get("exercises", 0) for s in skill_scores.values())
    total_cor = sum(s.get("correct", 0) for s in skill_scores.values())

    log.setdefault("sessions", []).append({
        "session_id": session["session_id"],
        "date": today,
        "duration_minutes": session.get("duration_minutes", 0),
        "skill_practiced": session.get("skill_practiced", "mixed"),
        "command_used": session.get("command_used", "/learn"),
        "exercises_completed": total_ex,
        "exercises_correct": total_cor,
        "exercises_incorrect": total_ex - total_cor,
        "accuracy": round(total_cor / total_ex, 2) if total_ex > 0 else 0.0,
        "focus_areas": session.get("focus_areas", []),
        "new_patterns_encountered": [e["pattern_id"] for e in session.get("errors", [])],
        "mastered_this_session": [],
        "notes": session.get("session_notes", ""),
        "streak_day": streak,
    })

    for ms in session.get("milestones", []):
        log.setdefault("milestones", []).append({
            "date": today,
            "milestone": ms,
            "session_id": session["session_id"],
        })

    log["metadata"]["total_sessions"] = len(log["sessions"])


# --- Main ---

def main():
    try:
        session = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"[Fluent] Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required fields
    for field in ("session_id", "date"):
        if field not in session:
            print(f"[Fluent] Error: Missing required field '{field}'", file=sys.stderr)
            sys.exit(1)

    session.setdefault("duration_minutes", 0)

    # Load all databases
    files = {
        "profile": DATA_DIR / "learner-profile.json",
        "progress": DATA_DIR / "progress-db.json",
        "mistakes": DATA_DIR / "mistakes-db.json",
        "mastery": DATA_DIR / "mastery-db.json",
        "sr": DATA_DIR / "spaced-repetition.json",
        "log": DATA_DIR / "session-log.json",
    }

    try:
        data = {k: load_json(p) for k, p in files.items()}
    except Exception as e:
        print(f"[Fluent] Error loading databases: {e}", file=sys.stderr)
        sys.exit(2)

    # Backup before changes
    backup_all(f"pre-update-{session['session_id']}")

    # Run all updaters
    try:
        update_learner_profile(data["profile"], session)
        update_progress_db(data["progress"], session)
        update_mistakes_db(data["mistakes"], session)
        update_mastery_db(data["mastery"], session, data["progress"])
        update_spaced_repetition(data["sr"], session)
        streak = data["profile"].get("current_streak_days", 0)
        update_session_log(data["log"], session, streak)
    except Exception as e:
        print(f"[Fluent] Error updating databases: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(2)

    # Save all atomically
    try:
        for k, p in files.items():
            save_json(p, data[k])
    except Exception as e:
        print(f"[Fluent] Error saving databases: {e}", file=sys.stderr)
        sys.exit(2)

    # Summary output
    stats = data["progress"]["overall_stats"]
    sr_tomorrow = len(data["sr"]["review_queue"].get("tomorrow", []))
    skill_scores = session.get("skill_scores", {})
    total_ex = sum(s.get("exercises", 0) for s in skill_scores.values())
    total_cor = sum(s.get("correct", 0) for s in skill_scores.values())

    print(f"[Fluent] ✅ Updated 6 databases for session {session['session_id']}")
    print(f"[Fluent] 🔥 Streak: {streak} days | Sessions: {stats['total_sessions']} | Minutes: {stats['total_study_minutes']}")
    print(f"[Fluent] 📊 This session: {total_cor}/{total_ex} correct ({round(total_cor/total_ex*100)}%)" if total_ex > 0 else "[Fluent] 📊 No exercises recorded")
    print(f"[Fluent] 📈 Overall accuracy: {stats['accuracy_rate']*100:.0f}% ({stats['total_exercises']} exercises)")
    print(f"[Fluent] 🧠 SR: {data['sr']['metadata']['total_items_tracked']} items tracked, {sr_tomorrow} due tomorrow")
    print(f"[Fluent] 📝 Errors tracked: {data['mistakes']['metadata']['total_patterns_tracked']} patterns")

    sys.exit(0)


if __name__ == "__main__":
    main()
