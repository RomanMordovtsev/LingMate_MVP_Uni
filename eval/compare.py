"""
Before/after table: the same model without a profile vs with one (docs/feedback/2026-11-11 §3).

    python -m eval.compare                    # latest date in eval/reports/
    python -m eval.compare --date 2026-11-16 --out eval/reports/compare-2026-11-16.md

Pairs eval/reports/<date>-<provider>-<model>.json with <...>-<profile>.json (meta.profile)
and prints a Markdown table of the metrics the transfer hints should move: transfer source,
lexical and register recall, plus detection / text match / false positives as a guard.
Paste it into the Monday report PR. Reports without a pair are listed, not compared.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from eval.run import REPORTS_DIR, _pct

METRICS = [("Detection", "detection_rate"), ("Category recall", "category_recall"),
           ("Text match", "text_match_rate"), ("False positives", "false_positive_rate"),
           ("Transfer source right", "transfer_accuracy")]
CATEGORIES = ["lexical", "register"]


def load_reports(reports_dir: Path, date: Optional[str] = None) -> List[Dict[str, Any]]:
    reports = []
    for path in sorted(reports_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict) and "meta" in data and "summary" in data:
            reports.append(data)
    if not reports:
        return []
    date = date or max(r["meta"]["date"] for r in reports)
    return [r for r in reports if r["meta"]["date"] == date]


def _value(summary: Dict[str, Any], key: str) -> Optional[float]:
    if key in CATEGORIES:
        return (summary.get("per_category", {}).get(key) or {}).get("recall")
    return summary.get(key)


def _delta(a: Optional[float], b: Optional[float], lower_is_better: bool = False) -> str:
    if a is None or b is None:
        return ""
    d = round((b - a) * 100)
    if d == 0:
        return " (=)"
    good = (d < 0) if lower_is_better else (d > 0)
    return f" ({'+' if d > 0 else ''}{d} {'↑' if good else '↓'})"


def compare(reports: List[Dict[str, Any]]) -> str:
    groups: Dict[Tuple[str, str], Dict[str, Dict[str, Any]]] = {}
    for r in reports:
        m = r["meta"]
        groups.setdefault((m["provider"], m.get("model") or "-"), {})[m.get("profile") or ""] = r
    if not reports:
        return "No reports found.\n"
    date = reports[0]["meta"]["date"]
    lines = [f"# Profile effect {date}: no profile → with profile", "",
             "Cells: without → with (difference in points; ↑ better). Metrics over answered cases only; "
             "check `answered` — a quota stop makes a column incomparable.", ""]
    keys = METRICS + [(f"`{c}` recall", c) for c in CATEGORIES]
    header = "| Model | Profile | Answered | " + " | ".join(k[0] for k in keys) + " |"
    lines += [header, "|" + "---|" * (3 + len(keys))]
    unpaired = []
    for (provider, model), by_profile in sorted(groups.items()):
        base = by_profile.get("")
        others = {p: r for p, r in by_profile.items() if p}
        if not base or not others:
            unpaired.append(f"{provider}/{model} ({', '.join(p or 'none' for p in by_profile)})")
            continue
        for prof, rep in sorted(others.items()):
            a, b = base["summary"], rep["summary"]
            cells = [f"{_pct(_value(a, k))} → {_pct(_value(b, k))}{_delta(_value(a, k), _value(b, k), k == 'false_positive_rate')}"
                     for _, k in keys]
            lines.append(f"| {provider}/{model} | {prof} | {a['answered']} → {b['answered']} | " + " | ".join(cells) + " |")
    if unpaired:
        lines += ["", "Not compared (no pair): " + "; ".join(unpaired)]
    lines += ["", "Caveat: the `en` hints name *línea* (Roman's real error), so the 3 `roman-*` cases are partly "
              "taught to the test; compare their lines under Misses in each report, and trust gains on the "
              "31 synthetic cases and Roman's live check more."]
    return "\n".join(lines) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Compare eval reports without vs with a learner profile")
    ap.add_argument("--reports", type=Path, default=REPORTS_DIR)
    ap.add_argument("--date", help="YYYY-MM-DD (default: latest)")
    ap.add_argument("--out", type=Path, help="also write the table to this .md file")
    args = ap.parse_args(argv)
    md = compare(load_reports(args.reports, args.date))
    if args.out:
        args.out.write_text(md, encoding="utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
