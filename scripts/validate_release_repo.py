#!/usr/bin/env python3
"""Validate that the public release repository has the minimum expected structure."""

from __future__ import annotations

import argparse
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


def require(path: Path, label: str, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"Missing {label}: {path}")


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Validate codex-subagents-kit release repository layout.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    errors: list[str] = []

    required_paths = {
        "README": repo_root / "README.md",
        "CHANGELOG": repo_root / "CHANGELOG.md",
        "LICENSE": repo_root / "LICENSE",
        "CONTRIBUTING": repo_root / "CONTRIBUTING.md",
        "SECURITY": repo_root / "SECURITY.md",
        "CODE_OF_CONDUCT": repo_root / "CODE_OF_CONDUCT.md",
        "GitHub about doc": repo_root / "docs" / "github-about.md",
        "triggering doc": repo_root / "docs" / "triggering-behavior.md",
        "history index": repo_root / "docs" / "history" / "chat-records-index.md",
        "reports index": repo_root / "reports" / "README.md",
        "GitHub workflow": repo_root / ".github" / "workflows" / "validate.yml",
        "skill dir": repo_root / "skills" / "codex-subagents-kit",
        "skill markdown": repo_root / "skills" / "codex-subagents-kit" / "SKILL.md",
        "selection guide": repo_root / "skills" / "codex-subagents-kit" / "references" / "selection-guide.md",
        "openai yaml": repo_root / "skills" / "codex-subagents-kit" / "agents" / "openai.yaml",
        "quick validate script": repo_root / "scripts" / "quick_validate_skill.py",
        "install script": repo_root / "scripts" / "install_skill.py",
        "repo validate script": repo_root / "scripts" / "validate_release_repo.py",
        "accepted live report": repo_root / "reports" / "score-report-release-eval-04-final-candidate.md",
        "accepted discoverability report": repo_root / "reports" / "discoverability-report-release-02-post-cutover.md",
        "final validation report": repo_root / "reports" / "final-release-validation-20260320.md",
    }

    for label, path in required_paths.items():
        require(path, label, errors)

    skill_md = required_paths["skill markdown"]
    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            errors.append("SKILL.md frontmatter missing")
        if "name: codex-subagents-kit" not in text:
            errors.append("SKILL.md does not declare expected skill name")
        if "Codex Subagents Kit" not in text:
            errors.append("SKILL.md title does not contain expected display title")

    openai_yaml = required_paths["openai yaml"]
    if openai_yaml.exists():
        text = openai_yaml.read_text(encoding="utf-8")
        if 'display_name: "Codex Subagents Kit"' not in text:
            errors.append("agents/openai.yaml missing expected display_name")
        if "$codex-subagents-kit" not in text:
            errors.append("agents/openai.yaml missing explicit $skill-name prompt guidance")

    for fixture_name, expected in {
        "baseline": "../../../skills/baseline-codex-agent-swarm",
        "release": "../../../skills/codex-subagents-kit",
    }.items():
        fixture_config = repo_root / "fixtures" / fixture_name / ".codex" / "config.toml"
        if fixture_config.exists():
            text = fixture_config.read_text(encoding="utf-8")
            if expected not in text:
                errors.append(f"fixtures/{fixture_name}/.codex/config.toml missing expected relative skills.config path")
        fixture_workspace = repo_root / "fixtures" / fixture_name / ".workspace"
        if fixture_workspace.exists():
            errors.append(f"fixtures/{fixture_name}/.workspace should not be committed")

    gitignore_path = repo_root / ".gitignore"
    if gitignore_path.exists():
        gitignore = gitignore_path.read_text(encoding="utf-8")
        for pattern in ("runs/", "**/.workspace/", "**/__pycache__/"):
            if pattern not in gitignore:
                errors.append(f".gitignore missing pattern: {pattern}")

    readme_path = repo_root / "README.md"
    if readme_path.exists():
        readme = readme_path.read_text(encoding="utf-8")
        for needle in (
            "Use $codex-subagents-kit",
            "discoverability",
            "implicit",
            "CHANGELOG.md",
            "docs/history/chat-records-index.md",
            "docs/github-about.md",
            "python scripts/quick_validate_skill.py --skill-dir skills/codex-subagents-kit",
        ):
            if needle not in readme:
                errors.append(f"README missing expected guidance: {needle}")

    if errors:
        print("STATUS=fail")
        for index, error in enumerate(errors, start=1):
            print(f"{index}. {error}")
        return 1

    print("STATUS=ok")
    print(f"REPO_ROOT={repo_root}")
    print("CHECKS=structure,skill-frontmatter,openai-yaml,fixture-configs,gitignore,readme")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
