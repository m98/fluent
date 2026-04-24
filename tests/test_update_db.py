#!/usr/bin/env python3
"""
Smoke test for .claude/hooks/update-db.py.

Runs the script against a fresh fixture DB in a temp dir, feeds it a sample
session report, and asserts schema invariants on the output files.

Usage:
    python3 tests/test_update_db.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / ".claude" / "hooks" / "update-db.py"


def make_fixtures(data_dir: Path):
    (data_dir / "learner-profile.json").write_text(json.dumps({
        "learner": {"name": "Test", "target_language": "Dutch",
                    "current_level": "A1", "target_level": "A2"},
        "profile_created": "2026-04-20",
        "last_updated": "2026-04-23",
        "current_streak_days": 2,
        "total_sessions": 1,
        "total_study_minutes": 10,
        "skills": {
            "vocabulary": {"current_level": 1, "confidence": 60,
                           "last_practiced": "2026-04-23",
                           "total_practice_time": 10}
        },
        "focus_areas": [],
        "achievements": [],
        "preferences": {}
    }))
    (data_dir / "progress-db.json").write_text(json.dumps({
        "metadata": {"last_updated": "2026-04-23", "language": "Dutch",
                     "tracking_started": "2026-04-20"},
        "overall_stats": {"total_sessions": 1, "total_exercises": 4,
                          "total_correct": 3, "total_incorrect": 1,
                          "accuracy_rate": 0.75,
                          "total_study_minutes": 10,
                          "average_session_duration": 10},
        "accuracy_trend": [{"date": "2026-04-23", "accuracy": 0.75,
                            "exercises": 4}],
        "skill_progress": {
            "vocabulary": {"sessions": 1, "accuracy": 0.75,
                           "last_practiced": "2026-04-23",
                           "exercises_completed": 4, "correct_count": 3,
                           "incorrect_count": 1}
        },
        "weekly_summary": []
    }))
    (data_dir / "mistakes-db.json").write_text(json.dumps({
        "metadata": {"last_updated": "2026-04-23",
                     "total_patterns_tracked": 0, "language": "Dutch"},
        "error_patterns": {}
    }))
    (data_dir / "mastery-db.json").write_text(json.dumps({
        "metadata": {"last_updated": "2026-04-23", "language": "Dutch"},
        "skills": {
            "vocabulary": {"mastery_level": 1, "confidence_score": 0.75,
                           "total_practice_time": 10,
                           "last_practiced": "2026-04-23",
                           "practice_count": 4, "avg_accuracy": 0.75}
        },
        "patterns": {}
    }))
    (data_dir / "spaced-repetition.json").write_text(json.dumps({
        "metadata": {"algorithm": "SM-2", "last_updated": "2026-04-23",
                     "total_items_tracked": 1, "language": "Dutch"},
        "review_queue": {"today": [], "tomorrow": ["vocab_dag"],
                         "this_week": [], "later": []},
        "items": {
            "vocab_dag": {
                "id": "vocab_dag", "type": "vocabulary", "content": "dag",
                "answer": "day / hi-bye", "category": "greetings",
                "difficulty": "A1", "created_date": "2026-04-23",
                "due_date": "2026-04-24", "interval_days": 1,
                "repetitions": 1, "easiness_factor": 2.5,
                "consecutive_correct": 1, "consecutive_incorrect": 0,
                "last_reviewed": "2026-04-23", "last_quality": 4,
                "mastery_level": 1, "total_reviews": 1, "priority": "medium"
            }
        }
    }))
    (data_dir / "session-log.json").write_text(json.dumps({
        "metadata": {"language": "Dutch", "learner_name": "Test",
                     "total_sessions": 1},
        "sessions": [{
            "session_id": "session-001", "date": "2026-04-23",
            "duration_minutes": 10,
            "skills_practiced": ["vocabulary"],
            "exercises_completed": 4, "accuracy": 0.75,
            "score_breakdown": {"vocabulary": 0.75},
            "topics_covered": [], "breakthroughs": [],
            "focus_next_session": [], "notes": "",
            "achievements_earned": []
        }],
        "milestones": []
    }))


SESSION_PAYLOAD = {
    "session_id": "session-002",
    "date": "2026-04-24",
    "duration_minutes": 15,
    "command_used": "/learn",
    "skills_practiced": ["vocabulary"],
    "skill_scores": {
        "vocabulary": {"exercises": 5, "correct": 4, "time_minutes": 15}
    },
    "errors": [{
        "pattern_id": "verb_spreek",
        "category": "grammar",
        "subcategory": "verb_conjugation",
        "your_answer": "Hij spreek",
        "correct_answer": "Hij spreekt",
        "context": "3rd person",
        "severity": "critical",
        "difficulty_score": 0.7
    }],
    "new_vocabulary": [{
        "item_id": "het_huis",
        "item_type": "vocabulary",
        "content": "het huis",
        "answer": "the house",
        "category": "nouns",
        "difficulty": "A1",
        "initial_quality": 4
    }],
    "review_results": [{"item_id": "vocab_dag", "quality": 5}],
    "topics_covered": ["house_vocab"],
    "breakthroughs": ["Got 'het huis' on first try"],
    "focus_next_session": ["de/het drill"],
    "session_notes": "Good session.",
    "milestones": []
}


class UpdateDbSmokeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fluent-test-"))
        (self.tmp / "data").mkdir()
        make_fixtures(self.tmp / "data")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, payload: dict):
        proc = subprocess.run(
            ["python3", str(SCRIPT)],
            input=json.dumps(payload).encode(),
            cwd=str(self.tmp),
            capture_output=True,
        )
        return proc

    def test_happy_path(self):
        proc = self._run(SESSION_PAYLOAD)
        self.assertEqual(proc.returncode, 0,
                         msg=f"stdout={proc.stdout!r} stderr={proc.stderr!r}")

        with open(self.tmp / "data" / "session-log.json") as f:
            log = json.load(f)
        latest = log["sessions"][-1]
        self.assertEqual(latest["session_id"], "session-002")
        self.assertIn("skills_practiced", latest)
        self.assertIsInstance(latest["skills_practiced"], list)
        self.assertIn("score_breakdown", latest)
        self.assertIn("topics_covered", latest)
        self.assertIn("breakthroughs", latest)
        self.assertIn("focus_next_session", latest)
        self.assertIn("achievements_earned", latest)
        self.assertEqual(latest["streak_day"], 3)  # was 2, yesterday -> +1

        with open(self.tmp / "data" / "learner-profile.json") as f:
            profile = json.load(f)
        self.assertEqual(profile["current_streak_days"], 3)
        conf = profile["skills"]["vocabulary"]["confidence"]
        self.assertIsInstance(conf, int)
        self.assertGreaterEqual(conf, 0)
        self.assertLessEqual(conf, 100)

        with open(self.tmp / "data" / "spaced-repetition.json") as f:
            sr = json.load(f)
        dag = sr["items"]["vocab_dag"]
        # Schema preserved
        for k in ("consecutive_correct", "consecutive_incorrect",
                  "mastery_level", "total_reviews", "priority",
                  "content", "answer", "category", "difficulty"):
            self.assertIn(k, dag, f"lost field {k} on vocab_dag")
        self.assertEqual(dag["total_reviews"], 2)  # was 1, +1 review
        self.assertEqual(dag["last_quality"], 5)

        # New vocabulary item fully populated
        huis = sr["items"]["het_huis"]
        for k in ("id", "type", "content", "answer", "category",
                  "difficulty", "due_date", "interval_days", "repetitions",
                  "easiness_factor", "consecutive_correct",
                  "consecutive_incorrect", "mastery_level",
                  "total_reviews", "priority"):
            self.assertIn(k, huis, f"new item missing {k}")

        with open(self.tmp / "data" / "mistakes-db.json") as f:
            mistakes = json.load(f)
        self.assertIn("verb_spreek", mistakes["error_patterns"])
        pat = mistakes["error_patterns"]["verb_spreek"]
        self.assertEqual(pat["consecutive_incorrect"], 1)
        self.assertEqual(pat["examples"][-1]["incorrect"], "Hij spreek")
        self.assertEqual(pat["examples"][-1]["correct"], "Hij spreekt")

        # Backup directory exists
        backup = self.tmp / ".backups" / "pre-update-session-002"
        self.assertTrue(backup.exists(), "pre-update backup missing")

    def test_missing_required_field_exits_1(self):
        proc = self._run({"date": "2026-04-24"})  # no session_id
        self.assertEqual(proc.returncode, 1)

    def test_same_day_does_not_bump_streak(self):
        # Profile last_updated = 2026-04-23; send a session on 2026-04-23.
        payload = dict(SESSION_PAYLOAD)
        payload["session_id"] = "session-003"
        payload["date"] = "2026-04-23"
        proc = self._run(payload)
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        with open(self.tmp / "data" / "learner-profile.json") as f:
            profile = json.load(f)
        self.assertEqual(profile["current_streak_days"], 2)


if __name__ == "__main__":
    unittest.main()
