# A/B test for the 1.0.2 rule additions

Version 1.0.2 adds three lines to the skill:

1. A writing rule: no idioms, no metaphors, no figurative language.
2. A vocabulary rule: use the short everyday word ("start", not "commence").
3. A rewrite guard: keep a technical term that the meaning needs, and flag the exception.

We test every change to the skill, including small ones. This directory holds the test for these three lines.

## Method

- Two arms: the shipped 1.0.1 skill ("current") and the 1.0.2 draft ("candidate").
- 3 models from 3 families: `claude-sonnet-5-medium`, `gpt-5.5-medium`, `gemini-3.6-flash-medium`.
- The 8 upstream scenarios from SimpleEnglish, unmodified. The scenarios predate the new rules and do not target them.
- Same prompt wrapper and linter as the main benchmark. 48 generations on the Cursor harness.
- A blind pairwise judge (`claude-opus-4-8-medium`) scored each of the 24 pairs twice, with the texts in both orders.

## Pre-registered decision rule

The rule was fixed in `ab_test.py` before any generation ran. If both conditions below hold, ship. In every other case, do not ship.

1. Candidate mean violations per 100 words is not worse than current by more than 0.05.
2. Judge: candidate wins plus ties cover at least 50% of valid pairs.

## Result

| Metric | current (1.0.1) | candidate (1.0.2) |
|---|---|---|
| Mean violations per 100 words | 0.061 | 0.028 |
| Mean words per output | 100 | 98 |
| Judge wins / ties / losses | 10 / 4 / 10 | 10 / 4 / 10 (mirror) |
| Mean judge score | 8.06 | 7.85 |

Rule 1: pass. Rule 2: pass (14 of 24 pairs, 58%). Decision: ship.

Caveats:

- The judge saw a dead-even split on wins, and the candidate's mean score is 0.21 lower. The additions do not improve judged quality. They improve linter compliance without a quality cost that the rule counts as material.
- One generation per cell. Re-run for variance.
- `raw/` holds all 48 generations and 24 judge files.
