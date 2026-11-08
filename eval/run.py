"""
Correction eval harness (roadmap 1.3a).

    python -m eval.run --provider ollama --model qwen2.5:7b-instruct
    python -m eval.run --provider gemini --model gemini-2.5-flash
    python -m eval.run --provider rule            # baseline, no model
    python -m eval.run --provider gemini --sleep 6   # slower, for free-tier limits

Runs every case in eval/cases/*.jsonl through LLMService.free_talk (same
prompts and normaliser as the app), scores the structured correction
(eval/scoring.py) and writes eval/reports/<date>-<provider>-<model>.json + .md.

Keys come only from the environment / local .env (GEMINI_API_KEY); they are
never written to reports or printed.

Free-tier rate limits (429/503): the runner waits --sleep seconds between
cases (default 4 s for gemini, 0 otherwise) and retries with a longer backoff
(EVAL_RETRY_DELAYS). Cases that still fail are counted as provider failures and
excluded from the quality metrics (docs/feedback/2026-11-08 §2).
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from core.llm.base import LLMProvider
from core.llm_service import LLMService
from eval.scoring import aggregate, score_case

ROOT = Path(__file__).resolve().parent
CASES_DIR = ROOT / "cases"
REPORTS_DIR = ROOT / "reports"
PROGRESS = {"mistakes": [], "vocabulary": [], "completed_scenarios": []}
EVAL_RETRY_DELAYS = [5.0, 15.0, 30.0]   # waits before retries 2..4 on 429/503
DEFAULT_SLEEP_S = {"gemini": 4.0}


class RuleProvider(LLMProvider):
    """Never configured → LLMService uses its rule-based fallback (baseline)."""
    name = "rule"
    model_name = None

    def is_configured(self) -> bool:
        return False

    def generate_json(self, system_prompt, user_prompt):  # pragma: no cover
        raise RuntimeError("rule provider has no model")


def load_cases(paths: Iterable[Path], ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    cases = []
    for path in sorted(paths):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                case = json.loads(line)
                if not ids or case["id"] in ids:
                    cases.append(case)
    return cases


def make_provider(name: str, model: Optional[str]) -> LLMProvider:
    if name == "rule":
        return RuleProvider()
    if name == "gemini":
        from core.llm.gemini_provider import GeminiProvider
        if model:
            os.environ["GEMINI_MODEL"] = model
        return GeminiProvider()
    if name == "ollama":
        from core.llm.ollama_provider import OllamaProvider
        if model:
            os.environ["OLLAMA_MODEL"] = model
        return OllamaProvider()
    raise ValueError(f"unknown provider {name!r}")


def settings_for(case: Dict[str, Any]) -> Dict[str, Any]:
    return {"target_language": case.get("target", "es").split("-")[0],
            "native_language": case.get("l1", "ru"), "level": case.get("level", "A2"),
            "interests": []}


def _scrub(text: str) -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return text.replace(key, "***") if key else text


def run(cases: List[Dict[str, Any]], provider: LLMProvider, *, retry_delay: float = 1.5,
        retry_delays: Optional[List[float]] = None, sleep: float = 0.0,
        sleeper=time.sleep, clock=time.perf_counter, progress=None) -> Dict[str, Any]:
    svc = LLMService(provider=provider)
    svc.retry_delay = retry_delay
    svc.retry_delays = retry_delays
    expect_model = provider.name != "rule"
    rows, latencies = [], []
    for i, case in enumerate(cases):
        if i and sleep > 0:
            sleeper(sleep)
        start = clock()
        error = None
        try:
            out = svc.free_talk(settings=settings_for(case), progress=PROGRESS,
                                history=[], message=case["original"])
        except Exception as e:  # keep going: one bad case must not kill the run
            out, error = {"correction": None, "source": "error"}, _scrub(f"{type(e).__name__}: {e}")
        elapsed = clock() - start
        failed = error is not None or (expect_model and out.get("source") == "fallback")
        row = score_case(case, out.get("correction"))
        row.update({"latency_s": round(elapsed, 3), "source": out.get("source"),
                    "provider_failed": failed, "correction": out.get("correction")})
        if error:
            row["error"] = error
        rows.append(row)
        if not failed:
            latencies.append(elapsed)
        if progress:
            mark = "FAIL" if failed else ("ok" if row["category_hit"] or not (row["expected_correction"] or row["false_positive"]) else "miss")
            progress(f"[{len(rows)}/{len(cases)}] {case['id']}: {mark} ({elapsed:.1f}s)")
    summary = aggregate(rows, latencies)
    return {"summary": summary, "cases": rows}


def _pct(x: Optional[float]) -> str:
    return "—" if x is None else f"{x * 100:.0f}%"


def to_markdown(report: Dict[str, Any]) -> str:
    s, meta = report["summary"], report["meta"]
    lines = [
        f"# Eval {meta['date']} — {meta['provider']} / {meta['model'] or '-'}",
        "",
        f"Cases: {s['cases']}, answered: {s['answered']} ({s['error_cases']} with errors, "
        f"{s['clean_cases']} correct). Provider failures: {s['provider_failures']} "
        "(excluded from the metrics below).",
        "",
        "| Metric | Value |", "|---|---|",
        f"| Detection (error cases) | {_pct(s['detection_rate'])} |",
        f"| Category recall | {_pct(s['category_recall'])} |",
        f"| Category precision | {_pct(s['category_precision'])} |",
        f"| Corrected text matches gold | {_pct(s['text_match_rate'])} |",
        f"| False positives on correct input | {_pct(s['false_positive_rate'])} |",
        f"| Transfer source right | {_pct(s['transfer_accuracy'])} |",
        f"| Transfer flagged (gold transfer, detected) | {_pct(s['transfer_flagged_rate'])} |",
        f"| transfer_source filled when flagged | {_pct(s['transfer_source_filled'])} |",
        f"| Latency mean / median / max, s | {s['latency_s']['mean']} / {s['latency_s']['median']} / {s['latency_s']['max']} |",
        "", "## Per category", "", "| Category | P | R | tp | fp | fn |", "|---|---|---|---|---|---|",
    ]
    for cat, m in s["per_category"].items():
        lines.append(f"| {cat} | {_pct(m['precision'])} | {_pct(m['recall'])} | {m['tp']} | {m['fp']} | {m['fn']} |")
    misses = [r for r in report["cases"] if not r.get("provider_failed")
              and (r["expected_correction"] and not (r["category_hit"] and r["text_match"])) or r["false_positive"]]
    if misses:
        lines += ["", "## Misses", ""]
        for r in misses:
            c = r.get("correction") or {}
            got = f"{c.get('original', '')} → {c.get('corrected', '')} [{c.get('error_category')}]" if c else "no correction"
            lines.append(f"- `{r['id']}` gold {r['gold_categories'] or 'none'}: {got}")
    failed = [r for r in report["cases"] if r.get("provider_failed")]
    if failed:
        lines += ["", "## Provider failures (not scored)", ""]
        lines += [f"- `{r['id']}`: {r.get('error') or r.get('source')}" for r in failed]
    return "\n".join(lines) + "\n"


def _slug(text: str) -> str:
    # ":" and "/" (ollama tags, org/model) become "-"; dots stay ("gemini-2.5-flash").
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-.") or "default"


def report_stem(meta: Dict[str, Any]) -> str:
    return f"{meta['date']}-{_slug(meta['provider'])}-{_slug(meta['model'] or 'none')}"


def write_report(report: Dict[str, Any], out_dir: Path) -> Path:
    # Append extensions as text: Path.with_suffix would cut "gemini-2.5-flash" at
    # the first dot and let models overwrite each other (docs/feedback/2026-11-08 §1).
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = report_stem(report["meta"])
    json_path, md_path = out_dir / f"{stem}.json", out_dir / f"{stem}.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(to_markdown(report), encoding="utf-8")
    return json_path


def _utf8_stdio() -> None:
    """Windows consoles are cp1251: never crash on Spanish text (feedback 2026-11-08 §4)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="LingMate correction eval (roadmap 1.3a)")
    ap.add_argument("--provider", choices=["gemini", "ollama", "rule"], required=True)
    ap.add_argument("--model", help="model name (default: provider env default)")
    ap.add_argument("--cases", nargs="*", type=Path, help="jsonl files (default: eval/cases/*.jsonl)")
    ap.add_argument("--id", action="append", dest="ids", help="run only this case id (repeatable)")
    ap.add_argument("--out", type=Path, default=REPORTS_DIR)
    ap.add_argument("--sleep", type=float, default=None,
                    help="seconds between cases (default: 4 for gemini, 0 otherwise)")
    args = ap.parse_args(argv)
    _utf8_stdio()

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    provider = make_provider(args.provider, args.model)
    if args.provider != "rule" and not provider.is_configured():
        hint = "GEMINI_API_KEY in .env" if args.provider == "gemini" else "a running Ollama with the model pulled"
        print(f"{args.provider} is not configured (need {hint}).", file=sys.stderr)
        return 2

    cases = load_cases(args.cases or CASES_DIR.glob("*.jsonl"), args.ids)
    if not cases:
        print("no cases found", file=sys.stderr)
        return 2
    sleep = args.sleep if args.sleep is not None else DEFAULT_SLEEP_S.get(args.provider, 0.0)
    report = run(cases, provider, sleep=sleep,
                 retry_delays=EVAL_RETRY_DELAYS if args.provider != "rule" else None,
                 progress=lambda line: print(line, file=sys.stderr, flush=True))
    report["meta"] = {"date": dt.date.today().isoformat(), "provider": args.provider,
                      "model": getattr(provider, "model_name", None), "sleep_s": sleep,
                      "case_files": sorted({p.name for p in (args.cases or CASES_DIR.glob('*.jsonl'))})}
    path = write_report(report, args.out)
    print(to_markdown(report))
    print(f"report: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
