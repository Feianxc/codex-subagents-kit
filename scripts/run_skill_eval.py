#!/usr/bin/env python3
"""Run Codex exec against baseline and release skills in the local skill-lab."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Variant:
    key: str
    skill_name: str
    skill_path: Path
    fixture_dir: Path


@dataclass(frozen=True)
class Case:
    key: str
    prompt_file: Path


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


def load_prompt(template_path: Path, skill_name: str) -> str:
    return template_path.read_text(encoding="utf-8").replace("{skill_name}", skill_name)


def parse_jsonl(raw: str) -> tuple[list[dict[str, object]], str, dict[str, int]]:
    events: list[dict[str, object]] = []
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
        events.append(event)

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

    return events, last_message, usage


def run_case(codex_executable: str, variant: Variant, case: Case, output_dir: Path) -> dict[str, object]:
    prompt = load_prompt(case.prompt_file, variant.skill_name)
    prompt += (
        "\n\nPreferred invocation for reliability: "
        f"Use ${variant.skill_name} at {variant.skill_path.as_posix()}.\n"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    completed = subprocess.run(
        [
            codex_executable,
            "exec",
            "--skip-git-repo-check",
            "--json",
            "-c",
            f"skills.config=[{{path='{variant.skill_path.as_posix()}', enabled=true}}]",
            "-C",
            str(variant.fixture_dir),
            "-",
        ],
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    (output_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    (output_dir / "events.jsonl").write_text(completed.stdout, encoding="utf-8")
    (output_dir / "stderr.txt").write_text(completed.stderr, encoding="utf-8")

    events, last_message, usage = parse_jsonl(completed.stdout)
    (output_dir / "response.md").write_text(last_message, encoding="utf-8")

    meta = {
        "variant": variant.key,
        "skill_name": variant.skill_name,
        "fixture_dir": str(variant.fixture_dir),
        "case": case.key,
        "returncode": completed.returncode,
        "usage": usage,
        "event_count": len(events),
        "response_chars": len(last_message),
    }
    (output_dir / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return meta


def main() -> int:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = argparse.ArgumentParser(description="Run skill-lab Codex evaluations.")
    parser.add_argument("--lab-root", default=".", help="Path to skill-lab root.")
    parser.add_argument("--run-id", help="Optional explicit run id.")
    parser.add_argument("--variant", action="append", help="Optional variant filter: baseline or release.")
    parser.add_argument(
        "--case",
        action="append",
        help="Optional case filter: smoke, mode-selection, topology, context-efficiency.",
    )
    args = parser.parse_args()

    lab_root = Path(args.lab_root).resolve()
    run_id = args.run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = lab_root / "runs" / run_id
    run_root.mkdir(parents=True, exist_ok=True)

    codex_executable = resolve_codex_executable()

    variants = [
        Variant(
            key="baseline",
            skill_name="codex-agent-swarm-baseline",
            skill_path=lab_root / "skills" / "baseline-codex-agent-swarm",
            fixture_dir=lab_root / "fixtures" / "baseline",
        ),
        Variant(
            key="release",
            skill_name="codex-subagents-kit",
            skill_path=lab_root / "skills" / "codex-subagents-kit",
            fixture_dir=lab_root / "fixtures" / "release",
        ),
    ]
    cases = [
        Case(key="smoke", prompt_file=lab_root / "prompts" / "smoke.md"),
        Case(key="mode-selection", prompt_file=lab_root / "prompts" / "mode-selection.md"),
        Case(key="topology", prompt_file=lab_root / "prompts" / "topology.md"),
        Case(key="context-efficiency", prompt_file=lab_root / "prompts" / "context-efficiency.md"),
    ]

    if args.variant:
        allowed_variants = set(args.variant)
        variants = [variant for variant in variants if variant.key in allowed_variants]
    if args.case:
        allowed_cases = set(args.case)
        cases = [case for case in cases if case.key in allowed_cases]

    manifest: dict[str, object] = {
        "run_id": run_id,
        "run_root": str(run_root),
        "codex_executable": codex_executable,
        "started_at": datetime.now().isoformat(),
        "results": [],
    }

    for variant in variants:
        for case in cases:
            case_root = run_root / variant.key / case.key
            meta = run_case(codex_executable, variant, case, case_root)
            manifest["results"].append(meta)

    (run_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"RUN_ID={run_id}")
    print(f"RUN_ROOT={run_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
