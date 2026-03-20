#!/usr/bin/env python3
"""Run a child Codex exec task from a prompt file without shell quoting issues."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def resolve_codex_executable() -> str:
    candidates = []
    if os.name == "nt":
        candidates.extend(["codex.cmd", "codex.exe", "codex"])
        appdata = os.environ.get("APPDATA")
        if appdata:
            candidates.extend(
                [
                    str(Path(appdata) / "npm" / "codex.cmd"),
                    str(Path(appdata) / "npm" / "codex"),
                ]
            )
    else:
        candidates.extend(["codex"])

    for candidate in candidates:
        resolved = shutil.which(candidate) if Path(candidate).name == candidate else candidate
        if resolved and Path(resolved).exists():
            return resolved

    raise FileNotFoundError("Unable to locate codex executable.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a Codex swarm child task from a prompt file.")
    parser.add_argument("--run-root", required=True, help="Run root for relative paths and logs.")
    parser.add_argument(
        "--workspace-root",
        help="Optional workspace root. If omitted, infer it from <workspace>/.workspace/codex-swarm/runs/<run_id>.",
    )
    parser.add_argument("--prompt-file", required=True, help="Prompt file to pass on stdin.")
    parser.add_argument("--output-file", required=True, help="Where the last assistant message should go.")
    parser.add_argument(
        "--sandbox",
        default="workspace-write",
        choices=("read-only", "workspace-write", "danger-full-access"),
        help="Sandbox mode for child exec.",
    )
    parser.add_argument(
        "--json-log-file",
        help="Optional JSONL event log file. When set, child stdout is written here.",
    )
    parser.add_argument(
        "--skip-git-repo-check",
        action="store_true",
        default=True,
        help="Keep Codex usable outside Git repos. Enabled by default.",
    )
    args = parser.parse_args()

    run_root = Path(args.run_root).resolve()
    prompt_file = Path(args.prompt_file).resolve()
    output_file = Path(args.output_file).resolve()
    json_log_file = Path(args.json_log_file).resolve() if args.json_log_file else None
    if args.workspace_root:
        workspace_root = Path(args.workspace_root).resolve()
    else:
        try:
            workspace_root = run_root.parents[3]
        except IndexError:
            print(
                "Unable to infer workspace root from run_root; pass --workspace-root explicitly.",
                file=sys.stderr,
            )
            return 1

    if not prompt_file.exists():
        print(f"Prompt file not found: {prompt_file}", file=sys.stderr)
        return 1

    try:
        codex_executable = resolve_codex_executable()
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output_file.parent.mkdir(parents=True, exist_ok=True)
    if json_log_file:
        json_log_file.parent.mkdir(parents=True, exist_ok=True)

    prompt_text = prompt_file.read_text(encoding="utf-8")

    command = [
        codex_executable,
        "exec",
        "--sandbox",
        args.sandbox,
        "-C",
        str(workspace_root),
        "--output-last-message",
        str(output_file),
    ]
    if args.skip_git_repo_check:
        command.append("--skip-git-repo-check")
    if json_log_file:
        command.append("--json")
    command.append("-")

    completed = subprocess.run(
        command,
        input=prompt_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    if json_log_file:
        json_log_file.write_text(completed.stdout, encoding="utf-8")
    else:
        sys.stdout.write(completed.stdout)

    if completed.stderr:
        sys.stderr.write(completed.stderr)

    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
