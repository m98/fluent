# Changelog

All notable changes to Fluent will be documented in this file.

## [Unreleased]

### Changed

- `AGENTS.md` is now the single instruction file for every AI agent. It holds
  the tutor role and rules that used to live in `CLAUDE.md`, in agent-neutral
  wording, plus a short "Running Fluent in Your Agent" section for agents
  without Claude Code's skill and hook system. `CLAUDE.md` is now a one-line
  `@AGENTS.md` import, so Claude Code behaves as before. The old `AGENTS.md`
  (a second guide that duplicated `LEARNING_SYSTEM.md` and pointed back at
  `CLAUDE.md`) is replaced. Edit `AGENTS.md`, not `CLAUDE.md`.

### Added

- Answer-leak guard (`answer-leak-guard.py`, `Stop` + `UserPromptSubmit` hooks).
  When an exercise message shows the answer after the prompt line, the item is
  voided and re-posed instead of being graded, so a leaked answer is never
  recorded as mastery. The guard only runs in conversations where the learner
  started a practice skill (`/fluent-learn`, `/fluent-vocab`, `/fluent-review`,
  `/fluent-writing`, `/fluent-speaking`, `/fluent-reading`); it stays silent in
  every other project (#14, #15, thanks @ShengLin1001).
- Review and reading prompts now end at an explicit learner-input line, and the
  review `**Type:**` header shows the bare category only (#13).

### Fixed

- Re-sending a session with the same `session_id` now replaces the earlier
  record, as the docs always said, instead of counting the session again
  (`total_sessions`, exercises and minutes were inflated on every retry, and
  corrected content was ignored). Only the most recent session can be
  replaced; otherwise `update-db.py` exits `1` and changes nothing (#19,
  thanks @dawood8080).
- `update-db.py` now also accepts the session payload as its first argument,
  so it no longer blocks forever waiting on stdin when run as a background
  task. Stdin remains the default (#11, thanks @tyrannomark).
- `/fluent-setup` no longer fails with `Skill fluent:fluent-learn can not be used
  with Skill tool due to disable-model-invocation` when the learner accepts the
  first lesson. Setup now ends by asking the learner to type `/fluent-learn`
  (#29).
- The `/fluent-learn` menu (options 1-5) no longer tries to start the gated
  practice skills through the Skill tool; it reads the chosen skill's file and
  follows it instead.
- `update-db.py` no longer corrupts learner databases when the session payload
  contains non-ASCII text (CJK, Arabic, …) on Windows/Git Bash. `force_utf8_io()`
  now reconfigures stdin as well — under an ASCII/C locale the payload was
  decoded with surrogateescape and crashed at save time, *after* some databases
  had already been written (double-counting stats on retry).
- All six databases are now written with a two-phase commit (stage every file
  to `.tmp`, then swap all in), so a serialization or encoding error exits `2`
  without touching any database — the documented "no files were modified"
  guarantee now actually holds.
- Pre-update backups are no longer overwritten when the same `session_id` is
  retried; a numbered sibling directory (`pre-update-<id>-2`, `-3`, …) is
  created instead, preserving the earliest (pre-corruption) backup.
- Test suite: file reads now pass `encoding="utf-8"` so non-Latin milestone
  tests pass on Windows (default cp932/cp1252 locales); added regression tests
  for CJK payloads, ASCII-locale runs, backup preservation, and save-failure
  atomicity.

## [0.3.0] — 2026-06-15

### Added

- Milestones support in the `update-db.py` session payload. The new
  `milestones[]` field accepts either a bare string or an object
  `{ "milestone": <required non-empty string>, "date": <optional YYYY-MM-DD,
  defaults to the session date> }`. Each milestone is recorded in both
  `session-log.milestones[]` and `learner-profile.achievements[]`. Validation
  rejects malformed entries (exit `1`, no files written); an unparseable
  `date` falls back to the session date.

## [0.2.1] — 2026-06-11

### Fixed

- Hooks no longer fail on Windows with `No such file or directory` (#5).
  Plugin hook commands in `hooks.json` used the bash default-value syntax
  `${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-.}}`, which Claude Code's own
  variable substitution does not understand on Windows — it replaced the
  variable names but left the `:-` separators literal, producing a single
  garbage path. Hook commands now use plain `${CLAUDE_PLUGIN_ROOT}` (always
  set for plugin hooks) and invoke scripts via an explicit `python3`/`bash`
  interpreter so they don't depend on shebang handling under Git Bash.

## [0.2.0] — 2026-05-14

### Breaking changes

All 12 skills renamed with a `fluent-` prefix to prevent collisions with other
plugins and Claude Code built-ins. Update any muscle memory or external
references.

| Old | New |
|-----|-----|
| `/setup` | `/fluent-setup` |
| `/learn` | `/fluent-learn` |
| `/review` | `/fluent-review` |
| `/vocab` | `/fluent-vocab` |
| `/writing` | `/fluent-writing` |
| `/speaking` | `/fluent-speaking` |
| `/reading` | `/fluent-reading` |
| `/progress` | `/fluent-progress` |
| `sm2-calculator` | `fluent-sm2-calculator` |
| `db-updater` | `fluent-db-updater` |
| `feedback-formatter` | `fluent-feedback-formatter` |
| `session-analyzer` | `fluent-session-analyzer` |

New session result files use `/results/fluent-{skill}-session-{NNN}.md`.
Existing files using the older `{skill}-session-{NNN}.md` naming are still
read by `fluent-session-analyzer` — no migration required.

### Fixed

- Plugin install no longer fails on first DB read. Skills now invoke helper
  scripts via `${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-.}}/.claude/hooks/...`
  so the path resolves regardless of CWD.
- Added missing `.claude/hooks/ensure_data_dir.py` referenced by
  `fluent-setup`.

### Migration

```bash
claude plugin update fluent@m98
```

Then use the new slash commands. Your data (`~/.claude/fluent-data/` or
`./data/`) is unchanged.

## [0.1.0] — 2026-03-15

Initial release.
