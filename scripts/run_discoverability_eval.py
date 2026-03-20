#!/usr/bin/env python3
"""Run repeated discoverability tests for Codex skills."""

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
    unique_markers: tuple[str, ...]


@dataclass(frozen=True)
class PromptCase:
    key: str
    prompt_file: Path


FAILURE_PATTERNS = (
    "未找到该技能",
    "未发现可用技能",
    "回退",
    "fallback",
)


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


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def load_prompt(path: Path, skill_name: str) -> str:
    return path.read_text(encoding="utf-8").replace("{skill_name}", skill_name)


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


def detect_success(text: str, variant: Variant) -> dict[str, object]:
    lower_text = text.lower()
    failure_hits = [pattern for pattern in FAILURE_PATTERNS if pattern.lower() in lower_text]
    marker_hits = [marker for marker in variant.unique_markers if marker.lower() in lower_text]
    exact_name = variant.skill_name.lower() in lower_text
    success = exact_name and bool(marker_hits) and not failure_hits
    return {
        "success": success,
        "failure_hits": failure_hits,
        "marker_hits": marker_hits,
        "exact_name": exact_name,
    }


def run_once(
    codex_executable: str,
    variant: Variant,
    case: PromptCase,
    load_mode: str,
    output_dir: Path,
) -> dict[str, object]:
    prompt = load_prompt(case.prompt_file, variant.skill_name)
    marker_hint = ", ".join(variant.unique_markers)
    prompt += (
        "\n\nFor the `unique-marker` line, echo at least one exact marker from this list if the intended skill is actually used:\n"
        f"{marker_hint}\n"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    command = [
        codex_executable,
        "exec",
        "--skip-git-repo-check",
        "--json",
    ]
    if load_mode == "injected":
        command.extend(
            [
                "-c",
                f"skills.config=[{{path='{variant.skill_path.as_posix()}', enabled=true}}]",
            ]
        )
    command.extend(["-C", str(variant.fixture_dir), "-"])

    completed = subprocess.run(
        command,
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

    response, usage = parse_jsonl(completed.stdout)
    (output_dir / "response.md").write_text(response, encoding="utf-8")

    detection = detect_success(response, variant)
    result = {
        "variant": variant.key,
        "skill_name": variant.skill_name,
        "case": case.key,
        "load_mode": load_mode,
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
    parser = argparse.ArgumentParser(description="Run discoverability evaluations for Codex skills.")
    parser.add_argument("--lab-root", default=".", help="Path to skill-lab root.")
    parser.add_argument("--run-id", help="Optional explicit run id.")
    parser.add_argument("--repeat", type=int, default=2, help="Number of repeats per combination.")
    parser.add_argument("--variant", action="append", help="Optional variant filter.")
    parser.add_argument("--load-mode", action="append", help="Optional load mode filter: injected or project.")
    parser.add_argument("--case", action="append", help="Optional case filter.")
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
            unique_markers=("capability-gate", "artifact-orchestrated-swarm", "single-controller"),
        ),
        Variant(
            key="release",
            skill_name="codex-subagents-kit",
            skill_path=lab_root / "skills" / "codex-subagents-kit",
            fixture_dir=lab_root / "fixtures" / "release",
            unique_markers=("config-guided-codex-subagents", "product gate", "four gates", "scorecard"),
        ),
    ]
    cases = [
        PromptCase("explicit-named", lab_root / "prompts" / "discoverability-explicit-named.md"),
        PromptCase("explicit-dollar", lab_root / "prompts" / "discoverability-explicit-dollar.md"),
        PromptCase("explicit-path", lab_root / "prompts" / "discoverability-explicit-path.md"),
        PromptCase("implicit", lab_root / "prompts" / "discoverability-implicit.md"),
    ]
    load_modes = ["injected", "project"]

    if args.variant:
        wanted = set(args.variant)
        variants = [variant for variant in variants if variant.key in wanted]
    if args.case:
        wanted = set(args.case)
        cases = [case for case in cases if case.key in wanted]
    if args.load_mode:
        wanted = set(args.load_mode)
        load_modes = [mode for mode in load_modes if mode in wanted]

    manifest: dict[str, object] = {
        "run_id": run_id,
        "run_root": str(run_root),
        "repeat": args.repeat,
        "results": [],
    }

    def write_manifest() -> None:
        (run_root / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    for variant in variants:
        for load_mode in load_modes:
            for case in cases:
                for index in range(1, args.repeat + 1):
                    case_root = run_root / variant.key / load_mode / case.key / f"repeat-{index}"
                    result = run_once(codex_executable, variant, case, load_mode, case_root)
                    manifest["results"].append(result)
                    write_manifest()

    write_manifest()
    print(f"RUN_ID={run_id}")
    print(f"RUN_ROOT={run_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
