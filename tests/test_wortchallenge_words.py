#!/usr/bin/env python3
"""Tests for .claude/hooks/wortchallenge_words.py."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / ".claude" / "hooks" / "wortchallenge_words.py"


def load_module():
    spec = importlib.util.spec_from_file_location("wortchallenge_words", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NOTE_TEMPLATE = """# {title}

## Type
{note_type}

## Meaning
### Turkish
{turkish}

### English
{english}

### Simple German Explanation
Eine kurze Erklärung.

## Grammar
-

## Forms
-

## Common Patterns
| German Pattern | Turkish | English |
|---|---|---|
| {title} benutzen | kullanmak | to use |

## Example Sentences
1. Ich benutze {title} heute.
2. Das ist ein Beispiel.
3. Wir lernen zusammen.
4. Der Satz ist kurz.

## Related Nodes

## Family Root
"""


class WortchallengeWordsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.words_dir = Path(self.tmp.name)
        (self.words_dir / "Antrieb.md").write_text(
            NOTE_TEMPLATE.format(
                title="Antrieb",
                note_type="Noun",
                turkish="itici güç / motivasyon",
                english="drive / motivation",
            ),
            encoding="utf-8",
        )
        (self.words_dir / "ablehnen.md").write_text(
            NOTE_TEMPLATE.format(
                title="ablehnen",
                note_type="Verb",
                turkish="reddetmek",
                english="to reject",
            ),
            encoding="utf-8",
        )
        (self.words_dir / "Bau.md").write_text(
            NOTE_TEMPLATE.format(
                title="Bau",
                note_type="Hub",
                turkish="yapı / inşa",
                english="construction",
            ),
            encoding="utf-8",
        )
        (self.words_dir / "Malformed.md").write_text(
            "# Malformed\n\n## Type\nNoun\n\n## Meaning\n### English\nbroken",
            encoding="utf-8",
        )
        self.module = load_module()

    def tearDown(self):
        self.tmp.cleanup()

    def test_load_words_includes_normal_notes_only(self):
        result = self.module.load_words(self.words_dir)
        contents = [word["content"] for word in result["words"]]

        self.assertEqual(contents, ["Antrieb", "ablehnen"])
        self.assertEqual(result["count"], 2)
        self.assertTrue(any("Bau.md" in path for path in result["skipped"]))
        self.assertTrue(any("Malformed.md" in path for path in result["skipped"]))

    def test_parse_note_builds_vocab_payload_fields(self):
        parsed = self.module.parse_note(self.words_dir / "Antrieb.md")

        self.assertEqual(parsed["item_id"], "wortchallenge_antrieb")
        self.assertEqual(parsed["item_type"], "vocabulary")
        self.assertIn("itici güç", parsed["answer"])
        self.assertEqual(parsed["source"]["type"], "wortchallenge")
        self.assertEqual(parsed["source"]["obsidian_link"], "[[Antrieb]]")
        self.assertIn("Ich benutze", parsed["first_example"])


if __name__ == "__main__":
    unittest.main()
