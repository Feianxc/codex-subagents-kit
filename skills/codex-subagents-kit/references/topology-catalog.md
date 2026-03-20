# Topology Catalog

## research-swarm

- controller x1
- explorer x2~3
- synthesizer/reviewer x1
- 适合：资料调研、架构摸底、最佳实践对比

## delivery-swarm

- controller x1
- explorer x1
- worker x1~2
- verifier x1
- 适合：中等规模实现 + 回归

## bugfix-swarm

- reproducer x1
- root-cause explorer x1
- patch worker x1
- regression verifier x1
- 适合：Bug 复现、根因分析、修复、回归闭环

## review-swarm

- controller x1
- code reviewer x1
- security reviewer x1
- docs reviewer x1
- 适合：PR 审查、变更风险评估、交付前检查

## Concurrency Budget Defaults

- explorer: 2~4
- writer: 1~2
- reviewer/verifier: 1
- same hot file writers: 0 concurrent

若没有 worktree / branch / file partition 证据，不要提升 writer 并发。
