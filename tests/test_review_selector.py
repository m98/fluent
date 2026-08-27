#!/usr/bin/env python3
"""Unit tests for the deterministic, concept-diverse review selector."""
import sys
import unittest
from datetime import date
from pathlib import Path

HOOKS = Path(__file__).resolve().parent.parent / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS))

from review_selector import choose_variant, concept_key, select_review_items  # noqa: E402


def make_item(item_id, concept_id=None, priority="medium", due_date="2026-08-27", mastery=0):
    item = {
        "id": item_id,
        "type": "error_pattern",
        "priority": priority,
        "due_date": due_date,
        "last_reviewed": "2026-08-26",
        "mastery_level": mastery,
    }
    if concept_id is not None:
        item["concept_id"] = concept_id
    return item


class ReviewSelectorTests(unittest.TestCase):
    def test_first_pass_covers_each_concept_before_variants(self):
        items = {}
        due = []
        for concept in "abcd":
            for suffix in "12":
                item_id = f"{concept}{suffix}"
                items[item_id] = make_item(item_id, concept)
                due.append(item_id)

        plan = select_review_items(items, due, limit=6, today="2026-08-27")

        self.assertEqual(plan["selected_item_ids"], ["a1", "b1", "c1", "d1"])
        self.assertEqual(plan["unique_concepts"], 4)
        self.assertEqual(plan["concept_counts"], {"a": 1, "b": 1, "c": 1, "d": 1})
        self.assertEqual(plan["variant_slots"], 2)
        self.assertEqual(plan["reserved_fill_item_ids"], ["a2", "b2"])
        self.assertEqual(plan["omitted_due_item_ids"], ["c2", "d2"])

    def test_priority_orders_concepts_without_starving_coverage(self):
        items = {
            "critical-a": make_item("critical-a", "a", priority="critical"),
            "high-b": make_item("high-b", "b", priority="high"),
            "medium-c": make_item("medium-c", "c", priority="medium"),
        }
        plan = select_review_items(items, items, limit=3, today="2026-08-27")

        self.assertEqual(plan["selected_item_ids"], ["critical-a", "high-b", "medium-c"])
        self.assertEqual(plan["unique_concepts"], 3)

    def test_concept_count_below_limit_allows_second_variant(self):
        items = {}
        due = []
        for n in range(3):
            concept = f"concept-{n}"
            for suffix in "12":
                item_id = f"{n}{suffix}"
                items[item_id] = make_item(item_id, concept)
                due.append(item_id)

        plan = select_review_items(items, due, limit=8, today="2026-08-27")

        self.assertEqual(plan["selected_count"], 6)
        self.assertEqual(plan["unique_concepts"], 3)
        self.assertTrue(all(count == 2 for count in plan["concept_counts"].values()))

    def test_does_not_reserve_slots_when_pool_fits_limit(self):
        items = {
            f"item-{n}": make_item(f"item-{n}", f"concept-{n}")
            for n in range(20)
        }
        plan = select_review_items(items, items, limit=20, today="2026-08-27")

        self.assertEqual(plan["selected_count"], 20)
        self.assertEqual(plan["variant_slots"], 0)
        self.assertEqual(plan["unique_concepts"], 20)
        self.assertEqual(plan["omitted_due_item_ids"], [])

    def test_reserves_two_slots_when_pool_exceeds_limit(self):
        items = {
            f"item-{n}": make_item(f"item-{n}", f"concept-{n}")
            for n in range(21)
        }
        plan = select_review_items(items, items, limit=20, today="2026-08-27")

        self.assertEqual(plan["selected_count"], 18)
        self.assertEqual(plan["variant_slots"], 2)
        self.assertEqual(plan["unique_concepts"], 18)
        self.assertEqual(len(plan["reserved_fill_item_ids"]), 2)
        self.assertEqual(len(plan["omitted_due_item_ids"]), 1)
        self.assertEqual(len(plan["deferred_items"]), 1)

    def test_small_candidate_set_does_not_reserve_empty_slots(self):
        items = {f"item-{n}": make_item(f"item-{n}", f"concept-{n}") for n in range(5)}
        plan = select_review_items(items, items, limit=20, today="2026-08-27")

        self.assertEqual(plan["selected_count"], 5)
        self.assertEqual(plan["variant_slots"], 0)
        self.assertEqual(plan["omitted_due_item_ids"], [])

    def test_nineteen_candidates_fit_without_reservation(self):
        items = {f"item-{n}": make_item(f"item-{n}", f"concept-{n}") for n in range(19)}
        plan = select_review_items(items, items, limit=20, today="2026-08-27")

        self.assertEqual(plan["selected_count"], 19)
        self.assertEqual(plan["variant_slots"], 0)
        self.assertEqual(plan["omitted_due_item_ids"], [])

    def test_small_limit_still_reserves_up_to_two_slots(self):
        items = {f"item-{n}": make_item(f"item-{n}", f"concept-{n}") for n in range(6)}
        plan = select_review_items(items, items, limit=5, today="2026-08-27")

        self.assertEqual(plan["selected_count"], 3)
        self.assertEqual(plan["variant_slots"], 2)
        self.assertEqual(len(plan["reserved_fill_item_ids"]), 2)
        self.assertEqual(len(plan["omitted_due_item_ids"]), 1)

    def test_selected_items_include_grading_context(self):
        items = {"item": make_item("item", "concept")}
        items["item"].update({"content": "wrong", "answer": "right", "category": "grammar"})
        plan = select_review_items(items, items, limit=20, today="2026-08-27")

        self.assertEqual(plan["selected_items"][0]["id"], "item")
        self.assertEqual(plan["selected_items"][0]["content"], "wrong")
        self.assertEqual(plan["selected_items"][0]["answer"], "right")

    def test_legacy_items_are_not_fuzzy_merged(self):
        one = make_item("while-a")
        two = make_item("wait-a")

        self.assertEqual(concept_key("while-a", one), "legacy:while-a")
        self.assertEqual(concept_key("wait-a", two), "legacy:wait-a")

    def test_explicit_concept_wins_over_compatibility_map(self):
        item = make_item("item", "explicit:concept")
        self.assertEqual(
            concept_key("item", item, {"item": "mapped:concept"}),
            "explicit:concept",
        )

    def test_selector_is_deterministic_with_duplicate_input_ids(self):
        items = {
            "a": make_item("a", "a"),
            "b": make_item("b", "b"),
        }
        plan = select_review_items(items, ["b", "a", "a"], limit=10, today="2026-08-27")

        self.assertEqual(plan["selected_item_ids"], ["a", "b"])
        self.assertEqual(len(plan["selected_item_ids"]), len(set(plan["selected_item_ids"])))

    def test_choose_variant_requires_same_concept_and_unasked_item(self):
        items = {
            "failed": make_item("failed", "time:waiting", priority="critical"),
            "variant": make_item("variant", "time:waiting", priority="high"),
            "other": make_item("other", "time:until", priority="critical"),
        }
        self.assertEqual(
            choose_variant(
                "failed",
                items,
                ["variant", "other"],
                seen_item_ids=["failed"],
                today="2026-08-27",
            ),
            "variant",
        )
        self.assertIsNone(
            choose_variant(
                "failed",
                items,
                ["variant"],
                seen_item_ids=["failed", "variant"],
                today="2026-08-27",
            )
        )

    def test_invalid_due_items_are_ignored(self):
        items = {"good": make_item("good", "good")}
        plan = select_review_items(items, ["missing", "good"], limit=20, today=date(2026, 8, 27))
        self.assertEqual(plan["selected_item_ids"], ["good"])
        self.assertEqual(plan["candidate_count"], 1)


if __name__ == "__main__":
    unittest.main()
