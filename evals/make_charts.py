#!/usr/bin/env python3
"""Generate the README charts (SVG) from benchmark results.

Reads results/results.json and results/raw/*__judge__*.json, writes
../assets/*.svg. No dependencies. Run after a benchmark run:

  python3 evals/make_charts.py
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "results"
ASSETS = HERE.parent / "assets"

FONT = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
GRAY = "#9aa2ac"    # baseline bars
BLUE = "#6ea8fe"    # simple-english bars
GREEN = "#3fb950"   # agent-ste bars
TEXT = "#8b949e"    # legible on light and dark GitHub themes

COND_LABELS = [("No skill", GRAY), ("SimpleEnglish", BLUE), ("agent-ste", GREEN)]


def short(model):
    return model.removesuffix("-medium")


def legend(x, y):
    parts, cx = [], x
    for label, color in COND_LABELS:
        parts.append(f'<rect x="{cx}" y="{y}" width="12" height="12" rx="2" fill="{color}"/>')
        parts.append(f'<text x="{cx + 17}" y="{y + 10}" font-family="{FONT}" '
                     f'font-size="12" fill="{TEXT}">{label}</text>')
        cx += 17 + 8 * len(label) + 28
    return parts


def mean_chart(models):
    means = []
    for key in ("baseline_viol_per_100w", "simple_english_viol_per_100w", "agent_ste_viol_per_100w"):
        means.append(sum(m[key] for m in models) / len(models))
    width, label_w, bar_span = 720, 130, 470
    xmax = 2.5
    rows = []
    y = 34
    for (label, color), val in zip(COND_LABELS, means):
        w = max(2, val / xmax * bar_span)
        rows.append(f'<text x="{label_w - 8}" y="{y + 15}" text-anchor="end" '
                    f'font-family="{FONT}" font-size="13" fill="{TEXT}">{label}</text>')
        rows.append(f'<rect x="{label_w}" y="{y}" width="{w:.1f}" height="20" rx="3" fill="{color}"/>')
        rows.append(f'<text x="{label_w + w + 8:.1f}" y="{y + 15}" font-family="{FONT}" '
                    f'font-size="13" font-weight="600" fill="{TEXT}">{val:.2f}</text>')
        y += 30
    title = (f'<text x="{label_w}" y="18" font-family="{FONT}" font-size="12" '
             f'fill="{TEXT}">STE violations per 100 words, mean of 12 models x 8 tasks (lower is better)</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y + 8}" '
           f'viewBox="0 0 {width} {y + 8}">{title}{"".join(rows)}</svg>')
    (ASSETS / "violations-mean.svg").write_text(svg)


def per_model_chart(models):
    width, label_w, bar_span = 760, 185, 500
    xmax = 4.5
    bar_h, bar_gap, row_gap = 11, 2, 10
    row_h = 3 * (bar_h + bar_gap) + row_gap
    top = 30
    parts = legend(label_w, 6)
    keys = ("baseline_viol_per_100w", "simple_english_viol_per_100w", "agent_ste_viol_per_100w")
    y = top
    for m in sorted(models, key=lambda m: -m["baseline_viol_per_100w"]):
        parts.append(f'<text x="{label_w - 8}" y="{y + 20}" text-anchor="end" '
                     f'font-family="{FONT}" font-size="12" fill="{TEXT}">{short(m["model"])}</text>')
        by = y
        for key, (_, color) in zip(keys, COND_LABELS):
            val = m[key]
            w = max(2, val / xmax * bar_span)
            parts.append(f'<rect x="{label_w}" y="{by}" width="{w:.1f}" height="{bar_h}" rx="2" fill="{color}"/>')
            parts.append(f'<text x="{label_w + w + 6:.1f}" y="{by + 9.5}" font-family="{FONT}" '
                         f'font-size="10" fill="{TEXT}">{val:.2f}</text>')
            by += bar_h + bar_gap
        y += row_h
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y}" '
           f'viewBox="0 0 {width} {y}">{"".join(parts)}</svg>')
    (ASSETS / "violations-by-model.svg").write_text(svg)


def judge_chart():
    wins = ties = losses = 0
    for f in RESULTS.glob("raw/*__judge__*.json"):
        j = json.loads(f.read_text())
        try:
            theirs = (j["order1_theirs_first"]["a_score"] + j["order2_ours_first"]["b_score"]) / 2
            ours = (j["order1_theirs_first"]["b_score"] + j["order2_ours_first"]["a_score"]) / 2
        except (KeyError, TypeError):
            continue
        if ours > theirs:
            wins += 1
        elif ours < theirs:
            losses += 1
        else:
            ties += 1
    total = wins + ties + losses
    width, label_w, bar_span = 720, 130, 470
    x = label_w
    parts = [f'<text x="{label_w}" y="18" font-family="{FONT}" font-size="12" fill="{TEXT}">'
             f'Blind pairwise judge, {total} pairs: agent-ste vs SimpleEnglish</text>']
    y = 34
    for n, label, color in ((wins, "agent-ste wins", GREEN), (ties, "ties", GRAY),
                            (losses, "SimpleEnglish wins", BLUE)):
        w = n / total * bar_span
        parts.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="22" fill="{color}"/>')
        parts.append(f'<text x="{x + w / 2:.1f}" y="{y + 15}" text-anchor="middle" '
                     f'font-family="{FONT}" font-size="12" font-weight="600" fill="#fff">{n}</text>')
        x += w
    ly = y + 40
    lx = label_w
    for n, label, color in ((wins, "agent-ste wins", GREEN), (ties, "ties", GRAY),
                            (losses, "SimpleEnglish wins", BLUE)):
        parts.append(f'<rect x="{lx}" y="{ly}" width="12" height="12" rx="2" fill="{color}"/>')
        parts.append(f'<text x="{lx + 17}" y="{ly + 10}" font-family="{FONT}" font-size="12" '
                     f'fill="{TEXT}">{label}</text>')
        lx += 17 + 7 * len(label) + 28
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{ly + 22}" '
           f'viewBox="0 0 {width} {ly + 22}">{"".join(parts)}</svg>')
    (ASSETS / "judge.svg").write_text(svg)
    print(f"judge: {wins} wins / {ties} ties / {losses} losses ({total} pairs)")


def main():
    ASSETS.mkdir(exist_ok=True)
    models = json.loads((RESULTS / "results.json").read_text())["models"]
    mean_chart(models)
    per_model_chart(models)
    judge_chart()
    print(f"wrote 3 charts to {ASSETS}")


if __name__ == "__main__":
    main()
