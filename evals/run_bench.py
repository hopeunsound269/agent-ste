#!/usr/bin/env python3
"""Three-condition benchmark: no skill vs simple-english vs agent-ste.

This is a derivative of run_bench.py from AminBlg/SimpleEnglish (MIT), with a
third condition added. The measurement layer is theirs, unmodified:
ste_lint.py and scenarios.json in this directory are byte-identical copies
from that repository (diff them to confirm). The prompt wrapper and the
headless CLI calls also match the upstream benchmark.

To run the simple-english condition, clone the upstream repo next to this
one (or set BENCH_SIMPLE_ENGLISH_SKILL to its SKILL.md path):

  git clone https://github.com/AminBlg/SimpleEnglish ../../SimpleEnglish

Resumable: existing raw result files are skipped.

Usage:
  python3 run_bench.py                # full matrix
  python3 run_bench.py --smoke        # 1 model x 1 scenario x 3 conditions
  python3 run_bench.py --report-only  # rebuild RESULTS.md from raw/
  python3 run_bench.py --judge        # blind pairwise judge: theirs vs ours

Env:
  BENCH_HARNESS=claude|cursor   CLI to call (default claude, like upstream)
  BENCH_MODELS=a,b,c            override the model list
  BENCH_JUDGE=<model>           override the judge model
"""
import json
import os
import pathlib
import subprocess
import sys
import time

import ste_lint

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
SKILLS = {
    "simple-english": pathlib.Path(os.environ.get(
        "BENCH_SIMPLE_ENGLISH_SKILL",
        REPO.parent / "SimpleEnglish" / "skills" / "simple-english" / "SKILL.md")),
    "agent-ste": REPO / "skills" / "agent-ste" / "SKILL.md",
}
# "claude" (Claude Code CLI, like upstream) or "cursor" (Cursor CLI).
# Separate results dirs so runs from the two harnesses never mix.
HARNESS = os.environ.get("BENCH_HARNESS", "claude")
RESULTS = HERE / ("results" if HARNESS == "claude" else f"results-{HARNESS}")
RAW = RESULTS / "raw"
MODELS = os.environ.get("BENCH_MODELS", "").split(",") if os.environ.get("BENCH_MODELS") else [
    "claude-opus-4-8",
    "claude-opus-4-7",
    "claude-opus-4-6",
    "claude-opus-4-5-20251101",
    "claude-sonnet-5",
    "claude-sonnet-4-6",
]
JUDGE_MODEL = os.environ.get("BENCH_JUDGE", "claude-opus-4-8")
CONDITIONS = ("baseline", "simple-english", "agent-ste")


def call_claude(prompt, model, timeout=300):
    if HARNESS == "cursor":
        return call_cursor(prompt, model, timeout)
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "json",
           "--disallowedTools", "Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch"]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd="/tmp")
    if proc.returncode != 0:
        raise RuntimeError(f"{model}: {proc.stderr[:300]}")
    env = json.loads(proc.stdout)
    if isinstance(env, list):
        env = next(m for m in env if m.get("type") == "result")
    if env.get("is_error"):
        raise RuntimeError(f"{model}: {str(env.get('result'))[:300]}")
    return {
        "text": env.get("result", ""),
        "input_tokens": env.get("usage", {}).get("input_tokens"),
        "output_tokens": env.get("usage", {}).get("output_tokens"),
        "duration_ms": env.get("duration_ms", int(1000 * (time.time() - t0))),
        "cost_usd": env.get("total_cost_usd"),
    }


def call_cursor(prompt, model, timeout=300):
    cmd = ["cursor-agent", "-p", prompt, "--model", model, "--output-format", "json", "--trust"]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd="/tmp")
    if proc.returncode != 0:
        raise RuntimeError(f"{model}: {proc.stderr[:300]}")
    env = json.loads(proc.stdout)
    if isinstance(env, list):
        env = next((m for m in env if m.get("type") == "result"), env[-1])
    if env.get("is_error") or env.get("error"):
        raise RuntimeError(f"{model}: {str(env.get('result') or env.get('error'))[:300]}")
    text = env.get("result") or env.get("text") or env.get("response") or ""
    usage = env.get("usage") or {}
    return {
        "text": text,
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "duration_ms": env.get("duration_ms", int(1000 * (time.time() - t0))),
        "cost_usd": env.get("total_cost_usd"),
    }


