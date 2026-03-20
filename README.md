# Codex Subagents Kit

面向 Codex 的 **Subagents / `.codex/agents/` / `skills.config` / artifact-based orchestration** 技能与测试仓库。

这个仓库的目标不是把 Codex 神化成“自动团队 runtime”，而是提供一套 **符合当前 Codex 真实机制** 的：

- 多智能体编排方法
- 上下文压缩方法
- 可验证的 artifacts / audit / scorecard 闭环
- discoverability 与 token 效率测试资产

## 仓库结构

- `skills/codex-subagents-kit/`
  - 最终公开发布 skill
- `skills/baseline-codex-agent-swarm/`
  - 回归测试对照 baseline
- `fixtures/`
  - 独立测试工作区
- `prompts/`
  - live / discoverability prompt 模板
- `scripts/`
  - 评测、打分、对比、全局 smoke 工具
- `reports/`
  - 已纳入版本控制的报告摘要
- `runs/`
  - 本地原始运行产物（默认不提交）

## 最终命名

- Skill slug：`codex-subagents-kit`
- Display name：`Codex Subagents Kit`

命名原则：

1. 对齐 Codex 当前公开/本机可观察机制里的 **Subagents**
2. 避免 `swarm / optimized` 这类实验味或过度承诺式命名
3. 保留产品化表达，但不假装存在未证实的原生 team runtime

## 主要能力

- 四层门控：
  - Product Gate
  - Session Gate
  - Policy Gate
  - Task Gate
- 模式选择：
  - `single-controller`
  - `native-subagents`
  - `config-guided-codex-subagents`
  - `artifact-orchestrated-swarm`
- 上下文控制：
  - 薄核心、深引用、按需读取
- 工程闭环：
  - `run_root`
  - `registry`
  - `audit`
  - `scorecard`

## 安装

### 本机全局安装

将 `skills/codex-subagents-kit/` 复制到：

```text
~/.codex/skills/codex-subagents-kit
```

Windows PowerShell 示例：

```powershell
Copy-Item -Recurse -Force `
  ".\skills\codex-subagents-kit" `
  "$HOME\.codex\skills\codex-subagents-kit"
```

## 推荐调用方式

优先：

```text
Use $codex-subagents-kit
```

需要最高确定性时：

```text
Use $codex-subagents-kit at <skill-path>
```

## 测试结论摘要

截至 **2026-03-20**，当前接受版证据为：

- live eval 最优版：
  - `reports/score-report-release-eval-04-final-candidate.md`
- discoverability 最优版：
  - `reports/discoverability-report-release-02-post-cutover.md`

核心结果：

- live eval：`release = 110`
- live eval usage：
  - avg input tokens = `39874`
  - avg output tokens = `2076`
- discoverability：
  - 显式调用成功率 `6/8 = 75%`
  - `explicit-dollar / explicit-named / explicit-path` 均为 `100%`
  - `implicit` 仍为 `0%`

这意味着：

1. 对公开安装后的 skill，显式调用已经稳定
2. `implicit` 仍不应作为主入口
3. 当前最稳的真实使用方法仍是显式 `$skill-name`

## 推荐测试命令

### 1. live eval

```powershell
& 'C:/Users/feian/.codex/tools/safe-run.ps1' `
  -ScriptPath 'E:/工作区/CODEX团队功能优化/skill-lab+/scripts/run_skill_eval.py' `
  -ScriptArgs @('--lab-root','E:/工作区/CODEX团队功能优化/skill-lab+','--run-id','my-run')
```

### 2. live 打分

```powershell
& 'C:/Users/feian/.codex/tools/safe-run.ps1' `
  -ScriptPath 'E:/工作区/CODEX团队功能优化/skill-lab+/scripts/score_skill_eval.py' `
  -ScriptArgs @('--run-root','E:/工作区/CODEX团队功能优化/skill-lab+/runs/my-run')
```

### 3. discoverability eval

```powershell
& 'C:/Users/feian/.codex/tools/safe-run.ps1' `
  -ScriptPath 'E:/工作区/CODEX团队功能优化/skill-lab+/scripts/run_discoverability_eval.py' `
  -ScriptArgs @('--lab-root','E:/工作区/CODEX团队功能优化/skill-lab+','--run-id','discover-run','--repeat','1','--variant','release')
```

### 4. 全局安装 smoke

```powershell
& 'C:/Users/feian/.codex/tools/safe-run.ps1' `
  -ScriptPath 'E:/工作区/CODEX团队功能优化/skill-lab+/scripts/run_global_skill_smoke.py' `
  -ScriptArgs @(
    '--run-root','E:/工作区/CODEX团队功能优化/skill-lab+/runs/global-smoke',
    '--workspace-root','E:/工作区/CODEX团队功能优化',
    '--skill-name','codex-subagents-kit',
    '--skill-path','C:/Users/feian/.codex/skills/codex-subagents-kit',
    '--marker','config-guided-codex-subagents',
    '--marker','product gate',
    '--marker','four gates',
    '--marker','scorecard'
  )
```

## 已知限制

- 当前 Codex 上，`implicit` skill discoverability 仍不可靠
- 是否真的可以直接使用 native child-agent，仍需要 **live session evidence**
- 本仓库强调的是 **真实机制适配**，不是对不存在能力的包装

## 许可证

默认采用 `MIT`，见 `LICENSE`。
