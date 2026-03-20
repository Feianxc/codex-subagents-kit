#!/usr/bin/env python3
"""Score discoverability evaluation results."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
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
    parser = argparse.ArgumentParser(description="Score discoverability evaluation results.")
    parser.add_argument("--run-root", required=True, help="Path to discoverability run root.")
    parser.add_argument("--report-file", help="Optional markdown report path.")
    args = parser.parse_args()

    run_root = Path(args.run_root).resolve()
    manifest = json.loads((run_root / "manifest.json").read_text(encoding="utf-8"))
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for item in manifest["results"]:
        grouped[(item["variant"], item["load_mode"], item["case"])].append(item)

    variant_totals: dict[str, dict[str, object]] = defaultdict(lambda: {"attempts": 0, "successes": 0, "input_tokens": 0, "output_tokens": 0})
    lines = [
        "# Discoverability Report",
        "",
        f"- Run Root: `{run_root}`",
        "",
        "| Variant | Load Mode | Case | Success Rate | Avg Input Tokens | Avg Output Tokens |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    detailed: dict[str, object] = {}

    for (variant, load_mode, case), items in sorted(grouped.items()):
        attempts = len(items)
        successes = sum(1 for item in items if item["success"])
        avg_input = round(sum(item["usage"]["input_tokens"] for item in items) / attempts)
        avg_output = round(sum(item["usage"]["output_tokens"] for item in items) / attempts)
        success_rate = round(100 * successes / attempts)
        lines.append(f"| {variant} | {load_mode} | {case} | {success_rate}% ({successes}/{attempts}) | {avg_input} | {avg_output} |")

        bucket = variant_totals[variant]
        bucket["attempts"] += attempts
        bucket["successes"] += successes
        bucket["input_tokens"] += sum(item["usage"]["input_tokens"] for item in items)
        bucket["output_tokens"] += sum(item["usage"]["output_tokens"] for item in items)
        detailed[f"{variant}:{load_mode}:{case}"] = {
            "attempts": attempts,
            "successes": successes,
            "success_rate_percent": success_rate,
            "avg_input_tokens": avg_input,
            "avg_output_tokens": avg_output,
        }

    lines.extend(["", "## Variant Summary", ""])
    for variant, bucket in sorted(variant_totals.items()):
        attempts = bucket["attempts"]
        successes = bucket["successes"]
        avg_input = round(bucket["input_tokens"] / attempts) if attempts else 0
        avg_output = round(bucket["output_tokens"] / attempts) if attempts else 0
        success_rate = round(100 * successes / attempts) if attempts else 0
        lines.append(
            f"- **{variant}**: success_rate={success_rate}% ({successes}/{attempts}), avg_input_tokens={avg_input}, avg_output_tokens={avg_output}"
        )
        bucket["success_rate_percent"] = success_rate
        bucket["avg_input_tokens"] = avg_input
        bucket["avg_output_tokens"] = avg_output

    summary = {
        "run_root": str(run_root),
        "variant_totals": variant_totals,
        "details": detailed,
    }
    (run_root / "discoverability-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report_path = Path(args.report_file).resolve() if args.report_file else run_root / "discoverability-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

    print(f"DISCOVERABILITY_SUMMARY={run_root / 'discoverability-summary.json'}")
    print(f"DISCOVERABILITY_REPORT={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
