"""LanguageTool pre-check (docs/feedback/2026-11-14 §2). No network: httpx.MockTransport."""
import json

import httpx
import pytest

from core.checkers.languagetool import (CheckerError, LanguageToolChecker, classify, combine,
                                        lt_language, matches_to_correction)
from core.feedback import ERROR_CATEGORIES
from eval import compare
from eval.run import CheckerProvider, load_cases, CASES_DIR, main, report_stem, run


def m(text, frag, repl, rule_id="X", cat="GRAMMAR", issue="grammar", message="msg"):
    off = text.index(frag)
    return {"offset": off, "length": len(frag), "message": message, "replacements": [{"value": repl}],
            "rule": {"id": rule_id, "issueType": issue, "category": {"id": cat}}}


@pytest.mark.parametrize("frag,repl,rule,cat,issue,want", [
    ("possible", "posible", "MORFOLOGIK_RULE_ES", "TYPOS", "misspelling", "spelling_accent"),
    ("esta", "está", "ES_DIACRITICS", "GRAMMAR", "grammar", "spelling_accent"),
    ("Donde", "¿Dónde", "Q_MARK", "PUNCTUATION", "typographical", "spelling_accent"),
    ("la problema", "el problema", "CONCORDANCIAS_DET_NOM", "GRAMMAR", "grammar", "gender"),
    ("a la cero", "al cero", "CONCORDANCIAS_DET_NOM", "GRAMMAR", "grammar", "gender"),
    ("soy cansado", "estoy cansado", "SER_ESTAR", "GRAMMAR", "grammar", "ser_estar"),
    ("la casa bonito", "la casa bonita", "CONCORDANCIAS_NOMBRE_ADJ", "GRAMMAR", "grammar", "agreement"),
    ("pienso de", "pienso en", "PENSAR_EN", "GRAMMAR", "grammar", "preposition"),
    ("muy muy", "muy", "REPETITION", "STYLE", "style", None),
])
def test_classify(frag, repl, rule, cat, issue, want):
    text = f"Hola, {frag} hoy."
    got, _ = classify(m(text, frag, repl, rule, cat, issue), frag, repl)
    assert got == want
    assert got is None or got in ERROR_CATEGORIES


def test_false_friend_is_lexical_transfer():
    text = "Estoy embarazada por el error."
    corr = matches_to_correction(text, [m(text, "embarazada", "avergonzada", "ES_FALSE_FRIEND", "FALSE_FRIENDS")],
                                 mother_tongue="en")
    assert corr["error_category"] == "lexical" and corr["is_transfer"] and corr["transfer_source"] == "en"


def test_all_replacements_applied_and_main_by_priority():
    text = "Es possible que la problema es grande."
    corr = matches_to_correction(text, [
        m(text, "possible", "posible", "MORFOLOGIK_RULE_ES", "TYPOS", "misspelling"),
        m(text, "la problema", "el problema", "CONCORDANCIAS_DET_NOM"),
    ], mother_tongue="ru")
    assert corr["corrected"] == "Es posible que el problema es grande."
    assert corr["original"] == text
    assert corr["error_category"] == "gender"          # grammar before spelling
    assert corr["explanation"].startswith("Род") and not corr["is_transfer"]


def test_no_matches_or_style_only_is_none():
    text = "Un café, porfa."
    assert matches_to_correction(text, []) is None
    assert matches_to_correction(text, [m(text, "porfa", "por favor", "COLLOQ", "COLLOQUIALISMS", "style")]) is None


def test_overlapping_matches_do_not_corrupt_text():
    text = "Donde esta la estacion?"
    corr = matches_to_correction(text, [
        m(text, "Donde esta", "¿Dónde está", "Q", "PUNCTUATION", "typographical"),
        m(text, "esta", "está", "DIAC"),
        m(text, "estacion", "estación", "MORFOLOGIK_RULE_ES", "TYPOS", "misspelling"),
    ])
    # the outer "Donde esta" overlaps the inner "esta": only the later, inner one is applied
    assert corr["corrected"] == "Donde está la estación?"


def test_language_code():
    assert lt_language("es-ES") == "es" and lt_language("es") == "es" and lt_language("es-AR") == "es-AR"


def _checker(handler, **kw):
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return LanguageToolChecker("http://lt.local/v2", client=client, **kw)


def test_checker_sends_only_the_sentence_and_parses():
    seen = []

    def handler(request):
        if request.url.path.endswith("/languages"):
            return httpx.Response(200, json=[])
        seen.append(dict(httpx.QueryParams(request.content.decode())))
        text = seen[-1]["text"]
        return httpx.Response(200, json={"matches": [m(text, "possible", "posible", "MORFOLOGIK_RULE_ES",
                                                       "TYPOS", "misspelling")]})

    lt = _checker(handler)
    assert lt.is_configured() and lt.model_name == "local" and lt.min_interval_s == 0
    corr = lt.check("Es possible.", target="es-ES", mother_tongue="ru")
    assert corr["corrected"] == "Es posible." and corr["error_category"] == "spelling_accent"
    assert seen == [{"text": "Es possible.", "language": "es", "motherTongue": "ru"}]
    assert lt.check("") is None and lt.check("x" * 3000) is None and len(seen) == 1


