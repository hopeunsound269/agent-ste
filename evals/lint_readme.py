#!/usr/bin/env python3
"""Lint a markdown document's prose with the upstream STE linter.

The linter (ste_lint.py, byte-identical to AminBlg/SimpleEnglish) parses
prose, not markdown layout. Before the lint pass, this wrapper removes the
lines the linter cannot parse as sentences:

- table rows (lines that start with "|")
- badge and image lines (lines that start with "[![", "![", or "<")

Everything else in the document is prose and gets zero tolerance. CI fails
when the prose contains one or more violations.

Usage: python3 lint_readme.py README.md
"""
import json
import pathlib
import sys

import ste_lint


def prose_of(path):
    lines = pathlib.Path(path).read_text().splitlines()
    kept = [ln for ln in lines
            if not ln.lstrip().startswith(("|", "[![", "![", "<"))]
    return "\n".join(kept)


def main():
    path = sys.argv[1]
    report = ste_lint.lint(prose_of(path), "descriptive")
    print(json.dumps(report, indent=2))
    if report["violations_total"] > 0:
        print(f"FAIL: {path} prose has {report['violations_total']} STE violation(s)")
        sys.exit(1)
    print(f"PASS: {path} prose has 0 STE violations")


if __name__ == "__main__":
    main()