def build_prompt(scenario, condition, skill_texts):
    if condition == "baseline":
        return scenario["prompt"]
    return ("Follow these writing instructions exactly, including the self-check step:\n\n"
            + skill_texts[condition] + "\n\n---\n\nTask: " + scenario["prompt"]
            + "\n\nReturn only the final text, no rule commentary.")


def generate(models, scenarios):
    skill_texts = {k: p.read_text() for k, p in SKILLS.items()}
    RAW.mkdir(parents=True, exist_ok=True)
    todo = [(m, c, s) for m in models for s in scenarios for c in CONDITIONS]
    for i, (model, cond, sc) in enumerate(todo, 1):
        out = RAW / f"{model}__{cond}__{sc['id']}.json"
        if out.exists():
            continue
        print(f"[{i}/{len(todo)}] {model} {cond} {sc['id']}", flush=True)
        try:
            res = call_claude(build_prompt(sc, cond, skill_texts), model)
        except Exception as e:
            print(f"  FAILED: {e}", flush=True)
            continue
        res.update(model=model, condition=cond, scenario=sc["id"], type=sc["type"])
        res["lint"] = ste_lint.lint(res["text"], sc["type"])
        out.write_text(json.dumps(res, indent=2))
        time.sleep(2)


def aggregate():
    rows = [json.loads(p.read_text()) for p in sorted(RAW.glob("*.json")) if "__judge__" not in p.name]
    per_model = {}
    for r in rows:
        m = per_model.setdefault(r["model"], {c: [] for c in CONDITIONS})
        m[r["condition"]].append(r)
    table = []
    for model in [m for m in MODELS if m in per_model]:
        row = {"model": model}
        for cond in CONDITIONS:
            runs = per_model[model][cond]
            if not runs:
                continue
            key = cond.replace("-", "_")
            row[f"{key}_viol_per_100w"] = round(
                sum(r["lint"]["violations_per_100w"] for r in runs) / len(runs), 2)
            row[f"{key}_mean_sentence"] = round(
                sum(r["lint"]["mean_sentence_words"] for r in runs) / len(runs), 1)
            row[f"{key}_output_tokens"] = round(
                sum(r["output_tokens"] or 0 for r in runs) / len(runs))
            row[f"{key}_words"] = round(
                sum(r["lint"]["words"] for r in runs) / len(runs))
            row[f"{key}_n"] = len(runs)
        b = row.get("baseline_viol_per_100w")
        if b:
            for key in ("simple_english", "agent_ste"):
                s = row.get(f"{key}_viol_per_100w")
                if s is not None:
                    row[f"{key}_reduction_pct"] = round(100 * (b - s) / b, 1)
        table.append(row)
    (RESULTS / "results.json").write_text(json.dumps(
        {"generated": time.strftime("%Y-%m-%d"), "models": table, "runs": len(rows)}, indent=2))
    return table


def judge_summary():
    files = sorted(RAW.glob("*__judge__*.json"))
    per_model, wins, ties, losses = {}, 0, 0, 0
    ours_sum = theirs_sum = valid = 0
    for p in files:
        d = json.loads(p.read_text())
        o1, o2 = d["order1_theirs_first"], d["order2_ours_first"]
        if not o1 or not o2:
            continue
        ours = (o1["b_score"] + o2["a_score"]) / 2
        theirs = (o1["a_score"] + o2["b_score"]) / 2
        valid += 1
        ours_sum += ours
        theirs_sum += theirs
        w = per_model.setdefault(d["model"], [0, 0, 0])
        if ours > theirs:
            wins += 1
            w[0] += 1
        elif ours == theirs:
            ties += 1
            w[1] += 1
        else:
            losses += 1
            w[2] += 1
    if not valid:
        return []
    lines = [
        "",
        "## Judge pass (blind pairwise, simple-english vs agent-ste)",
        "",
        f"For each model x scenario pair, {JUDGE_MODEL} scored the simple-english text",
        "and the agent-ste text on the same 0-10 rubric as the upstream benchmark,",
        "twice with the texts in both orders, scores averaged. The judge saw no labels.",
        "",
        f"Result: agent-ste scored higher in {wins} of {valid} pairs, tied in",
        f"{ties}, and lost in {losses}. Mean rubric score: {ours_sum / valid:.2f} "
        f"agent-ste, {theirs_sum / valid:.2f} simple-english.",
        "",
        "| Model | agent-ste wins | Ties | Losses |",
        "|---|---|---|---|",
    ]
    for m in [m for m in MODELS if m in per_model]:
        w, t, l = per_model[m]
        lines.append(f"| {m} | {w} | {t} | {l} |")
    return lines


