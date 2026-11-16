"""
LLM alone vs LLM + LanguageTool, computed from one night's reports — no extra
model calls (docs/feedback/2026-11-14 §2; roadmap 5.7 hybrid pipelines).

    python -m eval.hybrid                         # latest date in eval/reports/
    python -m eval.hybrid --date 2026-11-16 --out eval/reports/hybrid-2026-11-16.md

Needs the night's `<date>-languagetool-*.json` (python -m eval.run --provider
languagetool). For every LLM report of that date the per-case corrections are
combined with LanguageTool's by the same "fill" policy as --precheck (the LLM's
correction wins, LanguageTool fills turns without one) and re-scored with the
same scoring. A live `--precheck languagetool` run gives the same numbers.
"""
import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.checkers.languagetool import combine
from eval.compare import _delta, load_reports
from eval.run import CASES_DIR, REPORTS_DIR, _pct, load_cases
from eval.scoring import aggregate, score_case

FOCUS = ["spelling_accent", "agreement", "gender"]   # where a rule checker should help
METRICS = [("Detection", "detection_rate"), ("Category recall", "category_recall"),
           ("Text match", "text_match_rate"), ("False positives", "false_positive_rate")]


def hybrid_summary(llm: Dict[str, Any], lt: Dict[str, Any], cases: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    lt_by_id = {r["id"]: r for r in lt["cases"]}
    rows, filled = [], 0
    for r in llm["cases"]:
        case = cases.get(r["id"])
        if case is None:
            continue
        if r.get("provider_failed"):
            rows.append({**score_case(case, None), "provider_failed": True})
            continue
        lt_row = lt_by_id.get(r["id"]) or {}
        lt_corr = None if lt_row.get("provider_failed") else lt_row.get("correction")
        corr, used = combine(r.get("correction"), lt_corr)
        filled += used
        rows.append(score_case(case, corr))
    summary = aggregate(rows)
    summary["precheck_filled"] = filled
    return summary


def _value(summary: Dict[str, Any], key: str) -> Optional[float]:
    if key in FOCUS:
        return (summary.get("per_category", {}).get(key) or {}).get("recall")
    return summary.get(key)


def hybrid_table(reports: List[Dict[str, Any]], cases: Dict[str, Dict[str, Any]]) -> str:
    if not reports:
        return "No reports found.\n"
    date = reports[0]["meta"]["date"]
    lt = next((r for r in reports if r["meta"]["provider"] == "languagetool"), None)
    if lt is None:
        return (f"# LLM + LanguageTool {date}\n\nNo LanguageTool report for this date "
                "(run `python -m eval.run --provider languagetool`).\n")
    keys = METRICS + [(f"`{c}` recall", c) for c in FOCUS]
    lines = [f"# LLM + LanguageTool {date}: LLM alone → hybrid (policy \"fill\")", "",
             f"LanguageTool alone ({lt['meta'].get('model')}): " + ", ".join(
                 f"{name.lower()} {_pct(_value(lt['summary'], k))}" for name, k in keys) + ".", "",
             "Cells: LLM alone → LLM + LanguageTool (difference in points; ↑ better). "
             "*Filled* = turns where only LanguageTool gave a correction.", "",
             "| Model | Profile | Filled | " + " | ".join(k[0] for k in keys) + " |",
             "|" + "---|" * (3 + len(keys))]
    for rep in sorted(reports, key=lambda r: (r["meta"]["provider"], r["meta"].get("model") or "",
                                              r["meta"].get("profile") or "")):
        m = rep["meta"]
        if m["provider"] in ("languagetool", "rule") or m.get("precheck"):
            continue
        a, b = rep["summary"], hybrid_summary(rep, lt, cases)
        cells = [f"{_pct(_value(a, k))} → {_pct(_value(b, k))}"
                 f"{_delta(_value(a, k), _value(b, k), k == 'false_positive_rate')}" for _, k in keys]
        lines.append(f"| {m['provider']}/{m.get('model') or '-'} | {m.get('profile') or 'none'} | "
                     f"{b['precheck_filled']} | " + " | ".join(cells) + " |")
    lines += ["", "Watch *False positives*: LanguageTool also flags correct colloquial turns; "
              "a hybrid that gains detection but loses here is not better for the learner."]
    return "\n".join(lines) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="LLM alone vs LLM + LanguageTool from saved reports")
    ap.add_argument("--reports", type=Path, default=REPORTS_DIR)
    ap.add_argument("--date", help="YYYY-MM-DD (default: latest)")
    ap.add_argument("--out", type=Path, help="also write the table to this .md file")
    args = ap.parse_args(argv)
    cases = {c["id"]: c for c in load_cases(CASES_DIR.glob("*.jsonl"))}
    md = hybrid_table(load_reports(args.reports, args.date), cases)
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
