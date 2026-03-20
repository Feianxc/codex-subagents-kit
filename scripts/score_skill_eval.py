#!/usr/bin/env python3
"""Score baseline vs release skill-lab results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FAILURE_PATTERNS = ("未找到该技能", "未发现可用技能", "回退", "fallback")


def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def has_failure_pattern(text: str) -> bool:
    lower = text.lower()
    return any(pattern.lower() in lower for pattern in FAILURE_PATTERNS)


def pattern_score(text: str, patterns: list[str], points: int) -> tuple[int, list[str]]:
    hits = [pattern for pattern in patterns if pattern.lower() in text.lower()]
    if not patterns:
        return points, hits
    score = round(points * len(hits) / len(patterns))
    return score, hits


def score_variant(run_root: Path, variant: str) -> dict[str, object]:
    smoke = load_text(run_root / variant / "smoke" / "response.md")
    mode = load_text(run_root / variant / "mode-selection" / "response.md")
    topology = load_text(run_root / variant / "topology" / "response.md")
    context = load_text(run_root / variant / "context-efficiency" / "response.md")

    metrics: list[dict[str, int]] = []
    for case in ["smoke", "mode-selection", "topology", "context-efficiency"]:
        meta_path = run_root / variant / case / "meta.json"
        if meta_path.exists():
            metrics.append(json.loads(meta_path.read_text(encoding="utf-8")))

    avg_output_tokens = 0
    avg_input_tokens = 0
    avg_chars = 0
    if metrics:
        avg_output_tokens = round(sum(m["usage"]["output_tokens"] for m in metrics) / len(metrics))
        avg_input_tokens = round(sum(m["usage"]["input_tokens"] for m in metrics) / len(metrics))
        avg_chars = round(sum(m["response_chars"] for m in metrics) / len(metrics))

    all_text = "\n".join([smoke, mode, topology, context])
    failure_cases = [
        case_name
        for case_name, text in (
            ("smoke", smoke),
            ("mode-selection", mode),
            ("topology", topology),
            ("context-efficiency", context),
        )
        if has_failure_pattern(text)
    ]

    codex_alignment_score, codex_hits = pattern_score(
        all_text,
        ["subagents", ".codex/agents", "skills.config", "codex", "config-guided", "native-subagents"],
        20,
    )
    mode_score, mode_hits = pattern_score(
        mode,
        ["mode:", "config-guided", "native", ".codex/agents", "skills.config"],
        20,
    )
    topology_score, topology_hits = pattern_score(
        topology,
        ["topology:", "concurrency", "hot-file", "review", "security", "regression", "scorecard"],
        20,
    )
    context_score, context_hits = pattern_score(
        context,
        ["load-first", "do-not-load-yet", "child-prompt", "cli", "script", "token"],
        20,
    )
    artifact_score, artifact_hits = pattern_score(
        smoke + "\n" + topology,
        ["artifact-core", "registry", "audit", "scorecard"],
        10,
    )
    invocation_integrity = 0 if len(failure_cases) == 4 else max(0, 10 - 3 * len(failure_cases))

    return {
        "variant": variant,
        "dimension_scores": {
            "codex_alignment": codex_alignment_score,
            "mode_selection": mode_score,
            "topology_quality": topology_score,
            "context_efficiency": context_score,
            "artifact_rigor": artifact_score,
            "invocation_integrity": invocation_integrity,
        },
        "hits": {
            "codex_alignment": codex_hits,
            "mode_selection": mode_hits,
            "topology_quality": topology_hits,
            "context_efficiency": context_hits,
            "artifact_rigor": artifact_hits,
            "failure_cases": failure_cases,
        },
        "usage": {
            "avg_input_tokens": avg_input_tokens,
            "avg_output_tokens": avg_output_tokens,
            "avg_response_chars": avg_chars,
        },
    }


def apply_token_efficiency(scores: dict[str, dict[str, object]]) -> None:
    output_tokens = {
        variant: data["usage"]["avg_output_tokens"]
        for variant, data in scores.items()
    }
    min_tokens = min(token for token in output_tokens.values() if token > 0)

    for variant, data in scores.items():
        own_tokens = data["usage"]["avg_output_tokens"]
        if own_tokens <= 0:
            token_score = 0
        elif own_tokens == min_tokens:
            token_score = 10
        else:
            ratio = min_tokens / own_tokens
            token_score = max(6, round(10 * ratio))
        data["dimension_scores"]["token_efficiency"] = token_score


def build_report(run_root: Path, scores: dict[str, dict[str, object]]) -> str:
    lines = [
        "# Skill Lab Score Report",
        "",
        f"- Run Root: `{run_root}`",
        "",
        "| Variant | Codex Alignment | Mode Selection | Topology | Context Efficiency | Artifact Rigor | Invocation Integrity | Token Efficiency | Total |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for variant, data in scores.items():
        dims = data["dimension_scores"]
        total = sum(dims.values())
        lines.append(
            f"| {variant} | {dims['codex_alignment']} | {dims['mode_selection']} | {dims['topology_quality']} | {dims['context_efficiency']} | {dims['artifact_rigor']} | {dims['invocation_integrity']} | {dims['token_efficiency']} | {total} |"
        )

    lines.extend(["", "## Usage", ""])
    for variant, data in scores.items():
        usage = data["usage"]
        lines.append(
            f"- **{variant}**: avg_input_tokens={usage['avg_input_tokens']}, avg_output_tokens={usage['avg_output_tokens']}, avg_response_chars={usage['avg_response_chars']}"
        )

    lines.extend(["", "## Pattern Hits", ""])
    for variant, data in scores.items():
        lines.append(f"### {variant}")
        for dimension, hits in data["hits"].items():
            lines.append(f"- {dimension}: {', '.join(hits) if hits else 'none'}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = argparse.ArgumentParser(description="Score skill-lab run results.")
    parser.add_argument("--run-root", required=True, help="Path to a run folder under skill-lab/runs.")
    parser.add_argument("--report-file", help="Optional markdown report output path.")
    args = parser.parse_args()

    run_root = Path(args.run_root).resolve()
    scores = {
        "baseline": score_variant(run_root, "baseline"),
        "release": score_variant(run_root, "release"),
    }
    apply_token_efficiency(scores)

    summary = {
        "run_root": str(run_root),
        "scores": scores,
    }
    summary_path = run_root / "score-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = build_report(run_root, scores)
    report_path = Path(args.report_file).resolve() if args.report_file else run_root / "score-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    print(f"SCORE_SUMMARY={summary_path}")
    print(f"SCORE_REPORT={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
