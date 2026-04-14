# Reports

这个目录只保留 **公开仓库需要的摘要级报告**，不保留大体量原始运行产物。

## 当前保留的报告

- `final-release-validation-20260320.md`
- `score-report-release-eval-04-final-candidate.md`
- `discoverability-report-release-02-post-cutover.md`
- `compare-release-eval-01-vs-04.md`
- `open-source-sync-20260414-skill-upgrade.md`

## 为什么不提交原始 runs

原始 `runs/` 目录通常包含：

- 大量 `events.jsonl`
- prompt / response 中间产物
- 本机路径痕迹
- 与本地运行 surface 强绑定的上下文

这些内容更适合保存在本机证据目录，不适合作为公开仓库的默认提交物。

## 说明

本目录中的报告已经做过轻量整理：

- 把绝对本机路径改成了更适合公开仓库阅读的“历史 run id / 相对说明”形式
- 保留关键日期、分数、token 指标与结论
