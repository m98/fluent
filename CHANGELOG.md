# Changelog

All notable changes to Fluent will be documented in this file.

## [0.4.0] — 2026-08-27

### Added

- `/fluent-review` now selects due items with deterministic concept-aware
  round-robin coverage instead of taking a priority-only slice.
- Added optional `concept_id` metadata and a compatibility map for legacy review
  items, plus bounded same-concept variants after a difficult answer.
- Added selector and updater tests for concept coverage, deferred items, and
  duplicate review protection.

### Fixed

- New vocabulary and error-pattern records now preserve optional `concept_id`.
- Reusing a `review_results.item_id` in one payload is rejected before any data
  is written.
- SM-2 interval rounding and per-item mastery threshold transitions now match
  the documented calculator; invalid review quality and unknown item IDs are
  rejected before writing.

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
