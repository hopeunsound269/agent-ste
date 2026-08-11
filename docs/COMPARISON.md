# STE skill comparison: agent-ste vs SimpleEnglish vs asd-ste100-skill vs no skill

A factual comparison of the open-source Agent Skills that make LLMs write ASD-STE100 Simplified Technical English. Benchmark numbers come from [the open three-condition run](../evals/results/RESULTS.md) of 2026-08-11: 12 models, 5 model families, 8 writing tasks, 288 fresh generations, one shared linter.

## Benchmark results

| Measure | No skill | SimpleEnglish | agent-ste |
|---|---|---|---|
| STE violations per 100 words (mean) | 2.23 | 0.29 | **0.09** |
| Mean reduction vs no skill | — | 85.1% | **95.5%** |
| Models with zero violations | 0 of 12 | 0 of 12 | **4 of 12** |
| Blind judge preference (95 pairs) | — | 26 | **52** (17 ties) |
| Best on model count | — | 1 of 12 | **11 of 12** |

The linter counts the mechanical STE rules: sentence length, banned modals, perfect tenses, contractions, semicolons, Latin abbreviations, dangling "-ing" clauses, mid-sentence conditions, filler words, and synonym rotation. It is a floor, not a certification.

## Feature comparison

| | agent-ste | SimpleEnglish | asd-ste100-skill |
|---|---|---|---|
| Format | Agent Skills standard | Agent Skills standard + Claude plugin | Claude Code skill |
| Install | `npx skills add abryfs/agent-ste` | `npx skills add AminBlg/SimpleEnglish` or plugin marketplace | manual copy |
| Mandatory self-check before delivery | **Yes: a 10-search final gate** | No | No |
| Agent-facing text rules (prompts, tool descriptions, error messages) | **Yes, a dedicated section** | No | Framing only |
| Word-count rulings for code and identifiers | **Yes** | No | No |
| Prompt fallback for tools without skills | Yes, compact + micro | Yes | No |
| Skill size on activation (approx. tokens) | 2,200 | 4,500 | 1,400 |
| Open benchmark with raw data | **Yes, 288 generations in-repo** | Yes, 48 generations | No |
| Output style / slash commands for Claude Code | No | **Yes** | No |
| Community size | new | **largest** | mid |
| License | MIT | MIT | MIT |

## Which one to pick

- Pick **agent-ste** for measured rule-following across model families, and for text that other machines parse: system prompts, tool descriptions, error messages, and inter-agent messages.
- Pick **SimpleEnglish** for the Claude Code plugin ecosystem: output styles, slash commands, and hooks. Its benchmark harness is the base of ours, and the project deserves the credit for it.
- Pick **asd-ste100-skill** for a minimal single-file rewriter inside Claude Code.
- Pick **no skill** for marketing text and brand writing. STE deletes persuasion by design.

All three skills paraphrase the STE rules. None of the three reproduces the copyrighted STE dictionary. For word-level rulings, download the [official standard](https://www.asd-ste100.org/) from ASD. It is free.

## Method notes

The comparison run is honest about its limits: one generation per cell, a Claude judge scored partly-Claude output, and both skills coach the rules that the linter counts. The measurement layer (linter, tasks, prompt wrapper) is byte-identical to the SimpleEnglish upstream benchmark, so neither skill got a home-field rule set. To re-run everything, read [Reproduce](../README.md#reproduce).
