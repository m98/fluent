#!/usr/bin/env python3
"""Select a diverse, deterministic set of due review items.

The selector is deliberately read-only. It accepts the JSON emitted by
read-db.py on stdin and prints a plan on stdout; it never mutates learner data.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple, Union


PRIORITY_RANK = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


@dataclass(frozen=True)
class Candidate:
    item_id: str
    item: Mapping[str, Any]
    concept_id: str


def _as_nonempty_string(value: Any) -> Optional[str]:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _parse_day(value: Any) -> Optional[date]:
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def load_concept_map(path: Optional[Union[str, Path]] = None) -> Dict[str, str]:
    """Load an optional item_id -> concept_id compatibility map."""
    if path is None:
        path = Path(__file__).resolve().parent.parent / "references" / "review-concepts.json"
    path = Path(path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    mapping = raw.get("item_concepts", raw) if isinstance(raw, dict) else {}
    if not isinstance(mapping, dict):
        return {}
    result: Dict[str, str] = {}
    for item_id, raw_concept in mapping.items():
        concept = _as_nonempty_string(raw_concept)
        if isinstance(item_id, str) and concept:
            result[item_id] = concept
    return result


def concept_key(
    item_id: str,
    item: Mapping[str, Any],
    concept_map: Optional[Mapping[str, str]] = None,
) -> str:
    """Resolve a stable concept key without guessing from fuzzy text."""
    explicit = _as_nonempty_string(item.get("concept_id"))
    if explicit:
        return explicit
    mapped = _as_nonempty_string((concept_map or {}).get(item_id))
    if mapped:
        return mapped
    # Legacy items remain fully supported, but are intentionally not merged.
    return f"legacy:{item_id}"


def _priority(item: Mapping[str, Any]) -> int:
    return PRIORITY_RANK.get(str(item.get("priority", "medium")).lower(), 2)


def item_sort_key(item_id: str, item: Mapping[str, Any], today: Optional[Union[str, date]] = None) -> Tuple[Any, ...]:
    """Sort critical/high items first, then older and less-mastered items."""
    today_day = _parse_day(today) if isinstance(today, str) else today
    due_day = _parse_day(item.get("due_date"))
    overdue = max(0, (today_day - due_day).days) if today_day and due_day else 0
    due_text = due_day.isoformat() if due_day else "9999-12-31"
    last_text = (
        _as_nonempty_string(item.get("last_reviewed"))
        or _as_nonempty_string(item.get("created_date"))
        or "9999-12-31"
    )
    try:
        mastery = int(item.get("mastery_level", 0))
    except (TypeError, ValueError):
        mastery = 0
    return (_priority(item), -overdue, due_text, mastery, last_text, item_id)


def _unique_ids(ids: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    result: List[str] = []
    for item_id in ids:
        if not isinstance(item_id, str) or item_id in seen:
            continue
        seen.add(item_id)
        result.append(item_id)
    return result


def _make_candidates(
    items: Mapping[str, Mapping[str, Any]],
    due_ids: Iterable[str],
    concept_map: Optional[Mapping[str, str]],
    today: Optional[Union[str, date]],
) -> List[Candidate]:
    candidates: List[Candidate] = []
    for item_id in _unique_ids(due_ids):
        item = items.get(item_id)
        if not isinstance(item, Mapping):
            continue
        candidates.append(Candidate(item_id, item, concept_key(item_id, item, concept_map)))
    return sorted(candidates, key=lambda c: item_sort_key(c.item_id, c.item, today))


def select_review_items(
    items: Mapping[str, Mapping[str, Any]],
    due_ids: Iterable[str],
    limit: int = 20,
    *,
    concept_map: Optional[Mapping[str, str]] = None,
    today: Optional[Union[str, date]] = None,
    max_per_concept: Optional[int] = None,
    variant_slots: int = 2,
) -> Dict[str, Any]:
    """Select due items by priority bands and concept round-robin.

    The first pass gives every concept at most one item. If there are fewer
    concepts than the limit, a second pass may select one additional item per
    concept. The result is deterministic and never repeats an item ID.
    """
    limit = max(0, int(limit))
    candidates = _make_candidates(items, due_ids, concept_map, today)
    reserve = min(max(0, int(variant_slots)), max(0, limit - 1))
    if len(candidates) <= limit:
        reserve = 0
    primary_limit = max(0, limit - reserve)
    buckets: Dict[str, List[Candidate]] = defaultdict(list)
    for candidate in candidates:
        buckets[candidate.concept_id].append(candidate)

    concept_order = sorted(
        buckets,
        key=lambda concept: item_sort_key(
            buckets[concept][0].item_id, buckets[concept][0].item, today
        ),
    )
    if max_per_concept is None:
        max_per_concept = 1 if len(concept_order) >= primary_limit and primary_limit else 2
    max_per_concept = max(0, int(max_per_concept))

    selected: List[Candidate] = []
    for round_number in range(max_per_concept):
        for concept in concept_order:
            if len(selected) >= primary_limit:
                break
            bucket = buckets[concept]
            if round_number < len(bucket):
                selected.append(bucket[round_number])
        if len(selected) >= primary_limit:
            break

    selected_ids = [candidate.item_id for candidate in selected]
    selected_set = set(selected_ids)
    omitted_candidates = [candidate for candidate in candidates if candidate.item_id not in selected_set]
    selected_concepts = {candidate.concept_id for candidate in selected}
    fill_candidates = [
        candidate for candidate in omitted_candidates
        if candidate.concept_id not in selected_concepts
    ]
    fill_candidates += [
        candidate for candidate in omitted_candidates
        if candidate.concept_id in selected_concepts
    ]
    reserved_candidates = fill_candidates[:reserve]
    reserved_ids = [candidate.item_id for candidate in reserved_candidates]
    reserved_set = set(reserved_ids)
    deferred_candidates = [
        candidate for candidate in omitted_candidates
        if candidate.item_id not in reserved_set
    ]
    deferred = [candidate.item_id for candidate in deferred_candidates]
    counts: Dict[str, int] = defaultdict(int)
    for candidate in selected:
        counts[candidate.concept_id] += 1
    variant_candidates = {
        candidate.item_id: [
            other.item_id
            for other in omitted_candidates
            if other.concept_id == candidate.concept_id
        ][:2]
        for candidate in selected
    }

    return {
        "selected_item_ids": selected_ids,
        "selected_items": [
            _public_item(candidate.item_id, candidate.item, candidate.concept_id)
            for candidate in selected
        ],
        "omitted_due_item_ids": deferred,
        "reserved_fill_item_ids": reserved_ids,
        "reserved_fill_items": [
            _public_item(candidate.item_id, candidate.item, candidate.concept_id)
            for candidate in reserved_candidates
        ],
        "deferred_items": [
            _public_item(candidate.item_id, candidate.item, candidate.concept_id)
            for candidate in deferred_candidates
        ],
        "selected_count": len(selected_ids),
        "unique_concepts": len({candidate.concept_id for candidate in selected}),
        "concept_counts": dict(counts),
        "variant_candidates": variant_candidates,
        "max_per_concept": max_per_concept,
        "variant_slots": len(reserved_candidates),
        "candidate_count": len(candidates),
    }


def _public_item(item_id: str, item: Mapping[str, Any], concept_id: str) -> Dict[str, Any]:
    """Keep selector output useful without copying review histories."""
    fields = (
        "type", "item_type", "content", "answer", "category", "difficulty",
        "priority", "due_date", "last_reviewed", "mastery_level", "concept_id",
    )
    result = {"id": item_id, "concept_id": concept_id}
    for field in fields:
        if field in item:
            result[field] = item[field]
    return result


def _public_pattern(pattern_id: str, pattern: Mapping[str, Any]) -> Dict[str, Any]:
    """Expose grading context without duplicating the full example history."""
    fields = ("category", "subcategory", "description", "severity", "frequency", "mastery_level", "notes")
    result = {"pattern_id": pattern_id}
    for field in fields:
        if field in pattern:
            result[field] = pattern[field]
    examples = pattern.get("examples")
    if isinstance(examples, list) and examples:
        result["latest_example"] = examples[-1]
    return result


def choose_variant(
    failed_item_id: str,
    items: Mapping[str, Mapping[str, Any]],
    deferred_ids: Iterable[str],
    *,
    seen_item_ids: Iterable[str] = (),
    concept_map: Optional[Mapping[str, str]] = None,
    today: Optional[Union[str, date]] = None,
) -> Optional[str]:
    """Return the best unasked item from the failed item's concept."""
    failed_item = items.get(failed_item_id)
    if not isinstance(failed_item, Mapping):
        return None
    failed_concept = concept_key(failed_item_id, failed_item, concept_map)
    seen = set(seen_item_ids)
    variants = [
        candidate
        for candidate in _make_candidates(items, deferred_ids, concept_map, today)
        if candidate.concept_id == failed_concept and candidate.item_id not in seen
    ]
    return variants[0].item_id if variants else None


