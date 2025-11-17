#!/usr/bin/env python3
"""
Fluent Data Validation Hook
Validates JSON structure and creates backups after Write/Edit operations
"""
import json
import sys
import os
import shutil
from datetime import datetime
from pathlib import Path

def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid hook input: {e}", file=sys.stderr)
        sys.exit(1)

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Only process data/*.json files
    if not file_path or not file_path.startswith("data/") or not file_path.endswith(".json"):
        sys.exit(0)

    # Check if file exists
    if not os.path.exists(file_path):
        sys.exit(0)

    # Validate JSON structure
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = f"{file_path}.backup-{timestamp}"
        shutil.copy2(file_path, backup_path)

        print(f"[Fluent] ✓ Data saved and validated: {file_path}")
        print(f"[Fluent] 💾 Backup created: {backup_path}")

        # Exit code 0 = success
        sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"[Fluent] ⚠️  WARNING: Invalid JSON in {file_path}", file=sys.stderr)
        print(f"[Fluent] Error: {e}", file=sys.stderr)
        # Exit code 2 = blocking error (shows to Claude)
        sys.exit(2)
    except Exception as e:
        print(f"[Fluent] Error processing {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
