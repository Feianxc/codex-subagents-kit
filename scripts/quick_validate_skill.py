#!/usr/bin/env python3
"""Quick, self-contained validation for a Codex skill directory."""

from __future__ import annotations

import argparse
import re
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


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Validate a Codex skill folder.")
    parser.add_argument("--skill-dir", default="skills/codex-subagents-kit", help="Path to the skill directory.")
    parser.add_argument("--expected-name", default="codex-subagents-kit", help="Expected skill slug.")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    skill_md = skill_dir / "SKILL.md"
    openai_yaml = skill_dir / "agents" / "openai.yaml"
    errors: list[str] = []

    if not skill_dir.exists():
        errors.append(f"Skill directory not found: {skill_dir}")
    if not skill_md.exists():
        errors.append(f"Missing SKILL.md: {skill_md}")
    if not openai_yaml.exists():
        errors.append(f"Missing agents/openai.yaml: {openai_yaml}")

    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            errors.append("SKILL.md frontmatter missing")
        if f"name: {args.expected_name}" not in text:
            errors.append(f"SKILL.md missing expected name: {args.expected_name}")
        if "description:" not in text:
            errors.append("SKILL.md missing description field")
        if re.search(r"^#\s+", text, flags=re.MULTILINE) is None:
            errors.append("SKILL.md missing top-level markdown title")

    if openai_yaml.exists():
        yaml_text = openai_yaml.read_text(encoding="utf-8")
        if 'display_name: "Codex Subagents Kit"' not in yaml_text:
            errors.append("agents/openai.yaml missing expected display_name")
        if "$codex-subagents-kit" not in yaml_text:
            errors.append("agents/openai.yaml missing explicit $skill-name prompt guidance")

    if errors:
        print("STATUS=fail")
        for i, error in enumerate(errors, start=1):
            print(f"{i}. {error}")
        return 1

    print("STATUS=ok")
    print(f"SKILL_DIR={skill_dir}")
    print("CHECKS=exists,frontmatter,description,title,openai-yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
