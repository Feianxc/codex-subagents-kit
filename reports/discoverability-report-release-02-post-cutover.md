# Discoverability Report

- Historical Run ID: `20260320-release-discovery-02-post-cutover`

| Variant | Load Mode | Case | Success Rate | Avg Input Tokens | Avg Output Tokens |
| --- | --- | --- | --- | --- | --- |
| release | injected | explicit-dollar | 100% (1/1) | 33275 | 827 |
| release | injected | explicit-named | 100% (1/1) | 30917 | 704 |
| release | injected | explicit-path | 100% (1/1) | 34027 | 867 |
| release | injected | implicit | 0% (0/1) | 63603 | 1173 |
| release | project | explicit-dollar | 100% (1/1) | 15985 | 450 |
| release | project | explicit-named | 100% (1/1) | 30810 | 508 |
| release | project | explicit-path | 100% (1/1) | 15990 | 370 |
| release | project | implicit | 0% (0/1) | 49681 | 1865 |

## Variant Summary

- **release**: success_rate=75% (6/8), avg_input_tokens=34286, avg_output_tokens=846
