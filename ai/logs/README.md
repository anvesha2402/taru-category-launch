# Model call logs

One row per model call: time (UTC, Colab clock), agent, prompt version, model, input and output tokens, seconds, verdict, risk level, status and the text checked.

| File | Run | Rows |
|---|---|---|
| `ai4_guardrail_calls.csv` | AI4 claims guardrail, 2 Oct 2026: 1 demo claim + the 40 test claims (Qwen2.5-7B-Instruct, 4-bit, Colab T4) | 41 |
| `ai5_run2_calls.csv` | AI5 content agents, run 2: every guardrail call made while checking the 21 drafts | add from `ai5_run2_all_outputs.zip` (file `calls.csv`, renamed) |

The red-team and claims-matrix calls of the AI4 run are recorded with their verdicts in `ai/eval/redteam_guardrail_results_v1.csv` and `compliance/claims_matrix_prescreened.csv`; their per-call timings were not kept.

When a notebook runs, the guardrail appends to `ai/logs/calls.csv` inside that session. These files are the saved copies of each run.
