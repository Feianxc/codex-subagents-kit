# Decision Matrix

## Mode Selection

| Mode | Use when | Avoid when | Evidence to record |
| --- | --- | --- | --- |
| `blueprint-only` | Goal is still fuzzy, risk is high, or environment is not ready | User asked for full execution and the task is already scoped | What is missing, what assumptions block execution |
| `single-controller` | One small task, or file overlap is high, or coordination cost would dominate | There are multiple independent outputs with clear boundaries | Why spawning would be wasteful |
| `native-multi-agent` | Current Codex runtime actually exposes native child-agent capability and you can cite concrete proof such as `multi_agent=true` plus live agent tools in-session | You only have `codex exec` subprocesses or a feature flag without usable tools | The exact feature-flag and runtime/tool evidence |
| `artifact-orchestrated-swarm` | Two or more spawn-worthy tasks exist and native support is absent, uncertain, or unstable | The job is too small to justify orchestration | Run root, child-run plan, registry ownership |

## Spawn Worthiness

Spawn a task only if all answers are "yes":

1. Does the task have a single objective?
2. Can you name stable input and output paths?
3. Can you write an acceptance rule that another agent could verify?
4. Is the file overlap with other spawned tasks low?
5. Is the task large enough that coordination cost is worth paying?

If any answer is "no", keep the work with the controller or downgrade the plan.

## Controller Responsibilities

The controller always owns:

- preflight framing
- mode selection
- task registry integrity
- final merge / acceptance
- audit honesty

Never offload those to a child run.
