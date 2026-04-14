#!/usr/bin/env python3
"""Run forward/regression prompts for codex-subagents-kit in a dedicated testbed."""

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


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def slugify_component(value: str) -> str:
    slug = re.sub(r"[^a-z0-9._-]+", "-", value.lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "case"


def ensure_project_agents(skill_root: Path, testbed_root: Path) -> list[str]:
    copied: list[str] = []
    source_dir = skill_root / "assets" / "project-agents"
    target_dir = testbed_root / ".codex" / "agents"
    target_dir.mkdir(parents=True, exist_ok=True)
    for source in sorted(source_dir.glob("*.toml")):
        target = target_dir / source.name
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        copied.append(source.name)

    scorer_path = target_dir / "scorer.toml"
    scorer_path.write_text(
        'name = "scorer"\n'
        'description = "Regression scorer for Codex skill outputs."\n'
        'developer_instructions = """\n'
        "Score outputs against the provided rubric and expected markers.\n"
        "Do not redesign the architecture unless the task explicitly asks for it.\n"
        "Return score breakdown, evidence pointers, and blockers.\n"
        '"""\n'
        'sandbox_mode = "read-only"\n',
        encoding="utf-8",
    )
    copied.append("scorer.toml")
    return copied


def build_config_text(skill_path: str, max_threads: int, max_depth: int) -> str:
    return f"""[features]
multi_agent = true

[agents]
max_threads = {max_threads}
max_depth = {max_depth}

[[skills.config]]
path = "{skill_path}"
enabled = true
"""


def build_agents_md() -> str:
    return """# AGENTS

## Purpose
- This cleanroom exists only to run forward/regression prompts against the local `codex-subagents-kit`.

## Team shape
- Controller keeps final synthesis and score ownership.
- `explorer` is read-only and maps evidence.
- `worker` is for bounded implementation tasks only.
- `reviewer` calls out risk, missing validation, and boundary mistakes.
- `verifier` checks regression and acceptance evidence.
- `scorer` applies the regression rubric and reports score deltas.

## Boundaries
- Keep repo norms in `AGENTS.md`.
- Keep tools/MCP decisions in runtime prompts.
- Keep temporary findings and score deltas in run artifacts, not in `AGENTS.md`.
- Do not search parent directories or historical run artifacts for the active case.

## Loop rules
- Every round must record stop-condition and fallback.
- Prefer summary-only returns with evidence paths.
- Do not claim `native-subagents` without explicit session evidence.
"""


def prepare_case_workspace(
    skill_root: Path,
    run_root: Path,
    label: str,
    case: dict[str, object],
    max_threads: int,
    max_depth: int,
) -> dict[str, object]:
    testbeds_root = (run_root.parent.parent / "testbeds").resolve()
    case_id = slugify_component(str(case["id"]))
    label_slug = slugify_component(label)
    testbed_root = (testbeds_root / run_root.name / label_slug / case_id).resolve()
    if testbeds_root not in testbed_root.parents:
        raise ValueError(f"Refusing to prepare cleanroom outside testbeds root: {testbed_root}")

    if testbed_root.exists():
        shutil.rmtree(testbed_root)

    copied_agents = ensure_project_agents(skill_root, testbed_root)
    skill_path = skill_root.as_posix()
    write_text(testbed_root / ".codex" / "config.toml", build_config_text(skill_path, max_threads, max_depth))
    write_text(testbed_root / "AGENTS.md", build_agents_md())
    write_text(
        testbed_root / "CASE_SCENARIO.md",
        (
            f"# Regression Case\n\n"
            f"- Case ID: `{case['id']}`\n"
            f"- Title: `{case['title']}`\n\n"
            "## User Request\n\n"
            f"{case['prompt']}\n"
        ),
    )

    manifest = {
        "prepared_at_utc": utc_now(),
        "testbed_root": str(testbed_root),
        "skill_root": str(skill_root),
        "case_id": str(case["id"]),
        "label": label,
        "copied_agents": copied_agents,
        "config_path": str(testbed_root / ".codex" / "config.toml"),
        "agents_md_path": str(testbed_root / "AGENTS.md"),
        "case_scenario_path": str(testbed_root / "CASE_SCENARIO.md"),
    }
    write_json(
        run_root / "manifests" / "testbeds" / f"{label_slug}--{case_id}.json",
        manifest,
    )
    return manifest


def build_prompt(case: dict[str, object]) -> str:
    request = str(case["prompt"]).replace("\r", " ").replace("\n", " ").strip()
    return (
        f"{request} "
        "额外约束：这条消息本身就是完整 case，不要要求我再提供 prompt；"
        "不要写“已理解/已对齐/请继续提供任务”这类元响应；"
        "只允许把当前 cleanroom 工作目录中的 AGENTS.md、.codex/config.toml、.codex/agents/*、CASE_SCENARIO.md 当作环境证据；"
        "不要搜索父目录、历史 run artifacts、旧 manifests、旧 logs；"
        "如果任务要求结构字段，就直接逐项给出。"
    )


def run_case(
    codex_executable: str,
    testbed_root: Path,
    prompt_text: str,
    output_file: Path,
    log_file: Path,
    sandbox: str,
    timeout_seconds: int,
) -> dict[str, object]:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    command = [
        codex_executable,
        "exec",
        "--ephemeral",
        "--sandbox",
        sandbox,
        "-C",
        str(testbed_root),
        "--output-last-message",
        str(output_file),
        "--skip-git-repo-check",
        prompt_text,
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        write_text(
            log_file,
            (
                f"COMMAND={' '.join(command)}\n"
                f"TIMEOUT_SECONDS={timeout_seconds}\n\n"
                "=== STDOUT ===\n"
                f"{exc.stdout or ''}\n\n"
                "=== STDERR ===\n"
                f"{exc.stderr or ''}\n"
            ),
        )
        return {
            "returncode": 124,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or f"Timed out after {timeout_seconds}s",
        }
    write_text(
        log_file,
        (
            f"COMMAND={' '.join(command)}\n"
            f"RETURN_CODE={completed.returncode}\n\n"
            "=== STDOUT ===\n"
            f"{completed.stdout}\n\n"
            "=== STDERR ===\n"
            f"{completed.stderr}\n"
        ),
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


MARKER_ALIASES = {
    "not warranted": [
        "warranted: no",
        "warranted = no",
        "warranted false",
        "不值得多智能体",
        "不值得 spawn",
        "not worth multi-agent",
        "not worth spawning",
    ],
    "why-not-spawn": [
        "why not spawn",
        "不值得 spawn",
        "不值得多智能体",
    ],
    "skills.config": [
        "[[skills.config]]",
        "skills config",
    ],
    "task-registry": [
        "task registry",
        "registry",
    ],
    "protocol-audit": [
        "protocol audit",
    ],
    "shared-findings": [
        "shared findings",
        "findings ledger",
    ],
    "summary": [
        "summary-only",
        "summary return",
        "summary-return",
        "evidence-dense summary",
    ],
    "official": [
        "官方",
    ],
    "engineering": [
        "工程",
    ],
    "tools": [
        "工具",
        "tooling",
    ],
    "runtime-state": [
        "runtime state",
        "runtime state boundary",
        "runtime-state-boundary",
        "运行时状态",
    ],
}


def contains_marker(text: str, marker: str, *, allow_alias: bool = True) -> bool:
    normalized_text = re.sub(r"\s+", " ", text.lower()).strip()
    variants = {
        marker.lower(),
        marker.lower().replace("-", "_"),
        marker.lower().replace("-", " "),
        marker.lower().replace("_", "-"),
        marker.lower().replace("_", " "),
    }
    if allow_alias:
        for alias in MARKER_ALIASES.get(marker.lower(), []):
            alias_lower = alias.lower()
            variants.update(
                {
                    alias_lower,
                    alias_lower.replace("-", "_"),
                    alias_lower.replace("-", " "),
                    alias_lower.replace("_", "-"),
                    alias_lower.replace("_", " "),
                }
            )
    return any(variant in normalized_text for variant in variants)


def score_case(case: dict[str, object], output_text: str, returncode: int) -> dict[str, object]:
    checks = []
    required_markers = list(case.get("required_markers", []))
    forbidden_markers = list(case.get("forbidden_markers", []))
    expected_topology = case.get("expected_topology")
    expected_runtime_mode = case.get("expected_runtime_mode")

    for marker in required_markers:
        checks.append(
            {
                "name": f"required:{marker}",
                "passed": contains_marker(output_text, marker, allow_alias=True),
            }
        )
    for marker in forbidden_markers:
        checks.append(
            {
                "name": f"forbidden:{marker}",
                "passed": not contains_marker(output_text, marker, allow_alias=False),
            }
        )
    topology_candidates = (
        [str(value) for value in expected_topology]
        if isinstance(expected_topology, list)
        else [str(expected_topology)]
    )
    mode_candidates = (
        [str(value) for value in expected_runtime_mode]
        if isinstance(expected_runtime_mode, list)
        else [str(expected_runtime_mode)]
    )
    checks.append(
        {
            "name": f"topology:{'|'.join(topology_candidates)}",
            "passed": any(contains_marker(output_text, candidate, allow_alias=False) for candidate in topology_candidates),
        }
    )
    checks.append(
        {
            "name": f"mode:{'|'.join(mode_candidates)}",
            "passed": any(contains_marker(output_text, candidate, allow_alias=False) for candidate in mode_candidates),
        }
    )
    checks.append({"name": "command-success", "passed": returncode == 0})
    score = sum(1 for check in checks if check["passed"])
    max_score = len(checks)
    return {
        "score": score,
        "max_score": max_score,
        "pass_rate": round((score / max_score) * 100, 1) if max_score else 0.0,
        "checks": checks,
        "status": "pass" if score == max_score else ("partial" if score > 0 else "fail"),
    }


def update_results_files(run_root: Path, round_record: dict[str, object]) -> None:
    iter_root = run_root / "outputs" / "iter-loop"
    iter_root.mkdir(parents=True, exist_ok=True)

    results_json_path = run_root / "manifests" / "iter-loop-results.json"
    if results_json_path.exists():
        payload = json.loads(results_json_path.read_text(encoding="utf-8"))
    else:
        payload = {
            "skill_name": "codex-subagents-kit",
            "status": "running",
            "rounds": [],
        }

    payload["updated_at_utc"] = utc_now()
    payload["status"] = "complete"
    payload["rounds"].append(round_record)
    payload["best_round_pass_rate"] = max(round_["pass_rate"] for round_ in payload["rounds"])
    write_text(results_json_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    tsv_path = iter_root / "results.tsv"
    if not tsv_path.exists():
        write_text(tsv_path, "round\tcase_count\tscore\tmax_score\tpass_rate\tstatus\tdescription\n")
    with tsv_path.open("a", encoding="utf-8") as handle:
        handle.write(
            f"{round_record['label']}\t{round_record['case_count']}\t{round_record['score']}\t"
            f"{round_record['max_score']}\t{round_record['pass_rate']}%\t"
            f"{round_record['status']}\t{round_record['description']}\n"
        )

    dashboard_path = iter_root / "dashboard.html"
    dashboard_path.write_text(
        """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>codex-subagents-kit iter-loop</title>
  <style>
    body { font-family: "Segoe UI", Arial, sans-serif; margin: 24px; background: #fbfcff; color: #1b1f2a; }
    h1, h2 { margin-bottom: 8px; }
    .pill { display:inline-block; padding:4px 10px; border-radius:999px; background:#e8eefc; margin-right:8px; }
    table { width:100%; border-collapse: collapse; margin-top: 16px; background: white; }
    th, td { border:1px solid #dde4f4; padding:8px; text-align:left; }
    th { background:#f0f4ff; }
    .ok { color:#11855d; }
    .warn { color:#9a6700; }
    .fail { color:#b42318; }
  </style>
</head>
<body>
  <h1>codex-subagents-kit iter-loop dashboard</h1>
  <p class="pill">Auto refresh: 10s</p>
  <p class="pill">Data file: manifests/iter-loop-results.json</p>
  <div id="status">Loading...</div>
  <table>
    <thead>
      <tr><th>Round</th><th>Cases</th><th>Score</th><th>Pass rate</th><th>Status</th><th>Description</th></tr>
    </thead>
    <tbody id="rows"></tbody>
  </table>
  <script>
    async function refresh() {
      const response = await fetch('../../manifests/iter-loop-results.json?_=' + Date.now());
      const data = await response.json();
      document.getElementById('status').innerText =
        `Status: ${data.status} | Updated: ${data.updated_at_utc || 'n/a'} | Best pass rate: ${data.best_round_pass_rate || 0}%`;
      const rows = document.getElementById('rows');
      rows.innerHTML = '';
      for (const round of (data.rounds || [])) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${round.label}</td>
          <td>${round.case_count}</td>
          <td>${round.score}/${round.max_score}</td>
          <td>${round.pass_rate}%</td>
          <td>${round.status}</td>
          <td>${round.description}</td>`;
        rows.appendChild(tr);
      }
    }
    refresh();
    setInterval(refresh, 10000);
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Run codex-subagents-kit forward/regression cases.")
    parser.add_argument("--run-root", required=True, help="Run root for artifacts.")
    parser.add_argument("--cases-file", required=True, help="Path to the JSON case list.")
    parser.add_argument("--label", required=True, help="Round label, e.g. baseline or round-1.")
    parser.add_argument("--sandbox", default="workspace-write", choices=("read-only", "workspace-write", "danger-full-access"))
    parser.add_argument("--max-threads", type=int, default=4)
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument(
        "--description",
        default="forward/regression round",
        help="Human-readable description stored in results.tsv/results.json.",
    )
    parser.add_argument("--case-timeout-seconds", type=int, default=420)
    parser.add_argument(
        "--case-id",
        action="append",
        default=[],
        help="Only run the specified case id. Repeatable.",
    )
    args = parser.parse_args()

    run_root = Path(args.run_root).resolve()
    run_root.mkdir(parents=True, exist_ok=True)
    skill_root = Path(__file__).resolve().parents[1]
    cases = read_json(Path(args.cases_file).resolve())
    if not isinstance(cases, list):
        print("cases-file must contain a JSON array.", file=sys.stderr)
        return 1
    if args.case_id:
        selected = set(args.case_id)
        cases = [case for case in cases if str(case.get("id")) in selected]
        if not cases:
            print("No cases matched --case-id.", file=sys.stderr)
            return 1

    try:
        codex_executable = resolve_codex_executable()
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    round_results = []
    round_prompts_root = run_root / "prompts" / "iter-loop" / args.label
    round_outputs_root = run_root / "outputs" / "iter-loop" / args.label
    round_logs_root = run_root / "logs" / "iter-loop" / args.label

    for case in cases:
        case_id = str(case["id"])
        testbed_manifest = prepare_case_workspace(
            skill_root=skill_root,
            run_root=run_root,
            label=args.label,
            case=case,
            max_threads=args.max_threads,
            max_depth=args.max_depth,
        )
        testbed_root = Path(str(testbed_manifest["testbed_root"]))
        prompt_text = build_prompt(case)
        prompt_path = round_prompts_root / f"{case_id}.md"
        output_path = round_outputs_root / f"{case_id}.md"
        log_path = round_logs_root / f"{case_id}.log"
        write_text(prompt_path, prompt_text)
        command_result = run_case(
            codex_executable=codex_executable,
            testbed_root=testbed_root,
            prompt_text=prompt_text,
            output_file=output_path,
            log_file=log_path,
            sandbox=args.sandbox,
            timeout_seconds=args.case_timeout_seconds,
        )
        output_text = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        score_result = score_case(case, output_text, int(command_result["returncode"]))
        round_results.append(
            {
                "id": case_id,
                "title": case["title"],
                "expected_topology": case["expected_topology"],
                "expected_runtime_mode": case["expected_runtime_mode"],
                "prompt_path": str(prompt_path),
                "output_path": str(output_path),
                "log_path": str(log_path),
                "testbed_root": str(testbed_root),
                "testbed_manifest": str(
                    run_root / "manifests" / "testbeds" / f"{slugify_component(args.label)}--{slugify_component(case_id)}.json"
                ),
                "returncode": int(command_result["returncode"]),
                **score_result,
            }
        )

    score = sum(result["score"] for result in round_results)
    max_score = sum(result["max_score"] for result in round_results)
    pass_rate = round((score / max_score) * 100, 1) if max_score else 0.0
    round_record = {
        "label": args.label,
        "created_at_utc": utc_now(),
        "description": args.description,
        "case_count": len(round_results),
        "score": score,
        "max_score": max_score,
        "pass_rate": pass_rate,
        "status": "keep" if pass_rate >= 85.0 else "review",
        "cases": round_results,
        "testbed_manifests_dir": str(run_root / "manifests" / "testbeds"),
    }

    write_text(
        round_outputs_root / "summary.md",
        "\n".join(
            [
                f"# Regression Round `{args.label}`",
                "",
                f"- Description: `{args.description}`",
                f"- Case count: `{len(round_results)}`",
                f"- Score: `{score}/{max_score}`",
                f"- Pass rate: `{pass_rate}%`",
                "",
                "## Cases",
                "",
                *[
                    f"- `{result['id']}` — `{result['score']}/{result['max_score']}` — `{result['status']}` — `{result['output_path']}`"
                    for result in round_results
                ],
            ]
        )
        + "\n",
    )
    write_text(
        run_root / "manifests" / f"iter-loop-{args.label}.json",
        json.dumps(round_record, indent=2, ensure_ascii=False) + "\n",
    )
    update_results_files(run_root, round_record)

    print(f"ROUND_LABEL={args.label}")
    print(f"ROUND_SCORE={score}/{max_score}")
    print(f"ROUND_PASS_RATE={pass_rate}")
    print(f"ROUND_SUMMARY={round_outputs_root / 'summary.md'}")
    print(f"TESTBED_ROOTS={run_root / 'manifests' / 'testbeds'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
