#!/usr/bin/env python3
"""
Fluent → Anki Exporter
Reads all spaced-repetition items and writes an Anki-importable TSV file.

Usage:
    python3 .claude/hooks/export-anki.py [output_path]

If output_path is omitted, writes to ~/Desktop/fluent-<lang>-anki-YYYY-MM-DD.txt
Exit codes: 0=success, 1=no items, 2=I/O error
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fluent_paths import data_dir, force_utf8_io

force_utf8_io()

DATA_DIR = data_dir()


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def escape_field(text: str) -> str:
    """Escape tabs and newlines for TSV; convert newlines to Anki HTML line breaks."""
    return text.replace("\t", " ").replace("\n", "<br>").replace("\r", "")


def make_front(item: dict) -> str:
    content = item.get("content", "").strip()
    item_type = item.get("type", "vocabulary")
    if item_type == "grammar_rule":
        return f"[Grammar] {content}"
    if item_type == "error_pattern":
        return f"[Pattern] {content}"
    return content


def make_back(item: dict) -> str:
    parts = [item.get("answer", "").strip()]
    category = item.get("category", "").strip()
    difficulty = item.get("difficulty", "").strip()
    if category:
        parts.append(f"<i>Category: {category}</i>")
    if difficulty:
        parts.append(f"<i>Level: {difficulty}</i>")
    return "<br>".join(p for p in parts if p)


def make_tags(item: dict, lang_slug: str) -> str:
    tags = [f"fluent::{lang_slug}"]
    item_type = item.get("type", "vocabulary")
    tags.append(f"type::{item_type}")
    category = item.get("category", "").strip()
    if category:
        tags.append(f"category::{category.replace(' ', '_')}")
    difficulty = item.get("difficulty", "").strip()
    if difficulty:
        tags.append(f"level::{difficulty}")
    mastery = item.get("mastery_level", 0)
    tags.append(f"mastery::{mastery}")
    return " ".join(tags)


def main():
    sr = load_json(DATA_DIR / "spaced-repetition.json")
    profile = load_json(DATA_DIR / "learner-profile.json")

    items = sr.get("items", {})
    # Profile may nest fields under "learner" (plugin schema) or at top level
    learner = profile.get("learner", profile)
    language = learner.get("target_language", profile.get("target_language", "Unknown"))
    lang_slug = language.lower().replace(" ", "_")

    if not items:
        print(f"[Fluent] No items found in {DATA_DIR / 'spaced-repetition.json'}", file=sys.stderr)
        sys.exit(1)

    today = datetime.now().strftime("%Y-%m-%d")

    if len(sys.argv) > 1:
        out_path = Path(sys.argv[1]).expanduser().resolve()
    else:
        out_path = Path.home() / "Desktop" / f"fluent-{lang_slug}-anki-{today}.txt"

    header_lines = [
        "#separator:tab",
        f"#deck:Fluent {language}",
        "#notetype:Basic",
        "#columns:Front\tBack\tTags",
        "#tags column:3",
        "#html:true",
    ]

    card_lines = []
    skipped = 0
    for item_id, item in sorted(items.items()):
        front = escape_field(make_front(item))
        back = escape_field(make_back(item))
        tags = escape_field(make_tags(item, lang_slug))
        if not front or not back:
            skipped += 1
            continue
        card_lines.append(f"{front}\t{back}\t{tags}")

    try:
        out_path.write_text(
            "\n".join(header_lines + card_lines) + "\n",
            encoding="utf-8",
        )
    except OSError as e:
        print(f"[Fluent] Error writing export file: {e}", file=sys.stderr)
        sys.exit(2)

    count = len(card_lines)
    print(f"[Fluent] ✅ Exported {count} cards to {out_path}")
    if skipped:
        print(f"[Fluent] ⚠️  Skipped {skipped} items with missing content or answer")
    print(f"[Fluent] 📥 In Anki: File → Import → select the file above")
    print(f"[Fluent] 🏷️  Deck: 'Fluent {language}' | Tags: type, category, mastery level")


if __name__ == "__main__":
    main()
