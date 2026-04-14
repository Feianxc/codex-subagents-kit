#!/usr/bin/env python3
"""Install or update codex-subagents-kit into the local Codex skills directory."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Install codex-subagents-kit into ~/.codex/skills.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument(
        "--source-dir",
        help="Optional explicit source skill directory. Defaults to <repo-root>/skills/codex-subagents-kit.",
    )
    parser.add_argument(
        "--target-dir",
        help="Optional explicit target directory. Defaults to ~/.codex/skills/codex-subagents-kit.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite target if it exists.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions only.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    source_dir = Path(args.source_dir).resolve() if args.source_dir else repo_root / "skills" / "codex-subagents-kit"
    target_dir = (
        Path(args.target_dir).expanduser().resolve()
        if args.target_dir
        else Path.home() / ".codex" / "skills" / "codex-subagents-kit"
    )

    if not source_dir.exists():
        print(f"ERROR: source directory not found: {source_dir}")
        return 1
    if not (source_dir / "SKILL.md").exists():
        print(f"ERROR: SKILL.md not found under source directory: {source_dir}")
        return 1

    print(f"SOURCE={source_dir}")
    print(f"TARGET={target_dir}")

    if target_dir.exists():
        if not args.force:
            print("ERROR: target already exists. Re-run with --force to overwrite.")
            return 2
        print("ACTION=remove-existing-target")
        if not args.dry_run:
            shutil.rmtree(target_dir)

    print("ACTION=copy-skill")
    if not args.dry_run:
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_dir, target_dir)

    print("STATUS=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

