# Skill Lab Score Report

- Run Root: `E:\工作区\CODEX团队功能优化\skill-lab+\runs\20260320-release-eval-03-wording-hardened`

| Variant | Codex Alignment | Mode Selection | Topology | Context Efficiency | Artifact Rigor | Invocation Integrity | Token Efficiency | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 3 | 8 | 20 | 20 | 10 | 7 | 6 | 74 |
| release | 20 | 20 | 20 | 20 | 8 | 10 | 10 | 108 |

## Usage

- **baseline**: avg_input_tokens=126899, avg_output_tokens=3379, avg_response_chars=884
- **release**: avg_input_tokens=35109, avg_output_tokens=1899, avg_response_chars=662

## Pattern Hits

### baseline
- codex_alignment: codex
- mode_selection: mode:, native
- topology_quality: topology:, concurrency, hot-file, review, security, regression, scorecard
- context_efficiency: load-first, do-not-load-yet, child-prompt, cli, script, token
- artifact_rigor: artifact-core, registry, audit, scorecard
- failure_cases: topology

### release
- codex_alignment: subagents, .codex/agents, skills.config, codex, config-guided, native-subagents
- mode_selection: mode:, config-guided, native, .codex/agents, skills.config
- topology_quality: topology:, concurrency, hot-file, review, security, regression, scorecard
- context_efficiency: load-first, do-not-load-yet, child-prompt, cli, script, token
- artifact_rigor: artifact-core, audit, scorecard
- failure_cases: none
