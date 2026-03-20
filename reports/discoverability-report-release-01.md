# Discoverability Report

- Run Root: `E:\工作区\CODEX团队功能优化\skill-lab+\runs\20260320-release-discovery-01`

| Variant | Load Mode | Case | Success Rate | Avg Input Tokens | Avg Output Tokens |
| --- | --- | --- | --- | --- | --- |
| baseline | injected | explicit-dollar | 100% (1/1) | 47999 | 1912 |
| baseline | injected | explicit-named | 0% (0/1) | 14532 | 932 |
| baseline | injected | explicit-path | 0% (0/1) | 14536 | 558 |
| baseline | injected | implicit | 0% (0/1) | 121492 | 1603 |
| baseline | project | explicit-dollar | 0% (0/1) | 69329 | 3434 |
| baseline | project | explicit-named | 0% (0/1) | 14532 | 568 |
| baseline | project | explicit-path | 100% (1/1) | 137145 | 1880 |
| baseline | project | implicit | 0% (0/1) | 31166 | 1114 |
| release | injected | explicit-dollar | 0% (0/1) | 31161 | 1169 |
| release | injected | explicit-named | 0% (0/1) | 14533 | 433 |
| release | injected | explicit-path | 100% (1/1) | 109886 | 1836 |
| release | injected | implicit | 0% (0/1) | 63477 | 1046 |
| release | project | explicit-dollar | 0% (0/1) | 14532 | 556 |
| release | project | explicit-named | 0% (0/1) | 14533 | 468 |
| release | project | explicit-path | 100% (1/1) | 141121 | 2220 |
| release | project | implicit | 0% (0/1) | 31075 | 1017 |

## Variant Summary

- **baseline**: success_rate=25% (2/8), avg_input_tokens=56341, avg_output_tokens=1500
- **release**: success_rate=25% (2/8), avg_input_tokens=52540, avg_output_tokens=1093
