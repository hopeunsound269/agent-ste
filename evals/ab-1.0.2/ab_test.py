#!/usr/bin/env python3
"""A/B test: shipped SKILL.md (current) vs skill-candidate.md (candidate).

Same scenarios, linter, prompt wrapper, and cursor-harness calls as the
main benchmark. 3 models x 8 scenarios x 2 arms = 48 generations, then a
blind pairwise judge on each pair, both orders.

Pre-registered decision rule (set before any results existed):
ship the candidate only if BOTH hold:
  1. candidate mean viol/100w <= current mean + 0.05
  2. judge: candidate wins + ties >= 50% of valid pairs

Usage:
  python3 ab_test.py            # generate
  python3 ab_test.py --judge    # judge pass
  python3 ab_test.py --report   # report + decision
"""
import json
import pathlib
import subprocess
import sys
import time

import ste_lint

HERE = pathlib.Path(__file__).resolve().parent
SKILLS = {
    "current": HERE.parent / "agent-ste" / "skills" / "agent-ste" / "SKILL.md",
    "candidate": HERE / "skill-candidate.md",
}
RAW = HERE / "ab-raw"
MODELS = ["claude-sonnet-5-medium", "gpt-5.5-medium", "gemini-3.6-flash-medium"]
JUDGE_MODEL = "claude-opus-4-8-medium"
CONDITIONS = ("current", "candidate")


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
    return {"text": text, "duration_ms": env.get("duration_ms", int(1000 * (time.time() - t0)))}


def build_prompt(scenario, skill_text):
    return ("Follow these writing instructions exactly, including the self-check step:\n\n"
            + skill_text + "\n\n---\n\nTask: " + scenario["prompt"]
            + "\n\nReturn only the final text, no rule commentary.")


def generate(scenarios):
    skill_texts = {k: p.read_text() for k, p in SKILLS.items()}
    RAW.mkdir(exist_ok=True)
    todo = [(m, c, s) for m in MODELS for s in scenarios for c in CONDITIONS]
    for i, (model, cond, sc) in enumerate(todo, 1):
        out = RAW / f"{model}__{cond}__{sc['id']}.json"
        if out.exists():
            continue
        print(f"[{i}/{len(todo)}] {model} {cond} {sc['id']}", flush=True)
        try:
            res = call_cursor(build_prompt(sc, skill_texts[cond]), model)
        except Exception as e:
            print(f"  FAILED: {e}", flush=True)
            continue
        res.update(model=model, condition=cond, scenario=sc["id"], type=sc["type"])
        res["lint"] = ste_lint.lint(res["text"], sc["type"])
        out.write_text(json.dumps(res, indent=2))
        time.sleep(2)


def judge(scenarios):
    rubric = ("Score the two texts A and B on: (1) can a tired non-native reader "
              "misread any sentence, (2) is every instruction executable as written, "
              "(3) filler or slop present. Reply with JSON only: "
              '{"a_score": 0-10, "b_score": 0-10}')
    for model in MODELS:
        for sc in scenarios:
            pair = {}
            for cond in CONDITIONS:
                p = RAW / f"{model}__{cond}__{sc['id']}.json"
                if p.exists():
                    pair[cond] = json.loads(p.read_text())["text"]
            if len(pair) != 2:
                continue
            out = RAW / f"{model}__judge__{sc['id']}.json"
            if out.exists():
                continue
            scores = []
            for a, b in ((pair["current"], pair["candidate"]),
                         (pair["candidate"], pair["current"])):
                res = call_cursor(f"{rubric}\n\nTEXT A:\n{a}\n\nTEXT B:\n{b}", JUDGE_MODEL)
                try:
                    scores.append(json.loads(res["text"].strip().strip("`json\n")))
                except json.JSONDecodeError:
                    scores.append(None)
            out.write_text(json.dumps({"model": model, "scenario": sc["id"],
                                       "order1_current_first": scores[0],
                                       "order2_candidate_first": scores[1]}, indent=2))
            print(f"judged {model} {sc['id']}", flush=True)


def report():
    rows = [json.loads(p.read_text()) for p in sorted(RAW.glob("*.json"))
            if "__judge__" not in p.name]
    means = {}
    for cond in CONDITIONS:
        rs = [r for r in rows if r["condition"] == cond]
        means[cond] = {
            "n": len(rs),
            "viol_per_100w": round(sum(r["lint"]["violations_per_100w"] for r in rs) / len(rs), 3),
            "words": round(sum(r["lint"]["words"] for r in rs) / len(rs)),
        }
    wins = ties = losses = valid = 0
    cand_sum = cur_sum = 0.0
    for p in sorted(RAW.glob("*__judge__*.json")):
        d = json.loads(p.read_text())
        o1, o2 = d["order1_current_first"], d["order2_candidate_first"]
        if not o1 or not o2:
            continue
        cand = (o1["b_score"] + o2["a_score"]) / 2
        cur = (o1["a_score"] + o2["b_score"]) / 2
        valid += 1
        cand_sum += cand
        cur_sum += cur
        if cand > cur:
            wins += 1
        elif cand == cur:
            ties += 1
        else:
            losses += 1
    print(json.dumps({"means": means, "judge": {
        "valid_pairs": valid, "candidate_wins": wins, "ties": ties,
        "candidate_losses": losses,
        "mean_candidate": round(cand_sum / valid, 2) if valid else None,
        "mean_current": round(cur_sum / valid, 2) if valid else None,
    }}, indent=2))
    lint_ok = means["candidate"]["viol_per_100w"] <= means["current"]["viol_per_100w"] + 0.05
    judge_ok = valid > 0 and (wins + ties) >= valid / 2
    print(f"\nRule 1 (lint no worse than +0.05): {'PASS' if lint_ok else 'FAIL'}")
    print(f"Rule 2 (judge wins+ties >= 50%):   {'PASS' if judge_ok else 'FAIL'}")
    print(f"\nDECISION: {'SHIP the candidate' if (lint_ok and judge_ok) else 'DO NOT SHIP'}")


def main():
    scenarios = json.loads((HERE / "scenarios.json").read_text())
    if "--judge" in sys.argv:
        judge(scenarios)
    elif "--report" in sys.argv:
        report()
    else:
        generate(scenarios)


if __name__ == "__main__":
    main()
