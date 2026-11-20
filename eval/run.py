"""
Correction eval harness (roadmap 1.3a).

    python -m eval.run --provider ollama --model qwen2.5:7b-instruct
    python -m eval.run --provider gemini --model gemini-2.5-flash
    python -m eval.run --provider rule            # baseline, no model
    python -m eval.run --provider gemini --sleep 6   # slower, for free-tier limits
    python -m eval.run --provider gemini --model gemini-2.5-flash --profile roman
    python -m eval.run --provider languagetool                 # LanguageTool alone, no LLM
    python -m eval.run --provider ollama --model gemma4:e2b --precheck languagetool

--provider languagetool scores LanguageTool's own correction (rule-based, no
LLM; LANGUAGETOOL_URL, default the public API). --precheck languagetool runs it
next to the LLM: the LLM's correction wins, LanguageTool fills the turns where
the LLM gave none (core/checkers/languagetool.combine, policy "fill"); the
report counts how many turns it filled (docs/feedback/2026-11-14 §2).

--profile <name> loads eval/profiles/<name>.json (a LearnerProfile) and runs every
case as that learner: the prompts then include the profile context and the
transfer-map hints (roadmap 1.2 + 1.5), as in the app after onboarding. Without
it the prompts are the legacy ones (no profile). The report and its file name
say which profile was used (docs/feedback/2026-11-11).

Runs every case in eval/cases/*.jsonl through LLMService.free_talk (same
prompts and normaliser as the app), scores the structured correction
(eval/scoring.py) and writes eval/reports/<date>-<provider>-<model>.json + .md.

Keys come only from the environment / local .env (GEMINI_API_KEY); they are
never written to reports or printed.

Free-tier rate limits (429/503): the runner waits --sleep seconds between
cases (default 4 s for gemini, 0 otherwise) and retries with a longer backoff
(EVAL_RETRY_DELAYS). Cases that still fail are counted as provider failures and
excluded from the quality metrics (docs/feedback/2026-11-08 §2).
A quota that resets in hours (e.g. Gemini free tier: 20 requests/day/model)
is not retried: the run stops calling the model, marks the remaining cases as
skipped failures and the report says so (PR #8, nightly eval 2026-11-09).
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

from core.checkers.languagetool import CheckerError, LanguageToolChecker, combine
from core.llm.base import LLMProvider
from core.llm_service import LLMService
from eval.scoring import aggregate, score_case

ROOT = Path(__file__).resolve().parent
CASES_DIR = ROOT / "cases"
PROFILES_DIR = ROOT / "profiles"
REPORTS_DIR = ROOT / "reports"
PROGRESS = {"mistakes": [], "vocabulary": [], "completed_scenarios": []}
EVAL_RETRY_DELAYS = [5.0, 15.0, 30.0]   # waits before retries 2..4 on 429/503
DEFAULT_SLEEP_S = {"gemini": 4.0}   # LanguageTool paces itself (min_interval_s)


class RuleProvider(LLMProvider):
    """Never configured → LLMService uses its rule-based fallback (baseline)."""
    name = "rule"
    model_name = None

    def is_configured(self) -> bool:
        return False

    def generate_json(self, system_prompt, user_prompt):  # pragma: no cover
        raise RuntimeError("rule provider has no model")


class CheckerProvider(LLMProvider):
    """A non-LLM checker scored as its own "provider" (no LLMService call)."""

    def __init__(self, checker):
        self.checker = checker
        self.name = checker.name
        self.model_name = checker.model_name

    def is_configured(self) -> bool:
        return self.checker.is_configured()

    def generate_json(self, system_prompt, user_prompt):  # pragma: no cover
        raise RuntimeError("checker provider has no model")


def _lt_args(case: Dict[str, Any]) -> Dict[str, Any]:
    return {"target": case.get("target", "es"), "mother_tongue": case.get("l1")}


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
    if name == "languagetool":
        return CheckerProvider(LanguageToolChecker())
    if name == "ollama":
        from core.llm.ollama_provider import OllamaProvider
        if model:
            os.environ["OLLAMA_MODEL"] = model
        return OllamaProvider()
    raise ValueError(f"unknown provider {name!r}")


def load_profile(name_or_path: str) -> Dict[str, Any]:
    """Profile fixture → app settings (validated like the onboarding form).
    Accepts a name from eval/profiles/ or a path to a JSON file."""
    from core.profile import LearnerProfile
    path = Path(name_or_path)
    if not path.suffix:
        path = PROFILES_DIR / f"{name_or_path}.json"
    if not path.is_file():
        names = sorted(p.stem for p in PROFILES_DIR.glob("*.json"))
        raise FileNotFoundError(f"profile {name_or_path!r} not found (available: {', '.join(names) or 'none'})")
    data = json.loads(path.read_text(encoding="utf-8"))
    settings = LearnerProfile(**data).to_settings()
    settings["profile_name"] = path.stem
    return settings


def settings_for(case: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    target = case.get("target", "es").split("-")[0]
    if profile and profile.get("target_language") == target:
        return profile
    return {"target_language": case.get("target", "es").split("-")[0],
            "native_language": case.get("l1", "ru"), "level": case.get("level", "A2"),
            "interests": []}


def _scrub(text: str) -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return text.replace(key, "***") if key else text


def run(cases: List[Dict[str, Any]], provider: LLMProvider, *, retry_delay: float = 1.5,
        retry_delays: Optional[List[float]] = None, sleep: float = 0.0,
        sleeper=time.sleep, clock=time.perf_counter, progress=None,
        profile: Optional[Dict[str, Any]] = None, precheck=None) -> Dict[str, Any]:
    svc = LLMService(provider=provider)
    svc.retry_delay = retry_delay
    svc.retry_delays = retry_delays
    expect_model = provider.name != "rule"
    filled = 0
    rows, latencies = [], []
    quota_stop: Optional[str] = None
    for i, case in enumerate(cases):
        if quota_stop:
            row = score_case(case, None)
            row.update({"latency_s": 0.0, "source": "skipped", "provider_failed": True,
                        "correction": None, "error": "skipped: provider quota exhausted"})
            rows.append(row)
            continue
        if i and sleep > 0:
            sleeper(sleep)
        start = clock()
        error, lt_error, lt_filled = None, None, False
        try:
            if isinstance(provider, CheckerProvider):
                out = {"correction": provider.checker.check(case["original"], **_lt_args(case)),
                       "source": provider.name}
            else:
                out = svc.free_talk(settings=settings_for(case, profile), progress=PROGRESS,
                                    history=[], message=case["original"])
        except Exception as e:  # keep going: one bad case must not kill the run
            out, error = {"correction": None, "source": "error"}, _scrub(f"{type(e).__name__}: {e}")
        if precheck is not None and error is None and out.get("source") != "fallback":
            try:
                lt = precheck.check(case["original"], **_lt_args(case))
            except CheckerError as e:
                lt, lt_error = None, str(e)[:300]
            out["correction"], lt_filled = combine(out.get("correction"), lt)
            filled += lt_filled
        elapsed = clock() - start
        failed = error is not None or (expect_model and out.get("source") == "fallback")
        row = score_case(case, out.get("correction"))
        row.update({"latency_s": round(elapsed, 3), "source": out.get("source"),
                    "provider_failed": failed, "correction": out.get("correction")})
        if error:
            row["error"] = error
        if precheck is not None:
            row["precheck_filled"] = lt_filled
            if lt_error:
                row["precheck_error"] = lt_error
        rows.append(row)
        if not failed:
            latencies.append(elapsed)
        if progress:
            mark = "FAIL" if failed else ("ok" if row["category_hit"] or not (row["expected_correction"] or row["false_positive"]) else "miss")
            progress(f"[{len(rows)}/{len(cases)}] {case['id']}: {mark} ({elapsed:.1f}s)")
        blocked = svc.quota_exhausted.get(provider.name)
        if blocked:
            quota_stop = _scrub(blocked[1])[:300]
            if progress:
                progress(f"quota exhausted after {len(rows)} cases: skipping the remaining "
                         f"{len(cases) - len(rows)} (retry another day or with fewer cases)")
    summary = aggregate(rows, latencies)
    summary["quota_stopped"] = quota_stop
    if precheck is not None:
        summary["precheck_filled"] = filled
        summary["precheck_errors"] = sum(1 for r in rows if r.get("precheck_error"))
    if profile:
        target = profile.get("target_language")
        summary["profile_cases"] = sum(1 for c in cases if c.get("target", "es").split("-")[0] == target)
    return {"summary": summary, "cases": rows}


def _pct(x: Optional[float]) -> str:
    return "—" if x is None else f"{x * 100:.0f}%"


def to_markdown(report: Dict[str, Any]) -> str:
    s, meta = report["summary"], report["meta"]
    lines = [
        f"# Eval {meta['date']} — {meta['provider']} / {meta['model'] or '-'}"
        + (f" — profile {meta['profile']}" if meta.get("profile") else "")
        + (f" + {meta['precheck']}" if meta.get("precheck") else ""),
        "",
        (f"Profile: **{meta['profile']}** (prompts include the profile context and transfer hints; "
         f"{s.get('profile_cases', s['cases'])}/{s['cases']} cases match its target language)."
         if meta.get("profile") else "Profile: none (legacy prompts, no profile context or transfer hints)."),
        "",
        *([f"Pre-check: **{meta['precheck']}** (policy \"fill\": the LLM's correction wins, the "
           f"checker fills turns without one): filled {s.get('precheck_filled', 0)} turns, "
           f"checker errors {s.get('precheck_errors', 0)}.", ""] if meta.get("precheck") else []),
        f"Cases: {s['cases']}, answered: {s['answered']} ({s['error_cases']} with errors, "
        f"{s['clean_cases']} correct). Provider failures: {s['provider_failures']} "
        "(excluded from the metrics below).",
        "",
    ]
    if s.get("quota_stopped"):
        lines += [f"**Stopped early: provider quota exhausted** after "
                  f"{sum(1 for r in report['cases'] if r.get('source') != 'skipped')} cases; "
                  "the rest were skipped. Compare this model on another day or with fewer cases.", ""]
    lines += [
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
    stem = f"{meta['date']}-{_slug(meta['provider'])}-{_slug(meta['model'] or 'none')}"
    if meta.get("precheck"):
        stem += "-lt" if meta["precheck"] == "languagetool" else f"-{_slug(meta['precheck'])}"
    return f"{stem}-{_slug(meta['profile'])}" if meta.get("profile") else stem


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
    ap.add_argument("--provider", choices=["gemini", "ollama", "rule", "languagetool"], required=True)
    ap.add_argument("--model", help="model name (default: provider env default)")
    ap.add_argument("--cases", nargs="*", type=Path, help="jsonl files (default: eval/cases/*.jsonl)")
    ap.add_argument("--id", action="append", dest="ids", help="run only this case id (repeatable)")
    ap.add_argument("--out", type=Path, default=REPORTS_DIR)
    ap.add_argument("--sleep", type=float, default=None,
                    help="seconds between cases (default: 4 for gemini, 0 otherwise)")
    ap.add_argument("--profile", help="learner profile from eval/profiles/ (e.g. roman) or a JSON path; "
                                      "default: no profile (legacy prompts)")
    ap.add_argument("--precheck", choices=["languagetool"],
                    help="run a non-LLM checker next to the LLM (its correction fills turns the LLM left uncorrected)")
    ap.add_argument("--date", type=dt.date.fromisoformat,
                    help="report date YYYY-MM-DD (default: today). The nightly script passes the "
                         "night's start date so a run that crosses midnight keeps one date.")
    args = ap.parse_args(argv)
    if args.precheck and args.provider in ("languagetool", "rule"):
        print("--precheck needs an LLM provider (gemini or ollama)", file=sys.stderr)
        return 2
    _utf8_stdio()

    profile = None
    if args.profile:
        try:
            profile = load_profile(args.profile)
        except Exception as e:
            print(f"bad profile: {e}", file=sys.stderr)
            return 2

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    provider = make_provider(args.provider, args.model)
    if args.provider != "rule" and not provider.is_configured():
        hint = {"gemini": "GEMINI_API_KEY in .env", "ollama": "a running Ollama with the model pulled",
                "languagetool": "network access to LANGUAGETOOL_URL (default: the public API)"}[args.provider]
        print(f"{args.provider} is not configured (need {hint}).", file=sys.stderr)
        return 2
    precheck = None
    if args.precheck:
        precheck = LanguageToolChecker()
        if not precheck.is_configured():
            print(f"languagetool not reachable at {precheck.url} (set LANGUAGETOOL_URL)", file=sys.stderr)
            return 2

    cases = load_cases(args.cases or CASES_DIR.glob("*.jsonl"), args.ids)
    if not cases:
        print("no cases found", file=sys.stderr)
        return 2
    sleep = args.sleep if args.sleep is not None else DEFAULT_SLEEP_S.get(args.provider, 0.0)
    report = run(cases, provider, sleep=sleep,
                 retry_delays=EVAL_RETRY_DELAYS if args.provider != "rule" else None,
                 progress=lambda line: print(line, file=sys.stderr, flush=True), profile=profile,
                 precheck=precheck)
    report["meta"] = {"date": (args.date or dt.date.today()).isoformat(), "provider": args.provider,
                      "model": getattr(provider, "model_name", None), "sleep_s": sleep,
                      "profile": profile["profile_name"] if profile else None,
                      "precheck": args.precheck,
                      "case_files": sorted({p.name for p in (args.cases or CASES_DIR.glob('*.jsonl'))})}
    path = write_report(report, args.out)
    print(to_markdown(report))
    print(f"report: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
