# Three-condition benchmark results

Run details:

- Date: 2026-08-11.
- Harness: Cursor CLI (`cursor-agent`), headless, one call per cell, tools disabled.
- Matrix: 12 models x 8 scenarios x 3 conditions = 288 generations, all fresh in this run (no reused upstream numbers).
- Model names are Cursor model slugs. The `-medium` suffix is the reasoning-effort setting.
- Scenarios, linter, and prompt wrapper are byte-identical to SimpleEnglish's upstream benchmark.
- Judge: `claude-opus-4-8-medium`, blind, both orders per pair. 95 of 96 pairs judged (one pair failed response parsing). A Claude judge scored partly-Claude output. Read the warnings at the end.
- Raw JSON for every generation and every judged pair is in `raw/`.

**Average reduction vs baseline: simple-english 85.1%, agent-ste 95.5%.**

| Model | Baseline v/100w | simple-english v/100w | agent-ste v/100w | s-e red. | ours red. | Words (base / s-e / ours) |
|---|---|---|---|---|---|---|
| claude-opus-4-8-medium | 3.5 | 0.17 | 0.09 | 95.1% | 97.4% | 100 / 93 / 93 |
| claude-sonnet-5-medium | 2.12 | 0.69 | 0.15 | 67.5% | 92.9% | 92 / 89 / 93 |
| claude-opus-5-medium | 3.65 | 0.37 | 0.32 | 89.9% | 91.2% | 126 / 97 / 93 |
| claude-fable-5-medium | 2.61 | 0.18 | 0.0 | 93.1% | 100.0% | 108 / 94 / 95 |
| gpt-5.6-sol-medium | 1.18 | 0.18 | 0.0 | 84.7% | 100.0% | 86 / 94 / 103 |
| gpt-5.6-terra-medium | 1.38 | 0.4 | 0.0 | 71.0% | 100.0% | 75 / 84 / 73 |
| gpt-5.6-luna-medium | 1.01 | 0.17 | 0.18 | 83.2% | 82.2% | 91 / 101 / 98 |
| gpt-5.5-medium | 1.94 | 0.13 | 0.11 | 93.3% | 94.3% | 92 / 84 / 88 |
| glm-5.2-max | 4.23 | 0.3 | 0.09 | 92.9% | 97.9% | 95 / 82 / 101 |
| composer-2.5 | 1.53 | 0.36 | 0.07 | 76.5% | 95.4% | 99 / 103 / 106 |
| gemini-3.6-flash-medium | 1.63 | 0.16 | 0.08 | 90.2% | 95.1% | 87 / 106 / 105 |
| cursor-grok-4.5-medium | 2.04 | 0.33 | 0.0 | 83.8% | 100.0% | 101 / 101 / 102 |

## Judge pass (blind pairwise, simple-english vs agent-ste)

For each model x scenario pair, claude-opus-4-8-medium scored the simple-english text
and the agent-ste text on the same 0-10 rubric as the upstream benchmark,
twice with the texts in both orders, scores averaged. The judge saw no labels.

Result: agent-ste scored higher in 52 of 95 pairs, tied in
17, and lost in 26. Mean rubric score: 8.07 agent-ste, 7.53 simple-english.

| Model | agent-ste wins | Ties | Losses |
|---|---|---|---|
| claude-opus-4-8-medium | 5 | 1 | 2 |
| claude-sonnet-5-medium | 4 | 2 | 2 |
| claude-opus-5-medium | 6 | 1 | 1 |
| claude-fable-5-medium | 6 | 1 | 1 |
| gpt-5.6-sol-medium | 6 | 0 | 2 |
| gpt-5.6-terra-medium | 3 | 1 | 4 |
| gpt-5.6-luna-medium | 3 | 3 | 2 |
| gpt-5.5-medium | 5 | 2 | 1 |
| glm-5.2-max | 5 | 1 | 2 |
| composer-2.5 | 3 | 3 | 2 |
| gemini-3.6-flash-medium | 4 | 1 | 3 |
| cursor-grok-4.5-medium | 2 | 1 | 4 |

## Honest number warnings

- The linter is the upstream regex pass, copied verbatim. Both skills coach
  the same mechanical rules it counts, so linter numbers measure rule-following,
  not overall writing quality. The judge pass is the quality signal.
- One generation per cell. Re-run for variance.
- Skill conditions carry their SKILL.md in the prompt; input tokens differ
  by skill length. Output tokens are reported.
- No tool can guarantee ASD-STE100 compliance, including either skill.
