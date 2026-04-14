#!/usr/bin/env python3
"""Probe local Codex runtime facts for swarm orchestration decisions."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import tomllib


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


def classify_session_gate(native_tooling: dict[str, object]) -> dict[str, object]:
    tools = [str(tool) for tool in native_tooling.get("tools", [])]
    source = str(native_tooling.get("source", "none"))
    direct_native_tools = {"spawn_agent", "send_input", "wait_agent", "resume_agent", "close_agent"}
    observed_direct = [tool for tool in tools if tool in direct_native_tools]

    if observed_direct and source == "cli-args":
        confidence = "strong"
        passed = True
        notes = [
            "Live session tool evidence was recorded explicitly.",
            "This is stronger than relying on feature flags or config alone.",
        ]
    elif observed_direct:
        confidence = "medium"
        passed = True
        notes = [
            "Native child-agent tools were observed indirectly.",
            "Treat this as usable evidence, but less direct than explicit live-session observation.",
        ]
    elif tools:
        confidence = "weak"
        passed = True
        notes = [
            "Some native-tool evidence was recorded, but not the core child-agent control tools.",
            "Do not over-claim native-subagents without corroborating evidence.",
        ]
    else:
        confidence = "none"
        passed = False
        notes = [
            "No live native child-agent tool evidence was recorded.",
            "Feature flags and config may still justify config-guided setup, but not native-subagents claims.",
        ]

    return {
        "pass": passed,
        "confidence": confidence,
        "observed_tools": observed_direct,
        "notes": notes,
    }


def read_toml_if_exists(path: Path) -> dict[str, object]:
    if not path.exists() or not path.is_file():
        return {}
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except Exception:
        return {}


def extract_agents_config(config: dict[str, object]) -> dict[str, object]:
    agents = config.get("agents", {})
    if not isinstance(agents, dict):
        return {}
    return {
        "max_threads": agents.get("max_threads"),
        "max_depth": agents.get("max_depth"),
        "defined_roles": sorted(k for k, v in agents.items() if isinstance(v, dict)),
    }


def extract_skills_config_count(config: dict[str, object]) -> int | None:
    skills = config.get("skills")
    if not isinstance(skills, dict):
        return None
    cfg = skills.get("config")
    if isinstance(cfg, list):
        return len(cfg)
    return None


def build_config_guided_evidence(
    home_config_path: Path,
    project_config_path: Path,
    global_agents_dir: Path,
    project_agents_dir: Path,
    home_snapshot: dict[str, object],
    project_snapshot: dict[str, object],
) -> dict[str, object]:
    signals: list[str] = []
    if project_agents_dir.exists():
        signals.append("project_agents_dir")
    if global_agents_dir.exists():
        signals.append("global_agents_dir")
    if project_config_path.exists():
        signals.append("project_config")
    if home_config_path.exists():
        signals.append("home_config")
    if project_snapshot.get("defined_roles"):
        signals.append("project_agent_roles")
    if home_snapshot.get("defined_roles"):
        signals.append("home_agent_roles")
    if project_snapshot.get("skills_config_count"):
        signals.append("project_skills_config")
    if home_snapshot.get("skills_config_count"):
        signals.append("home_skills_config")

    return {
        "available": bool(signals),
        "signals": signals,
        "notes": (
            [
                "Project or home Codex config artifacts were found.",
                "These support config-guided subagent setup, but they are not proof of live native session tooling.",
            ]
            if signals
            else ["No project/home config-guided subagent evidence was found."]
        ),
    }


def contains_pattern(command_result: dict[str, object], pattern: str) -> bool:
    if not command_result.get("ok"):
        return False
    stdout = str(command_result.get("stdout", ""))
    return re.search(pattern, stdout, flags=re.IGNORECASE) is not None


def main() -> int:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = argparse.ArgumentParser(description="Probe Codex runtime facts for swarm skills.")
    parser.add_argument("--run-root", required=True, help="Run root where audit files live.")
    parser.add_argument("--workspace-root", default=".", help="Workspace root to inspect for project config.")
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
    workspace_root = Path(args.workspace_root).resolve()
    run_root.mkdir(parents=True, exist_ok=True)
    manifests_dir = run_root / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)

    try:
        codex_executable = resolve_codex_executable()
    except FileNotFoundError as exc:
        features = {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc)}
        exec_help = {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc)}
        codex_help = {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc)}
        version = {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc)}
    else:
        version = run_command(codex_executable, ["--version"])
        features = run_command(codex_executable, ["features", "list"])
        exec_help = run_command(codex_executable, ["exec", "--help"])
        codex_help = run_command(codex_executable, ["--help"])
    multi_agent = parse_multi_agent(str(features["stdout"]))
    native_tooling = parse_native_tools(list(args.native_tool))

    home_config_path = Path.home() / ".codex" / "config.toml"
    project_config_path = workspace_root / ".codex" / "config.toml"
    home_config = read_toml_if_exists(home_config_path)
    project_config = read_toml_if_exists(project_config_path)
    global_agents_dir = Path.home() / ".codex" / "agents"
    project_agents_dir = workspace_root / ".codex" / "agents"

    home_agents_snapshot = extract_agents_config(home_config)
    project_agents_snapshot = extract_agents_config(project_config)
    home_skills_config_count = extract_skills_config_count(home_config)
    project_skills_config_count = extract_skills_config_count(project_config)
    if home_skills_config_count is not None:
        home_agents_snapshot["skills_config_count"] = home_skills_config_count
    if project_skills_config_count is not None:
        project_agents_snapshot["skills_config_count"] = project_skills_config_count

    product_gate = {
        "pass": bool(multi_agent["enabled"]),
        "notes": (
            [
                "The `multi_agent` feature flag is enabled.",
                "This is product-layer support only; it does not prove current-session native tooling.",
            ]
            if multi_agent["enabled"]
            else [
                "The `multi_agent` feature flag was not observed as enabled.",
                "Default to artifact-orchestrated-swarm unless independent product evidence exists.",
            ]
        ),
    }
    session_gate = classify_session_gate(native_tooling)
    config_guided_evidence = build_config_guided_evidence(
        home_config_path=home_config_path,
        project_config_path=project_config_path,
        global_agents_dir=global_agents_dir,
        project_agents_dir=project_agents_dir,
        home_snapshot=home_agents_snapshot,
        project_snapshot=project_agents_snapshot,
    )
    exec_capability = {
        "available": bool(exec_help.get("ok")),
        "supports_output_last_message": contains_pattern(exec_help, r"output-last-message"),
        "supports_json": contains_pattern(exec_help, r"--json"),
    }

    if product_gate["pass"] and session_gate["pass"]:
        recommended_mode = "native-subagents"
        assessment_notes = [
            "Product Gate and Session Gate both pass.",
            "Use native-subagents first, but keep controller-owned audit and acceptance.",
        ]
    elif product_gate["pass"] and config_guided_evidence["available"]:
        recommended_mode = "config-guided-codex-subagents"
        assessment_notes = [
            "Product Gate passes, but Session Gate is not strong enough for native-subagents claims.",
            "Prefer config-guided project setup; do not claim native-subagents from feature flags or config alone.",
        ]
    elif product_gate["pass"]:
        recommended_mode = "config-guided-codex-subagents"
        assessment_notes = [
            "Product Gate passes, but no strong session or config-guided evidence was recorded.",
            "Config-guided setup is still the more honest default than claiming native-subagents.",
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
        "workspace_root": str(workspace_root),
        "multi_agent": multi_agent,
        "native_tooling": native_tooling,
        "paths": {
            "home_config_path": str(home_config_path),
            "project_config_path": str(project_config_path),
            "global_agents_dir": str(global_agents_dir),
            "project_agents_dir": str(project_agents_dir),
        },
        "filesystem": {
            "global_agents_dir_exists": global_agents_dir.exists(),
            "project_agents_dir_exists": project_agents_dir.exists(),
            "home_config_exists": home_config_path.exists(),
            "project_config_exists": project_config_path.exists(),
        },
        "config_snapshot": {
            "home_agents": home_agents_snapshot,
            "project_agents": project_agents_snapshot,
            "home_skills_config_count": home_skills_config_count,
            "project_skills_config_count": project_skills_config_count,
        },
        "commands": {
            "codex_executable": codex_executable if "codex_executable" in locals() else None,
            "codex_version": version,
            "codex_features_list": features,
            "codex_exec_help": exec_help,
            "codex_help": codex_help,
        },
        "gates": {
            "product_gate": product_gate,
            "session_gate": session_gate,
        },
        "config_guided_evidence": config_guided_evidence,
        "exec_capability": exec_capability,
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
                f"- Codex version: `{version['stdout']}`\n"
                f"- multi_agent stage: `{multi_agent['stage']}`\n"
                f"- multi_agent enabled: `{multi_agent['enabled']}`\n"
                f"- Product Gate: `{product_gate['pass']}`\n"
                f"- Session Gate: `{session_gate['pass']}`\n"
                f"- Session confidence: `{session_gate['confidence']}`\n"
                f"- Native tooling observed: `{native_tooling['observed']}`\n"
                f"- Native tools: `{', '.join(native_tooling['tools']) if native_tooling['tools'] else 'none'}`\n"
                f"- Config-guided evidence: `{config_guided_evidence['available']}`\n"
                f"- Config-guided signals: `{', '.join(config_guided_evidence['signals']) if config_guided_evidence['signals'] else 'none'}`\n"
                f"- Global agents dir exists: `{global_agents_dir.exists()}`\n"
                f"- Project agents dir exists: `{project_agents_dir.exists()}`\n"
                f"- Recommended mode: `{result['assessment']['recommended_mode']}`\n"
            )
            with audit_path.open("a", encoding="utf-8") as handle:
                handle.write(note)

    print(f"PROBE_FILE={output_path}")
    print(f"CODEX_VERSION={version['stdout']}")
    print(f"PRODUCT_GATE={product_gate['pass']}")
    print(f"SESSION_GATE={session_gate['pass']}")
    print(f"SESSION_CONFIDENCE={session_gate['confidence']}")
    print(f"MULTI_AGENT_ENABLED={multi_agent['enabled']}")
    print(f"NATIVE_TOOLING_OBSERVED={native_tooling['observed']}")
    print(f"NATIVE_TOOLS={','.join(native_tooling['tools'])}")
    print(f"CONFIG_GUIDED_EVIDENCE={config_guided_evidence['available']}")
    print(f"RECOMMENDED_MODE={result['assessment']['recommended_mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
