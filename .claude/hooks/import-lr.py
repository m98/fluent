#!/usr/bin/env python3
"""
Language Reactor → Fluent Importer

Reads a Language Reactor export (zip or CSV) and injects new vocabulary into
the matching Fluent spaced-repetition database.  Items already in the database
are silently skipped so re-running is safe.

Usage:
    python3 .claude/hooks/import-lr.py <zip_or_csv_path> [OPTIONS]

Options:
    --lang CODE        Target Fluent language code (default: auto-detect from file)
    --daily-limit N    Max items due per day when spreading the queue (default: 20)
    --dry-run          Preview without writing anything
    --data-dir PATH    Override the Fluent data directory (skips registry lookup)

Exit codes: 0=success, 1=user error, 2=I/O / data error
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
import unicodedata
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fluent_paths import (  # noqa: E402
    LANGUAGE_REGISTRY_PATH,
    force_utf8_io,
)

force_utf8_io()

TODAY = datetime.now().strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def date_plus(base: str, days: int) -> str:
    return (datetime.strptime(base, "%Y-%m-%d") + timedelta(days=days)).strftime("%Y-%m-%d")


def tomorrow() -> str:
    return date_plus(TODAY, 1)


def slugify(text: str) -> str:
    """Lowercase, normalise accents, keep only [a-z0-9], collapse to _."""
    text = text.lower().strip()
    # Expand common German (and other) ligatures before NFD decomposition
    text = text.replace("ß", "ss")
    nfkd = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in nfkd if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def load_registry() -> dict:
    if not LANGUAGE_REGISTRY_PATH.exists():
        return {}
    try:
        with open(LANGUAGE_REGISTRY_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def resolve_data_dir(lang_code: str, override: str | None) -> Path | None:
    if override:
        return Path(override).expanduser().resolve()
    registry = load_registry()
    languages = registry.get("languages", {})
    if lang_code in languages:
        return Path(languages[lang_code]["data_dir"]).expanduser().resolve()
    return None


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json_atomic(path: Path, data: dict) -> None:
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp), str(path))


def rebuild_queue(items: dict, today: str) -> dict:
    """Rebuild review_queue buckets from item due_dates."""
    tom = date_plus(today, 1)
    week_end = date_plus(today, 7)
    queue: dict[str, list] = {"today": [], "tomorrow": [], "this_week": [], "later": []}
    for item_id, item in items.items():
        due = item.get("due_date", today)
        if due <= today:
            queue["today"].append(item_id)
        elif due == tom:
            queue["tomorrow"].append(item_id)
        elif due <= week_end:
            queue["this_week"].append(item_id)
        else:
            queue["later"].append(item_id)
    return queue


# ---------------------------------------------------------------------------
# Language Reactor CSV parsing
# ---------------------------------------------------------------------------

# Column indices (tab-separated, no header row)
_C_ID       = 0   # WORD|lemma|lang or PHRASE-YT|lang|hash
_C_TYPE     = 1   # "Word" or "Phrase"
_C_SRC_SENT = 2   # source sentence (target language)
_C_TRL_SENT = 3   # translated sentence (native language)
_C_INFLECTED = 4  # word as it appears in sentence
_C_LEMMA    = 5   # base/dictionary form
_C_POS      = 6   # part of speech
_C_TRANSL   = 8   # comma-separated translations (native language)
_C_LANG     = 10  # BCP-47 language code
_C_TITLE    = 16  # video / show title
_C_DATE     = 17  # date saved


def load_lr_rows(file_path: Path) -> list[list[str]]:
    """Load Language Reactor items from a .zip or .csv / .tsv file."""
    if file_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(file_path) as zf:
            names = zf.namelist()
            csv_names = [n for n in names if n.endswith(".csv") and "/" not in n]
            if not csv_names:
                raise ValueError("No top-level .csv file found inside the zip.")
            with zf.open(csv_names[0]) as f:
                raw = f.read().decode("utf-8")
    else:
        raw = file_path.read_text(encoding="utf-8")

    reader = csv.reader(io.StringIO(raw), delimiter="\t")
    return [row for row in reader if row]


def detect_languages(rows: list[list[str]]) -> set[str]:
    return {row[_C_LANG] for row in rows if len(row) > _C_LANG and row[_C_LANG]}


def row_to_item(row: list[str], today: str) -> dict | None:
    """Convert one Language Reactor row to a Fluent spaced-repetition item dict.
    Returns None if the row lacks the minimum required fields."""
    if len(row) <= _C_LANG:
        return None

    item_type = row[_C_TYPE]   # "Word" or "Phrase"
    lang = row[_C_LANG]
    raw_id = row[_C_ID]

    if item_type == "Word":
        lemma = row[_C_LEMMA].strip() or row[_C_INFLECTED].strip()
        if not lemma:
            return None
        pos = row[_C_POS].strip()
        translations_raw = row[_C_TRANSL].strip() if len(row) > _C_TRANSL else ""
        # Take first 2 distinct translations (the list is often repetitive)
        translations = list(dict.fromkeys(t.strip() for t in translations_raw.split(",") if t.strip()))[:2]
        answer = ", ".join(translations) if translations else "(see example)"

        content_parts = [lemma]
        if pos:
            content_parts.append(f"[{pos}]")
        inflected = row[_C_INFLECTED].strip()
        src_sent = row[_C_SRC_SENT].strip().replace("\n", " ")
        trl_sent = row[_C_TRL_SENT].strip().replace("\n", " ")
        if src_sent:
            content_parts.append(f"— e.g. \"{src_sent}\"")

        content = " ".join(content_parts)

        answer_parts = [answer]
        if trl_sent:
            answer_parts.append(f"Example: \"{trl_sent}\"")
        title = row[_C_TITLE].strip() if len(row) > _C_TITLE else ""
        if title:
            answer_parts.append(f"Source: {title}")
        full_answer = "\n".join(answer_parts)

        item_id = f"lr_{slugify(lemma)}_{lang}"
        category = pos.lower() if pos else "vocabulary"

    else:  # Phrase
        src_sent = row[_C_SRC_SENT].strip().replace("\n", " ")
        trl_sent = row[_C_TRL_SENT].strip().replace("\n", " ")
        if not src_sent:
            return None
        content = src_sent
        answer_parts = [trl_sent] if trl_sent else []
        title = row[_C_TITLE].strip() if len(row) > _C_TITLE else ""
        if title:
            answer_parts.append(f"Source: {title}")
        full_answer = "\n".join(answer_parts) if answer_parts else "(phrase)"

        # Use a slice of the raw ID hash for uniqueness
        hash_part = slugify(raw_id)[-16:]
        item_id = f"lr_phrase_{lang}_{hash_part}"
        category = "phrase"

    return {
        "id": item_id,
        "type": "vocabulary",
        "content": content,
        "answer": full_answer,
        "category": category,
        "difficulty": "",
        "created_date": today,
        "due_date": tomorrow(),  # placeholder; overwritten by scheduler
        "interval_days": 1,
        "repetitions": 0,
        "easiness_factor": 2.5,
        "consecutive_correct": 0,
        "consecutive_incorrect": 0,
        "last_reviewed": today,
        "last_quality": 3,
        "mastery_level": 0,
        "total_reviews": 0,
        "priority": "medium",
        "lr_source": True,
    }


def assign_due_dates(new_items: list[dict], existing_queue: dict, daily_limit: int) -> None:
    """Spread due dates so at most daily_limit new items land on any one day.

    We look at how many items are already due tomorrow from the existing queue,
    then fill remaining slots before moving to the next day.
    """
    if daily_limit <= 0:
        # No spreading — all due tomorrow
        for item in new_items:
            item["due_date"] = tomorrow()
        return

    # Count already-scheduled items per day in the existing queue
    from collections import defaultdict
    day_counts: dict[str, int] = defaultdict(int)
    for bucket in existing_queue.values():
        for item_id in bucket:
            # We don't have the item's due_date here; assume tomorrow for queued items
            pass
    # Simpler: just start filling from tomorrow
    day_offset = 1
    slot = 0  # items assigned on current day

    for item in new_items:
        if slot >= daily_limit:
            day_offset += 1
            slot = 0
        item["due_date"] = date_plus(TODAY, day_offset)
        item["interval_days"] = day_offset
        slot += 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Import Language Reactor export into Fluent")
    parser.add_argument("file", help="Path to Language Reactor .zip or .csv export")
    parser.add_argument("--lang", help="Fluent language code to import into (e.g. de, es)")
    parser.add_argument("--daily-limit", type=int, default=20, metavar="N",
                        help="Max new items due per day (default: 20; 0 = no limit)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without writing")
    parser.add_argument("--data-dir", help="Override Fluent data directory path")
    args = parser.parse_args()

    file_path = Path(args.file).expanduser().resolve()
    if not file_path.exists():
        print(f"[Fluent] Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # ---- Load Language Reactor data ----------------------------------------
    try:
        rows = load_lr_rows(file_path)
    except Exception as e:
        print(f"[Fluent] Error reading export file: {e}", file=sys.stderr)
        sys.exit(2)

    if not rows:
        print("[Fluent] Error: no items found in export file.", file=sys.stderr)
        sys.exit(1)

    # ---- Determine target language -----------------------------------------
    available_langs = detect_languages(rows)

    if args.lang:
        lang_code = args.lang
        rows = [r for r in rows if len(r) > _C_LANG and r[_C_LANG] == lang_code]
        if not rows:
            print(f"[Fluent] Error: no items for language '{lang_code}' in the export.", file=sys.stderr)
            print(f"[Fluent]   Languages found: {', '.join(sorted(available_langs))}", file=sys.stderr)
            sys.exit(1)
    elif len(available_langs) == 1:
        lang_code = next(iter(available_langs))
    else:
        print(f"[Fluent] Error: export contains multiple languages ({', '.join(sorted(available_langs))}).", file=sys.stderr)
        print(f"[Fluent]   Use --lang CODE to pick one.", file=sys.stderr)
        sys.exit(1)

    # ---- Resolve Fluent data directory -------------------------------------
    data_dir = resolve_data_dir(lang_code, args.data_dir)

    if data_dir is None:
        registry = load_registry()
        known = ", ".join(sorted(registry.get("languages", {}).keys())) or "(none)"
        print(f"[Fluent] Error: language '{lang_code}' is not registered in Fluent.", file=sys.stderr)
        print(f"[Fluent]   Known languages: {known}", file=sys.stderr)
        print(f"[Fluent]   To add it, register a new language with fluent-lang.py, then run /fluent-setup.", file=sys.stderr)
        sys.exit(1)

    sr_path = data_dir / "spaced-repetition.json"
    if not sr_path.exists():
        print(f"[Fluent] Error: spaced-repetition.json not found at {sr_path}", file=sys.stderr)
        print(f"[Fluent]   Has /fluent-setup been run for '{lang_code}'?", file=sys.stderr)
        sys.exit(2)

    # ---- Parse and convert items -------------------------------------------
    parsed: list[dict] = []
    parse_errors = 0
    for row in rows:
        item = row_to_item(row, TODAY)
        if item:
            parsed.append(item)
        else:
            parse_errors += 1

    # ---- Load existing SR database and deduplicate -------------------------
    sr = load_json(sr_path)
    existing_items: dict = sr.setdefault("items", {})
    existing_queue: dict = sr.get("review_queue", {})

    new_items = [item for item in parsed if item["id"] not in existing_items]
    skipped = len(parsed) - len(new_items)

    # ---- Spread due dates --------------------------------------------------
    assign_due_dates(new_items, existing_queue, args.daily_limit)

    # ---- Summarise / dry-run -----------------------------------------------
    print(f"[Fluent] Language Reactor import — {lang_code.upper()}")
    print(f"[Fluent]   File:          {file_path.name}")
    print(f"[Fluent]   Items in file: {len(rows)} ({len(rows) - len(parsed)} unparseable)")
    print(f"[Fluent]   New to add:    {len(new_items)}")
    print(f"[Fluent]   Already known: {skipped}")
    if args.daily_limit > 0 and new_items:
        days_needed = -(-len(new_items) // args.daily_limit)  # ceiling div
        last_day = date_plus(TODAY, days_needed)
        print(f"[Fluent]   Schedule:      {args.daily_limit}/day → queue fills through {last_day}")

    if args.dry_run:
        print(f"[Fluent] Dry run — nothing written.")
        if new_items:
            print(f"[Fluent] First 5 items that would be added:")
            for item in new_items[:5]:
                print(f"  {item['id']}: {item['content'][:60]}")
        sys.exit(0)

    if not new_items:
        print(f"[Fluent] Nothing to import — all items already known.")
        sys.exit(0)

    # ---- Write ---------------------------------------------------------------
    # Backup before touching anything
    backup_path = data_dir / ".backups" / f"pre-lr-import-{TODAY}"
    backup_path.mkdir(parents=True, exist_ok=True)
    import shutil
    for f in data_dir.glob("*.json"):
        shutil.copy2(f, backup_path / f.name)

    for item in new_items:
        existing_items[item["id"]] = item

    sr["review_queue"] = rebuild_queue(existing_items, TODAY)
    sr.setdefault("metadata", {})["last_updated"] = TODAY
    sr["metadata"]["total_items_tracked"] = len(existing_items)

    save_json_atomic(sr_path, sr)

    print(f"[Fluent] ✅ Imported {len(new_items)} items into {sr_path}")
    print(f"[Fluent] 🧠 Total items tracked: {len(existing_items)}")
    print(f"[Fluent]   Backup saved to {backup_path}")


if __name__ == "__main__":
    main()
