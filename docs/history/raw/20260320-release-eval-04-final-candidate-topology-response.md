1. `topology: 默认选 \`artifact-orchestrated-swarm\` 的 \`review-swarm + regression verifier\`：\`controller x1\` 统筹，\`code reviewer x1\`、\`security reviewer x1\`、\`docs reviewer x1\`、\`regression verifier x1\` 独立产出；因当前未做 runtime probe、无 live native child-agent 证据，不宣称 \`native-subagents\`。`
2. `concurrency-budget: 子任务并发上限 4（3 个 review + 1 个 verifier）；若测试资源紧张则降到 3，把 regression 放第二波；\`controller\` 固定保留 preflight、mode selection、registry、final merge、scorecard。`
3. `hot-file-policy: 本流程默认只读；所有子任务只写各自 artifact（如 \`outputs/code-review.md\`、\`outputs/security.md\`、\`outputs/docs.md\`、\`outputs/regression.md\`）；若后续进入修复，任何同一 hot file 同时只允许 1 个 writer，先 analysis-first，再由 controller 合并。`
4. `review-separation: 代码 / 安全 / 文档一致性 / 回归验证四条线分离；实现者不能兼任唯一 reviewer；security 与 docs 不并入 code review，regression 只对变更集和关键路径给出可复验结论。`
5. `scorecard: 6 维评分——\`Codex alignment\`、\`Context efficiency\`、\`Mode-selection accuracy\`、\`Spawn quality\`、\`Validation/acceptance\`、\`Audit honesty\`；通过线建议 ≥4/5，且必须具备 \`task-registry\`、\`protocol-audit\`、\`team-report\`、\`scorecard\` 与 acceptance 记录。`

过程复盘：拆成模式选择、拓扑、并发、热文件、审查分离、scorecard 六块；只读取了 `selection-guide.md`、`topology-catalog.md`、`multi-agent-hardening.md`、`artifact-contract.md` 四份最小必要文档；未做 runtime probe，所以保守走 artifact 模式；最终只影响工作流设计，无代码或全局配置变更。

提示词优化：请基于 `$codex-subagents-kit`，为“代码审查 + 安全审查 + 文档一致性审查 + 回归验证”设计一个紧凑的 Codex review workflow，并输出 `topology`、`concurrency-budget`、`hot-file-policy`、`review-separation`、`scorecard`。