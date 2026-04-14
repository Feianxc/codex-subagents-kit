1. `topology: 按你提供路径的 $codex-agent-swarm-optimized，推荐用 artifact-orchestrated 的 review-swarm：controller x1 + code reviewer x1 + security reviewer x1 + docs-consistency reviewer x1 + regression verifier x1；若目标运行时有 live native child-agent 证据，再无缝切到 native-subagents。`

2. `concurrency-budget: 默认并行 4 个子任务（code / security / docs / regression 各 1）；controller 只做串行的 preflight、registry、audit、scorecard 与最终裁决；若 regression 会抢占 CI/构建产物，则改成 3 review 并行 + 1 verifier 串后。`

3. `hot-file-policy: 源码与文档对子任务一律只读；每个子任务只写自己的 output file；task-registry.md、protocol-audit.md、scorecard.md 由 controller 独占写；禁止两个子任务并发写同一 artifact、测试快照或汇总文件。`

4. `review-separation: 实现者不能成为唯一审查者；code / security / docs / regression 四条线独立 owner、独立 acceptance、独立证据；security review 不并入 code review，regression verifier 只基于待测变更与测试入口给可复现结论。`

5. `scorecard: 采用“双层卡”——流程层看 mode-selection、context efficiency、spawn quality、audit honesty；结果层看 code risk、security findings、docs drift、regression status；出门条件=四条线都有证据且无 Blocker，任何一条缺证据都算未完成。`

**过程复盘：** 我先按你给的路径读取了 `SKILL.md`，再只补读了 `selection-guide.md`、`topology-catalog.md`、`multi-agent-hardening.md`、`artifact-contract.md` 这 4 个与队形/并发/热文件/评分直接相关的参考；未实际启动子 agent，只输出了可落地的编排方案。  
**提示词优化版：** 请基于 `optimized-codex-agent-swarm` skill，为一个包含代码审查、安全审查、文档一致性审查和回归验证的 Codex 工作流，给出拓扑、并发预算、热文件策略、审查隔离规则和评分卡。