def test_checker_errors_and_rate_limit_pacing():
    lt = _checker(lambda r: httpx.Response(429, text="Too many requests"))
    with pytest.raises(CheckerError, match="429"):
        lt.check("Hola.")
    assert not _checker(lambda r: httpx.Response(500)).is_configured()

    t, waits = [0.0], []
    ok = _checker(lambda r: httpx.Response(200, json={"matches": []}), min_interval_s=3.5,
                  clock=lambda: t[0], sleeper=lambda s: (waits.append(s), t.__setitem__(0, t[0] + s)))
    ok.check("Uno.")
    t[0] += 1.0
    ok.check("Dos.")
    assert waits == [pytest.approx(2.5)]
    assert LanguageToolChecker(client=httpx.Client()).min_interval_s == 3.5   # public default


def test_combine_fill_policy():
    llm, lt = {"corrected": "a", "error_category": "lexical"}, {"corrected": "b", "error_category": "gender"}
    assert combine(llm, lt) == (llm, False)
    assert combine(None, lt) == (lt, True)
    assert combine(None, None) == (None, False)


# --- eval harness integration ---------------------------------------------

class FakeLT:
    name, model_name = "languagetool", "local"

    def __init__(self, fail=False):
        self.fail, self.calls = fail, 0

    def is_configured(self):
        return True

    def check(self, text, target="es", mother_tongue=None):
        self.calls += 1
        if self.fail:
            raise CheckerError("languagetool HTTP 429")
        if "possible" in text:
            return {"original": text, "corrected": text.replace("possible", "posible"),
                    "error_category": "spelling_accent", "cf_type": "explicit", "is_transfer": False,
                    "transfer_source": None, "explanation": "Орфография"}
        return None


def test_languagetool_alone_as_provider():
    cases = load_cases(CASES_DIR.glob("*.jsonl"))
    report = run(cases, CheckerProvider(FakeLT()))
    s = report["summary"]
    assert s["provider_failures"] == 0 and s["answered"] == len(cases)
    assert {r["source"] for r in report["cases"]} == {"languagetool"}
    assert s["detection_rate"] > 0     # at least the possible → posible case


def test_precheck_fills_rule_baseline_gaps():
    from eval.run import RuleProvider
    from core.llm.base import LLMProvider

    class Quiet(LLMProvider):
        name, model_name = "fake", "quiet"

        def is_configured(self):
            return True

        def generate_json(self, system_prompt, user_prompt):
            return {"reply": "Vale.", "roleplay_reply": "Vale.", "correction": None, "vocab": [],
                    "progress_note": "", "should_finish": False}

    cases = [c for c in load_cases(CASES_DIR.glob("*.jsonl")) if "possible" in c["original"]][:1]
    assert cases, "needs Roman's compliment case with 'possible'"
    lt = FakeLT()
    report = run(cases, Quiet(), precheck=lt)
    assert lt.calls == 1 and report["summary"]["precheck_filled"] == 1
    assert report["cases"][0]["precheck_filled"] and report["cases"][0]["correction"]["corrected"]

    report = run(cases, Quiet(), precheck=FakeLT(fail=True))
    assert report["summary"]["precheck_errors"] == 1 and not report["cases"][0]["provider_failed"]


def test_report_names_and_compare_groups():
    base = {"date": "2026-11-16", "provider": "ollama", "model": "gemma4:e2b", "profile": None}
    assert report_stem(base) == "2026-11-16-ollama-gemma4-e2b"
    assert report_stem({**base, "precheck": "languagetool"}) == "2026-11-16-ollama-gemma4-e2b-lt"
    assert report_stem({**base, "provider": "languagetool", "model": "public"}) == "2026-11-16-languagetool-public"
    summ = {"answered": 1, "per_category": {}}
    reps = [{"meta": {**base, "precheck": p}, "summary": summ} for p in (None, "languagetool")]
    out = compare.compare(reps)
    assert "gemma4:e2b + languagetool" in out          # not mixed with the plain run


def test_cli_rejects_precheck_without_llm(capsys):
    assert main(["--provider", "rule", "--precheck", "languagetool"]) == 2
    assert "needs an LLM" in capsys.readouterr().err


def test_hybrid_table_from_saved_reports(tmp_path):
    from eval import hybrid
    from eval.run import write_report
    from core.llm.base import LLMProvider

    class Quiet(LLMProvider):
        name, model_name = "ollama", "quiet:1b"

        def is_configured(self):
            return True

        def generate_json(self, system_prompt, user_prompt):
            return {"reply": "Vale.", "roleplay_reply": "Vale.", "correction": None, "vocab": [],
                    "progress_note": "", "should_finish": False}

    cases = load_cases(CASES_DIR.glob("*.jsonl"))
    date = "2026-11-16"
    llm = run(cases, Quiet())
    llm["meta"] = {"date": date, "provider": "ollama", "model": "quiet:1b", "profile": None}
    lt = run(cases, CheckerProvider(FakeLT()))
    lt["meta"] = {"date": date, "provider": "languagetool", "model": "local", "profile": None}
    for rep in (llm, lt):
        write_report(rep, tmp_path)
    by_id = {c["id"]: c for c in cases}
    summary = hybrid.hybrid_summary(llm, lt, by_id)
    assert summary["precheck_filled"] == 1 and summary["detection_rate"] > (llm["summary"]["detection_rate"] or 0)

    out = tmp_path / "hybrid.md"
    assert hybrid.main(["--reports", str(tmp_path), "--date", date, "--out", str(out)]) == 0
    md = out.read_text(encoding="utf-8")
    assert "ollama/quiet:1b" in md and "| 1 |" in md and "languagetool/" not in md

    write_report({**llm, "meta": {**llm["meta"], "date": "2026-11-17"}}, tmp_path)
    assert "No LanguageTool report" in hybrid.hybrid_table(
        [{**llm, "meta": {**llm["meta"], "date": "2026-11-17"}}], by_id)
