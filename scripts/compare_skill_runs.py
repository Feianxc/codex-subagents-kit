#!/usr/bin/env python3
"""Compare two scored skill-lab runs and flag regressions."""

from __future__ import annotations

import argparse
import json
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


def load_summary(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def compare_variant(base: dict[str, object], candidate: dict[str, object]) -> dict[str, object]:
    base_dims = base["dimension_scores"]
    cand_dims = candidate["dimension_scores"]

    guarded_dims = [
        "codex_alignment",
        "mode_selection",
        "topology_quality",
        "context_efficiency",
        "artifact_rigor",
        "invocation_integrity",
    ]
    regressions = [
        dim for dim in guarded_dims if cand_dims.get(dim, 0) < base_dims.get(dim, 0)
    ]

    token_delta = candidate["usage"]["avg_input_tokens"] - base["usage"]["avg_input_tokens"]
    output_delta = candidate["usage"]["avg_output_tokens"] - base["usage"]["avg_output_tokens"]
    total_delta = sum(cand_dims.values()) - sum(base_dims.values())

    verdict = "PASS"
    if regressions:
        verdict = "FAIL"
    elif token_delta > max(5000, round(base["usage"]["avg_input_tokens"] * 0.15)):
        verdict = "WARN"

    return {
        "verdict": verdict,
        "regressions": regressions,
        "token_delta": token_delta,
        "output_token_delta": output_delta,
        "total_score_delta": total_delta,
    }


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Compare two scored skill-lab runs.")
    parser.add_argument("--base-summary", required=True, help="Path to base score-summary.json")
    parser.add_argument("--candidate-summary", required=True, help="Path to candidate score-summary.json")
    parser.add_argument("--report-file", help="Optional report file path")
    args = parser.parse_args()

    base = load_summary(Path(args.base_summary).resolve())
    candidate = load_summary(Path(args.candidate_summary).resolve())

    report = {
        "base_run_root": base["run_root"],
        "candidate_run_root": candidate["run_root"],
        "variants": {},
    }

    lines = [
        "# Skill Run Comparison",
        "",
        f"- Base: `{base['run_root']}`",
        f"- Candidate: `{candidate['run_root']}`",
        "",
        "| Variant | Verdict | Score Delta | Input Token Delta | Output Token Delta | Regressions |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for variant in sorted(set(base["scores"]).intersection(candidate["scores"])):
        result = compare_variant(base["scores"][variant], candidate["scores"][variant])
        report["variants"][variant] = result
        regressions = ", ".join(result["regressions"]) if result["regressions"] else "none"
        lines.append(
            f"| {variant} | {result['verdict']} | {result['total_score_delta']} | {result['token_delta']} | {result['output_token_delta']} | {regressions} |"
        )

    report_path = Path(args.report_file).resolve() if args.report_file else Path(args.candidate_summary).resolve().parent / "comparison-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    json_path = report_path.with_suffix(".json")
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"COMPARISON_REPORT={report_path}")
    print(f"COMPARISON_JSON={json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
