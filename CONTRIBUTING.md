# Contributing

感谢你为 `codex-subagents-kit` 做贡献。

这个仓库不是单纯的 skill 文案样板，而是一个带有 **验证脚本、夹具、触发测试结论与工程边界** 的 Codex skill 工程仓库。提交前请尽量遵守以下规则。

## 贡献目标

优先做这些事：

1. 提高 `codex-subagents-kit` 的真实可用性
2. 降低 token 成本而不明显牺牲质量
3. 强化显式触发的稳定性
4. 保持 artifacts / audit / scorecard 闭环
5. 保持对 Codex 当前真实机制的诚实描述

不要做这些事：

1. 把未证实的能力包装成“官方原生支持”
2. 仅为追求分数而弱化失败判定
3. 往 `SKILL.md` 核心正文堆放冗长说明
4. 提交临时运行垃圾、私有路径痕迹或无关大文件

## 仓库结构原则

- `skills/codex-subagents-kit/`：当前公开发布版
- `skills/baseline-codex-agent-swarm/`：回归基线，不是主发布物
- `fixtures/`：最小测试工作区
- `prompts/`：测试 prompt 模板
- `scripts/`：安装、校验、评测脚本
- `reports/`：保留的摘要报告
- `docs/history/`：迭代与聊天记录索引

## 改 skill 时的规则

### 1. 保持 skill 薄核心

- `SKILL.md` 只保留核心决策与流程
- 细节优先放到 `references/`
- 可重复动作优先脚本化，而不是反复手写

### 2. 改 metadata 时要同步检查

如果修改了以下任一项：

- `SKILL.md` frontmatter 的 `name`
- `SKILL.md` frontmatter 的 `description`
- `agents/openai.yaml`

请同步检查：

- `README.md`
- `fixtures/**/.codex/config.toml`
- `docs/triggering-behavior.md`
- `scripts/validate_release_repo.py`

### 3. 不要在没有证据时放宽触发承诺

当前接受口径是：

- **显式调用** 有证据支持
- **自然语言隐式自动触发** 仍不应被承诺为稳定主路径

## 提交前建议验证

### A. skill 快速校验

```bash
python scripts/quick_validate_skill.py --skill-dir skills/codex-subagents-kit
```

### B. 仓库结构校验

```bash
python scripts/validate_release_repo.py --repo-root .
```

### C. 可选：本机安装测试

```bash
python scripts/install_skill.py --repo-root . --force
```

### D. 可选：更重的评测

如果你在具备 Codex 运行环境的本机上工作，可继续运行仓库中的评测脚本（例如 live eval / discoverability eval）。这类脚本依赖本地 Codex 能力与运行 surface，提交前请在 PR 中写清楚你的环境和结果。

## 不应提交的内容

不要提交：

- `runs/`
- `**/.workspace/`
- `__pycache__/`
- 临时日志
- 仅适用于某一台本机的私有配置或路径快照

## PR 建议

PR 描述至少说明：

1. 改了哪些文件
2. 是 metadata / workflow / references / scripts / docs / reports 中的哪一类
3. 跑了哪些验证
4. 与上一接受版相比的收益与风险

## CHANGELOG 规则

如果改动会影响以下任一项，建议同步更新 `CHANGELOG.md`：

1. 公开 skill 行为
2. 验证脚本或评分规则
3. 仓库结构与对外文档
4. 发布说明、证据口径或接受版结论

写 changelog 时建议：

- 保持简短、准确
- 优先写“对公开使用者有什么变化”
- 不把未重新验证的能力写成新的已验证结论