def _read_input() -> Dict[str, Any]:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON input: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit("Input must be a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--today", default=None)
    parser.add_argument("--max-per-concept", type=int, default=None)
    parser.add_argument("--variant-slots", type=int, default=2)
    parser.add_argument("--concept-map", default=None)
    args = parser.parse_args()

    payload = _read_input()
    databases = payload.get("databases", {})
    sr = databases.get("spaced_repetition", {})
    items = sr.get("items", {})
    queue = sr.get("review_queue", {})
    computed = payload.get("computed", {})
    queue_ids = queue.get("today", []) if isinstance(queue, Mapping) else []
    due_from_computed = computed.get("due_review_items")
    # read-db recomputes due dates at invocation time; use it as the source so
    # items rolling over from yesterday's queue snapshot are not lost.
    due_ids = due_from_computed if isinstance(due_from_computed, list) else queue_ids
    daily_limit = sr.get("daily_limits", {}).get("review_items_per_day", 20)
    limit = args.limit if args.limit is not None else daily_limit
    today = args.today or computed.get("today")
    plan = select_review_items(
        items,
        due_ids,
        limit,
        concept_map=load_concept_map(args.concept_map),
        today=today,
        max_per_concept=args.max_per_concept,
        variant_slots=args.variant_slots,
    )
    plan["today"] = today
    plan["limit"] = max(0, int(limit))
    plan["learner"] = databases.get("learner_profile", {}).get("learner", {})
    plan["due_reviews_count"] = computed.get("due_reviews_count", len(due_ids))
    patterns = databases.get("mistakes_db", {}).get("error_patterns", {})
    if isinstance(patterns, Mapping):
        plan["selected_patterns"] = {
            item_id: _public_pattern(item_id, patterns[item_id])
            for item_id in plan["selected_item_ids"]
            if isinstance(patterns.get(item_id), Mapping)
        }
    else:
        plan["selected_patterns"] = {}
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
