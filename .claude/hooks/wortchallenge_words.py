#!/usr/bin/env python3
"""
Read Wörterpraxis-style Obsidian word notes for /wortchallenge.

This helper is read-only. It never imports words into Fluent by itself; the
skill decides which unknown words to send to update-db.py as new_vocabulary.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fluent_paths import data_dir  # noqa: E402

CONFIG_PATH = data_dir() / "wortchallenge-source.json"
ELIGIBLE_TYPES = {"noun", "verb", "adjective", "phrase", "expression"}
EXCLUDED_TYPES = {"hub", "big-hub", "big hub"}


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return load_json(CONFIG_PATH)
    return {}


def resolve_words_dir(config: dict, words_dir: Optional[str] = None) -> Path:
    value = (
        words_dir
        or os.environ.get("WORTCHALLENGE_WORDS_DIR")
        or config.get("words_dir")
    )
    if not value:
        raise ValueError(
            "No words_dir configured. Create data/wortchallenge-source.json "
            "or set WORTCHALLENGE_WORDS_DIR."
        )
    resolved = Path(value).expanduser().resolve()
    if not resolved.is_dir():
        raise FileNotFoundError(f"words_dir not found: {resolved}")
    return resolved


def section(markdown: str, heading: str) -> str:
    pattern = rf"(?ims)^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, markdown)
    return match.group(1).strip() if match else ""


def subsection(markdown: str, heading: str) -> str:
    pattern = rf"(?ims)^###\s+{re.escape(heading)}\s*$\n(.*?)(?=^###\s+|^##\s+|\Z)"
    match = re.search(pattern, markdown)
    return match.group(1).strip() if match else ""


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("|---"):
            return cleaned.strip("- ").strip()
    return ""


def title_from_note(path: Path, markdown: str) -> str:
    match = re.search(r"(?m)^#\s+(.+?)\s*$", markdown)
    return match.group(1).strip() if match else path.stem


def normalize_id(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^(der|die|das)\s+", "", text, flags=re.IGNORECASE)
    replacements = str.maketrans({
        "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
        "Ä": "ae", "Ö": "oe", "Ü": "ue",
    })
    text = text.translate(replacements)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^A-Za-z0-9]+", "_", text.lower()).strip("_")
    return text or "item"


def first_example(examples: str) -> str:
    for line in examples.splitlines():
        cleaned = line.strip()
        match = re.match(r"^\d+\.\s+(.+)$", cleaned)
        if match:
            return match.group(1).strip()
    return ""


def parse_note(path: Path) -> Optional[Dict[str, object]]:
    markdown = path.read_text(encoding="utf-8")
    title = title_from_note(path, markdown)
    note_type = first_nonempty_line(section(markdown, "Type"))
    note_type_key = note_type.lower().strip()

    if note_type_key in EXCLUDED_TYPES or note_type_key not in ELIGIBLE_TYPES:
        return None

    turkish = subsection(markdown, "Turkish")
    english = subsection(markdown, "English")
    if not title or not first_nonempty_line(turkish):
        return None

    patterns = section(markdown, "Common Patterns")
    examples = section(markdown, "Example Sentences")

    answer_parts = [first_nonempty_line(turkish)]
    english_line = first_nonempty_line(english)
    if english_line:
        answer_parts.append(english_line)

    item_id = f"wortchallenge_{normalize_id(title)}"
    return {
        "item_id": item_id,
        "item_type": "vocabulary",
        "content": title,
        "answer": " / ".join(answer_parts),
        "category": f"wortchallenge_{normalize_id(note_type or 'vocabulary')}",
        "difficulty": "",
        "priority": "medium",
        "source": {
            "type": "wortchallenge",
            "note_path": str(path),
            "obsidian_link": f"[[{title}]]",
        },
        "note_type": note_type,
        "turkish": turkish,
        "english": english,
        "common_patterns": patterns,
        "example_sentences": examples,
        "first_example": first_example(examples),
    }


def load_words(words_dir: Path, limit: Optional[int] = None) -> Dict[str, object]:
    words: List[Dict[str, object]] = []
    skipped: List[str] = []
    for path in sorted(words_dir.glob("*.md")):
        parsed = parse_note(path)
        if parsed is None:
            skipped.append(str(path))
            continue
        words.append(parsed)
        if limit is not None and len(words) >= limit:
            break
    return {
        "words_dir": str(words_dir),
        "words": words,
        "skipped": skipped,
        "count": len(words),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--words-dir")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    try:
        config = load_config()
        words_dir = resolve_words_dir(config, args.words_dir)
        result = load_words(words_dir, args.limit or config.get("daily_limit"))
    except Exception as exc:
        print(f"[Fluent] wortchallenge word loading failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
