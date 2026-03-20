# Skill Run Comparison

- Base: `E:\工作区\CODEX团队功能优化\skill-lab+\runs\20260320-release-eval-01`
- Candidate: `E:\工作区\CODEX团队功能优化\skill-lab+\runs\20260320-release-eval-02-post-cutover`

| Variant | Verdict | Score Delta | Input Token Delta | Output Token Delta | Regressions |
| --- | --- | --- | --- | --- | --- |
| baseline | PASS | -4 | 316 | 393 | none |
| release | FAIL | -2 | -39604 | -944 | artifact_rigor, invocation_integrity |
