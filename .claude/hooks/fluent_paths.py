"""
Fluent path resolution — supports dual-mode (clone vs plugin install).

Data directory resolution precedence:
  1. $FLUENT_DATA_DIR if set (absolutized)
  2. $CLAUDE_PROJECT_DIR/data/$FLUENT_LANG (clone mode, if FLUENT_LANG is set)
  3. $CLAUDE_PROJECT_DIR/data if that dir holds learner-profile.json (clone mode, no FLUENT_LANG)
  4. ./data/$FLUENT_LANG (clone mode, in-repo cwd, if FLUENT_LANG is set)
  5. ./data if ./data/learner-profile.json exists (clone mode, in-repo cwd)
  6. ~/.claude/fluent-data/$FLUENT_LANG (plugin-mode fallback, if FLUENT_LANG is set)
  7. ~/.claude/fluent-data (plugin-mode fallback)

Set FLUENT_LANG=es (or fr, de, …) to study a specific language in isolation.
Each language gets its own data subdirectory and results subdirectory.

Plugin-root resolution precedence:
  1. $CLAUDE_PLUGIN_ROOT if set
  2. $CLAUDE_PROJECT_DIR if set
  3. parent of this file's .claude/ dir (dev-run fallback)

Pure resolvers (data_dir / plugin_root / backups_dir / results_dir) do not create directories.
Call ensure_data_dir() before writing.
"""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path


def force_utf8_io() -> None:
    """Make stdout/stderr UTF-8 so emoji/CJK output doesn't crash on Windows.

    Windows consoles default to a legacy code page (cp1252/gbk); printing the
    emoji in the hook summaries raises UnicodeEncodeError there. No-op on
    platforms whose streams are already UTF-8 or predate ``reconfigure``.
    Call once at the top of any hook that prints.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def active_lang_file() -> Path:
    """Path to the persisted active-language config file (~/.claude/fluent-active-lang).

    Written by /fluent-lang skill. FLUENT_LANG env var takes precedence over this file.
    """
    return Path.home() / ".claude" / "fluent-active-lang"


def _active_lang() -> str:
    """Return the active language code (lowercase) or empty string.

    Priority: FLUENT_LANG env var > ~/.claude/fluent-active-lang file.
    """
    env = os.environ.get("FLUENT_LANG", "").strip().lower()
    if env:
        return env
    cfg = active_lang_file()
    if cfg.exists():
        try:
            return cfg.read_text(encoding="utf-8").strip().lower()
        except OSError:
            pass
    return ""


@lru_cache(maxsize=1)
def data_dir() -> Path:
    """Resolve the runtime data directory (pure — does not create it).

    When FLUENT_LANG is set the resolved directory is always the language
    subdirectory (e.g. data/es/) regardless of whether it exists yet —
    ensure_data_dir() creates it on first use.
    """
    env = os.environ.get("FLUENT_DATA_DIR")
    if env:
        return Path(env).expanduser().resolve()

    lang = _active_lang()

    project = os.environ.get("CLAUDE_PROJECT_DIR")
    if project:
        base = (Path(project) / "data").resolve()
        if lang:
            candidate = base / lang
            # Use project-based lang dir only when in clone mode:
            # language subdir already has a profile, OR root data dir has one
            # (profile at root = clone mode that hasn't yet been partitioned).
            if (candidate / "learner-profile.json").exists() or (base / "learner-profile.json").exists():
                return candidate
        elif (base / "learner-profile.json").exists():
            return base

    cwd_data = (Path.cwd() / "data").resolve()
    if lang:
        candidate = cwd_data / lang
        if (candidate / "learner-profile.json").exists() or (cwd_data / "learner-profile.json").exists():
            return candidate
    elif (cwd_data / "learner-profile.json").exists():
        return cwd_data

    if lang:
        return (Path.home() / ".claude" / "fluent-data" / lang).resolve()
    return (Path.home() / ".claude" / "fluent-data").resolve()


def ensure_data_dir() -> Path:
    """Resolve the data directory and create it if missing. Call before writing."""
    d = data_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


@lru_cache(maxsize=1)
def plugin_root() -> Path:
    """Resolve the plugin/repo root directory."""
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        return Path(env).resolve()
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def backups_dir() -> Path:
    """Resolve the backups directory. Always nested inside data_dir to avoid collisions
    when the fallback ~/.claude/fluent-data is used (the parent ~/.claude/ is shared
    across plugins)."""
    return data_dir() / ".backups"


def ensure_backups_dir() -> Path:
    """Resolve the backups directory and create it if missing."""
    b = backups_dir()
    b.mkdir(parents=True, exist_ok=True)
    return b


@lru_cache(maxsize=1)
def results_dir() -> Path:
    """Resolve the results directory.

    When FLUENT_LANG is set returns results/{lang}/ so each language keeps
    its own session history (e.g. results/es/, results/fr/).
    Falls back to results/ for single-language setups.
    """
    lang = _active_lang()
    root = plugin_root()
    if lang:
        return root / "results" / lang
    return root / "results"


def ensure_results_dir() -> Path:
    """Resolve the results directory and create it if missing."""
    r = results_dir()
    r.mkdir(parents=True, exist_ok=True)
    return r
