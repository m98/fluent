# Anki Flashcards for Dutch Language Learning

This repository contains Anki flashcard decks for learning Dutch at A1 and A2 levels, covering basic vocabulary and phrases.

## Directory Structure

- `/anki-exports` - Final, confirmed flashcard decks ready for import into Anki
- `/work-in-progress` - New flashcards under development (moved to `/anki-exports` after confirmation)

## Anki Export Format

The flashcards use Anki's standard tab-separated text format with the following structure:

### File Headers

```
#separator:tab
#html:true
```

- `#separator:tab` - Indicates that fields are separated by tab characters
- `#html:true` - Enables HTML formatting in the cards (allows `<br/>` tags and other HTML)

### Card Structure

Each line after the headers represents one flashcard with two fields separated by a tab character:

```
[FRONT]	[BACK]
```

#### Front (Question/Prompt)
The Dutch word, phrase, or question that the learner sees first.

**Examples:**
- `Wie?` - Single Dutch word
- `Wat eet u graag?` - Dutch phrase/question
- `Boterham` - Dutch vocabulary word

#### Back (Answer/Translation)
The translation, explanation, or answer. Can include:
- English translations
- Translations in other languages (Persian, Turkish)
- Additional context or notes
- HTML formatting (line breaks with `<br/>`)
- Emojis for visual memory aids

**Examples:**
- `Kim? <br/> کی؟` - Multiple translations with HTML line break
- `Sandwich (bread slice)` - English translation with context
- `Wheel (چرخ دوچرخه)` - Translation with Persian explanation
- `I had a busy day` - Full sentence translation

### Sound Files

Some cards may reference audio files for pronunciation:
```
[sound:googletts-4f2087aa-52f3a507-fe00a757-31837b9d-ec8a5ddc.mp3]
```

**Note:** When creating new flashcards, do not include sound tags. These are added separately through Anki's audio features.

### Format Example

```
#separator:tab
#html:true
Wie?	Kim? <br/> کی؟
Boterham	Sandwich (bread slice)
Ik had een drukke dag.	I had a busy day
```

## Creating New Flashcards

1. Create new cards in the `/work-in-progress` directory
2. Follow the standard Anki format (tab-separated, with headers)
3. Do not include sound tags in new cards
4. After user confirmation, move the file to `/anki-exports`