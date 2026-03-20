#!/usr/bin/env python3
"""Probe local Codex runtime facts for swarm orchestration decisions."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
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


def run_command(codex_executable: str, args: list[str]) -> dict[str, object]:
    try:
        completed = subprocess.run(
            [codex_executable, *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
    except FileNotFoundError as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
        }


def parse_multi_agent(features_stdout: str) -> dict[str, object]:
    for line in features_stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0] == "multi_agent":
            return {
                "name": parts[0],
                "stage": parts[1],
                "enabled": parts[2].lower() == "true",
                "raw_line": line,
            }
    return {
        "name": "multi_agent",
        "stage": "unknown",
        "enabled": None,
        "raw_line": "",
    }


def parse_native_tools(explicit_tools: list[str]) -> dict[str, object]:
    env_raw = os.environ.get("CODEX_NATIVE_AGENT_TOOLS", "")
    env_tools = [tool.strip() for tool in env_raw.split(",") if tool.strip()]

    seen: list[str] = []
    for tool in [*explicit_tools, *env_tools]:
        if tool not in seen:
            seen.append(tool)

    return {
        "observed": bool(seen),
        "tools": seen,
        "source": "cli-args" if explicit_tools else ("env" if env_tools else "none"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe Codex runtime facts for swarm skills.")
    parser.add_argument("--run-root", required=True, help="Run root where audit files live.")
    parser.add_argument(
        "--native-tool",
        action="append",
        default=[],
        help="Record a native agent tool observed in the current session, e.g. spawn_agent.",
    )
    parser.add_argument(
        "--write-protocol-audit",
        action="store_true",
        help="Append a probe note into protocol-audit.md when it exists.",
    )
    args = parser.parse_args()

    run_root = Path(args.run_root).resolve()
    run_root.mkdir(parents=True, exist_ok=True)
    manifests_dir = run_root / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)

    try:
        codex_executable = resolve_codex_executable()
    except FileNotFoundError as exc:
        features = {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc)}
        exec_help = {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc)}
        codex_help = {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc)}
    else:
        features = run_command(codex_executable, ["features", "list"])
        exec_help = run_command(codex_executable, ["exec", "--help"])
        codex_help = run_command(codex_executable, ["--help"])
    multi_agent = parse_multi_agent(str(features["stdout"]))
    native_tooling = parse_native_tools(list(args.native_tool))

    if multi_agent["enabled"] and native_tooling["observed"]:
        recommended_mode = "native-multi-agent"
        assessment_notes = [
            "Feature flag and current-session native tool evidence are both present.",
            "Use native multi-agent first, but keep controller-owned audit and acceptance.",
        ]
    elif multi_agent["enabled"]:
        recommended_mode = "native-multi-agent-needs-fresh-tool-evidence"
        assessment_notes = [
            "Feature flag is enabled, but current-session native tool evidence was not recorded.",
            "Do not claim native multi-agent from flags alone; fall back unless live tools are confirmed.",
        ]
    else:
        recommended_mode = "artifact-orchestrated-swarm"
        assessment_notes = [
            "multi_agent is not enabled, so child codex exec orchestration is the honest default.",
            "Keep registry, outputs, and audit file-based.",
        ]

    result = {
        "probed_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_root": str(run_root),
        "multi_agent": multi_agent,
        "native_tooling": native_tooling,
        "commands": {
            "codex_executable": codex_executable if "codex_executable" in locals() else None,
            "codex_features_list": features,
            "codex_exec_help": exec_help,
            "codex_help": codex_help,
        },
        "assessment": {
            "recommended_mode": recommended_mode,
            "notes": assessment_notes,
        },
    }

    output_path = manifests_dir / "runtime-probe.json"
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.write_protocol_audit:
        audit_path = run_root / "protocol-audit.md"
        if audit_path.exists():
            note = (
                "\n## Runtime Probe\n\n"
                f"- Probe file: `{output_path}`\n"
                f"- multi_agent stage: `{multi_agent['stage']}`\n"
                f"- multi_agent enabled: `{multi_agent['enabled']}`\n"
                f"- Native tooling observed: `{native_tooling['observed']}`\n"
                f"- Native tools: `{', '.join(native_tooling['tools']) if native_tooling['tools'] else 'none'}`\n"
                f"- Recommended mode: `{result['assessment']['recommended_mode']}`\n"
            )
            with audit_path.open("a", encoding="utf-8") as handle:
                handle.write(note)

    print(f"PROBE_FILE={output_path}")
    print(f"MULTI_AGENT_ENABLED={multi_agent['enabled']}")
    print(f"NATIVE_TOOLING_OBSERVED={native_tooling['observed']}")
    print(f"NATIVE_TOOLS={','.join(native_tooling['tools'])}")
    print(f"RECOMMENDED_MODE={result['assessment']['recommended_mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
