#!/usr/bin/env python3
"""Run discoverability smoke tests against a globally installed Codex skill."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


FAILURE_PATTERNS = (
    "未找到该技能",
    "未发现可用技能",
    "回退",
    "fallback",
)


@dataclass(frozen=True)
class SmokeCase:
    key: str
    prompt: str


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def resolve_codex_executable() -> str:
    candidates: list[str] = []
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
        candidates.append("codex")

    for candidate in candidates:
        resolved = shutil.which(candidate) if Path(candidate).name == candidate else candidate
        if resolved and Path(resolved).exists():
            return resolved
    raise FileNotFoundError("Unable to locate codex executable.")


def parse_jsonl(raw: str) -> tuple[str, dict[str, int]]:
    last_message = ""
    usage = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0}

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        if event.get("type") == "item.completed":
            item = event.get("item", {})
            if isinstance(item, dict) and item.get("type") == "agent_message":
                text = item.get("text")
                if isinstance(text, str):
                    last_message = text
        elif event.get("type") == "turn.completed":
            raw_usage = event.get("usage", {})
            if isinstance(raw_usage, dict):
                for key in usage:
                    value = raw_usage.get(key)
                    if isinstance(value, int):
                        usage[key] = value

    return last_message, usage


def detect_success(text: str, skill_name: str, markers: tuple[str, ...]) -> dict[str, object]:
    lower_text = text.lower()
    failure_hits = [pattern for pattern in FAILURE_PATTERNS if pattern.lower() in lower_text]
    marker_hits = [marker for marker in markers if marker.lower() in lower_text]
    exact_name = skill_name.lower() in lower_text
    success = exact_name and bool(marker_hits) and not failure_hits
    return {
        "success": success,
        "failure_hits": failure_hits,
        "marker_hits": marker_hits,
        "exact_name": exact_name,
    }


def build_cases(skill_name: str, skill_path: str | None, markers: tuple[str, ...]) -> list[SmokeCase]:
    marker_text = ", ".join(markers)
    suffix = (
        "\n\nReply in Simplified Chinese.\n"
        "Output exactly 3 lines:\n"
        "1. `skill-detected: ...`\n"
        "2. `unique-marker: ...`\n"
        "3. `DISCOVERY_DONE`\n\n"
        "For the `unique-marker` line, echo at least one exact marker from this list if the intended skill is actually used:\n"
        f"{marker_text}\n"
    )
    cases = [
        SmokeCase("explicit-named", f'Use the skill named "{skill_name}".{suffix}'),
        SmokeCase("explicit-dollar", f"Use ${skill_name} for this task.{suffix}"),
    ]
    if skill_path:
        cases.append(SmokeCase("explicit-path", f"Use ${skill_name} at {skill_path} for this task.{suffix}"))
    return cases


def run_case(
    codex_executable: str,
    workspace_root: Path,
    case: SmokeCase,
    output_dir: Path,
    skill_name: str,
    markers: tuple[str, ...],
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    completed = subprocess.run(
        [
            codex_executable,
            "exec",
            "--skip-git-repo-check",
            "--json",
            "-C",
            str(workspace_root),
            "-",
        ],
        input=case.prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    (output_dir / "prompt.md").write_text(case.prompt, encoding="utf-8")
    (output_dir / "events.jsonl").write_text(completed.stdout, encoding="utf-8")
    (output_dir / "stderr.txt").write_text(completed.stderr, encoding="utf-8")

    response, usage = parse_jsonl(completed.stdout)
    (output_dir / "response.md").write_text(response, encoding="utf-8")

    detection = detect_success(response, skill_name, markers)
    result = {
        "case": case.key,
        "returncode": completed.returncode,
        "usage": usage,
        "response_chars": len(response),
        **detection,
    }
    (output_dir / "meta.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Run global Codex skill smoke tests.")
    parser.add_argument("--run-root", required=True, help="Output run directory.")
    parser.add_argument("--workspace-root", required=True, help="Workspace to execute codex exec in.")
    parser.add_argument("--skill-name", required=True, help="Installed global skill name.")
    parser.add_argument("--skill-path", help="Optional path for explicit-path case.")
    parser.add_argument(
        "--marker",
        action="append",
        required=True,
        help="Unique marker expected when the intended skill is used. Repeatable.",
    )
    args = parser.parse_args()

    run_root = Path(args.run_root).resolve()
    workspace_root = Path(args.workspace_root).resolve()
    run_root.mkdir(parents=True, exist_ok=True)

    codex_executable = resolve_codex_executable()
    markers = tuple(args.marker)
    cases = build_cases(args.skill_name, args.skill_path, markers)

    manifest = {
        "run_root": str(run_root),
        "workspace_root": str(workspace_root),
        "skill_name": args.skill_name,
        "skill_path": args.skill_path,
        "markers": list(markers),
        "results": [],
    }

    for case in cases:
        case_root = run_root / case.key
        result = run_case(
            codex_executable=codex_executable,
            workspace_root=workspace_root,
            case=case,
            output_dir=case_root,
            skill_name=args.skill_name,
            markers=markers,
        )
        manifest["results"].append(result)

    (run_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"RUN_ROOT={run_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