def report(table):
    def avg(key):
        ok = [r[key] for r in table if key in r]
        return round(sum(ok) / len(ok), 1) if ok else None

    n = sum(r.get(f"{c.replace('-', '_')}_n", 0) for r in table for c in CONDITIONS)
    lines = [
        "# Three-condition benchmark results",
        "",
        f"Same scenarios, linter, prompt wrapper, and models as SimpleEnglish's",
        f"upstream benchmark. {n} generations, all three conditions regenerated",
        "fresh in this run (no reused upstream numbers).",
        "",
        f"**Average reduction vs baseline: simple-english {avg('simple_english_reduction_pct')}%, "
        f"agent-ste {avg('agent_ste_reduction_pct')}%.**",
        "",
        "| Model | Baseline v/100w | simple-english v/100w | agent-ste v/100w | s-e red. | ours red. | Words (base / s-e / ours) |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in table:
        lines.append(
            f"| {r['model']} | {r.get('baseline_viol_per_100w', '—')} "
            f"| {r.get('simple_english_viol_per_100w', '—')} | {r.get('agent_ste_viol_per_100w', '—')} "
            f"| {r.get('simple_english_reduction_pct', '—')}% | {r.get('agent_ste_reduction_pct', '—')}% "
            f"| {r.get('baseline_words', '—')} / {r.get('simple_english_words', '—')} "
            f"/ {r.get('agent_ste_words', '—')} |")
    lines += judge_summary()
    lines += [
        "",
        "## Honest number warnings",
        "",
        "- The linter is the upstream regex pass, copied verbatim. Both skills coach",
        "  the same mechanical rules it counts, so linter numbers measure rule-following,",
        "  not overall writing quality. The judge pass is the quality signal.",
        "- One generation per cell. Re-run for variance.",
        "- Skill conditions carry their SKILL.md in the prompt; input tokens differ",
        "  by skill length. Output tokens are reported.",
        "- No tool can guarantee ASD-STE100 compliance, including either skill.",
    ]
    (RESULTS / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def judge(scenarios):
    import itertools
    rubric = ("Score the two texts A and B on: (1) can a tired non-native reader "
              "misread any sentence, (2) is every instruction executable as written, "
              "(3) filler or slop present. Reply with JSON only: "
              '{"a_score": 0-10, "b_score": 0-10}')
    for model, sc in itertools.product(MODELS, scenarios):
        pair = {}
        for cond in ("simple-english", "agent-ste"):
            p = RAW / f"{model}__{cond}__{sc['id']}.json"
            if p.exists():
                pair[cond] = json.loads(p.read_text())["text"]
        if len(pair) != 2:
            continue
        out = RAW / f"{model}__judge__{sc['id']}.json"
        if out.exists():
            continue
        scores = []
        for a, b in ((pair["simple-english"], pair["agent-ste"]),
                     (pair["agent-ste"], pair["simple-english"])):
            res = call_claude(f"{rubric}\n\nTEXT A:\n{a}\n\nTEXT B:\n{b}", JUDGE_MODEL)
            try:
                scores.append(json.loads(res["text"].strip().strip("`json\n")))
            except json.JSONDecodeError:
                scores.append(None)
        out.write_text(json.dumps({"model": model, "scenario": sc["id"],
                                   "order1_theirs_first": scores[0],
                                   "order2_ours_first": scores[1]}, indent=2))
        print(f"judged {model} {sc['id']}", flush=True)


def main():
    scenarios = json.loads((HERE / "scenarios.json").read_text())
    if "--smoke" in sys.argv:
        generate([MODELS[-1]], scenarios[:1])
    elif "--judge" in sys.argv:
        judge(scenarios)
        return
    elif "--report-only" not in sys.argv:
        generate(MODELS, scenarios)
    report(aggregate())


if __name__ == "__main__":
    main()
