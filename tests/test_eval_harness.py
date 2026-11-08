"""Eval harness (roadmap 1.3a): scoring + runner with mock providers. No network, no keys."""
import json

from core.llm.base import LLMProvider
from eval import run as runner
from eval.scoring import aggregate, norm, score_case, text_matches

QUEUE = {"id": "q", "original": "No estoy en la línea.",
         "acceptable": ["No estoy en la cola.", "No estoy haciendo cola."],
         "error_categories": ["lexical"], "is_transfer": True, "transfer_source": "en"}
CLEAN = {"id": "c", "original": "Un café con leche, porfa.", "acceptable": ["Un café con leche, porfa."],
         "error_categories": [], "is_transfer": False, "expect_correction": False}


def corr(original, corrected, cat, transfer=None):
    return {"original": original, "corrected": corrected, "error_category": cat, "cf_type": "recast",
            "is_transfer": transfer is not None, "transfer_source": transfer, "explanation": "x"}


def test_norm_keeps_accents_drops_punctuation():
    assert norm("¿Dónde  está?") == "dónde está"
    assert norm("Esta bien") != norm("Está bien")


def test_text_match_full_fragment_and_substitution():
    assert text_matches(QUEUE, corr("", "No estoy en la cola", "lexical"))
    assert text_matches(QUEUE, corr("la línea", "la cola", "lexical"))   # substituted into sentence
    assert text_matches(QUEUE, corr("línea", "cola", "lexical"))         # fragment found in gold
    assert not text_matches(QUEUE, corr("la línea", "la fila", "lexical"))
    assert not text_matches(QUEUE, corr("No estoy", "No estoy", "lexical"))  # fragment already in original
    assert not text_matches(QUEUE, None)


def test_score_case_hit_miss_and_transfer():
    hit = score_case(QUEUE, corr("la línea", "la cola", "lexical", "en"))
    assert hit["category_hit"] and hit["text_match"] and hit["transfer_hit"] and not hit["false_positive"]
    wrong = score_case(QUEUE, corr("la línea", "la cola", "preposition"))
    assert not wrong["category_hit"] and wrong["text_match"] and not wrong["transfer_hit"]
    missed = score_case(QUEUE, None)
    assert not missed["detected"] and not missed["category_hit"]


def test_clean_case_false_positive():
    assert score_case(CLEAN, corr("porfa", "por favor", "register"))["false_positive"]
    assert not score_case(CLEAN, None)["false_positive"]


def test_aggregate_metrics():
    rows = [score_case(QUEUE, corr("la línea", "la cola", "lexical", "en")),
            score_case(QUEUE, corr("la línea", "la fila", "register")),
            score_case(QUEUE, None),
            score_case(CLEAN, corr("porfa", "por favor", "register")),
            score_case(CLEAN, None)]
    s = aggregate(rows, [1.0, 2.0, 3.0])
    assert s["error_cases"] == 3 and s["clean_cases"] == 2
    assert s["detection_rate"] == round(2 / 3, 3)
    assert s["category_recall"] == round(1 / 3, 3)
    assert s["category_precision"] == round(1 / 3, 3)   # 1 tp, 2 fp (register twice)
    assert s["false_positive_rate"] == 0.5
    assert s["per_category"]["lexical"] == {"tp": 1, "fp": 0, "fn": 2, "precision": 1.0, "recall": 0.333}
    assert s["per_category"]["register"]["fp"] == 2
    assert s["latency_s"] == {"mean": 2.0, "median": 2.0, "max": 3.0}


class GoldProvider(LLMProvider):
    """Answers every case with its first acceptable sentence, as a good model would."""
    name = "ollama"
    model_name = "mock:7b"

    def __init__(self, cases, fail_ids=()):
        self.by_text = {c["original"]: c for c in cases}
        self.fail_ids = set(fail_ids)

    def is_configured(self):
        return True

    def generate_json(self, system_prompt, user_prompt):
        msg = json.loads(user_prompt)["message"]
        case = self.by_text[msg]
        if case["id"] in self.fail_ids:
            raise RuntimeError("500 boom")
        correction = None
        if case.get("expect_correction", True):
            correction = {"original": case["original"], "corrected": case["acceptable"][0],
                          "error_category": case["error_categories"][0], "cf_type": "recast",
                          "is_transfer": case["is_transfer"], "transfer_source": case.get("transfer_source"),
                          "explanation": "ok"}
        return {"reply": "Vale.", "correction": correction, "vocab": [], "encouragement": ""}


def test_run_all_real_cases_with_gold_mock_scores_perfectly():
    cases = runner.load_cases(runner.CASES_DIR.glob("*.jsonl"))
    report = runner.run(cases, GoldProvider(cases), retry_delay=0)
    s = report["summary"]
    assert s["cases"] == len(cases) and s["provider_failures"] == 0
    assert s["detection_rate"] == s["category_recall"] == s["text_match_rate"] == 1.0
    assert s["category_precision"] == 1.0 and s["false_positive_rate"] == 0.0
    assert s["transfer_accuracy"] == 1.0


def test_run_counts_provider_failures_and_rule_baseline():
    cases = [dict(QUEUE, target="es-ES", l1="ru"), dict(CLEAN, original="¿Me pones una caña?",
                                                       acceptable=["¿Me pones una caña?"])]
    report = runner.run(cases, GoldProvider(cases, fail_ids={"q"}), retry_delay=0)
    assert report["summary"]["provider_failures"] == 1
    assert report["cases"][0]["source"] == "fallback" and report["cases"][0]["provider_failed"]

    base = runner.run(cases, runner.RuleProvider(), retry_delay=0)
    assert base["summary"]["provider_failures"] == 0   # fallback is the expected source for "rule"
    assert base["summary"]["detection_rate"] == 0.0


def test_main_writes_json_and_markdown_report(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    cases = tmp_path / "c.jsonl"
    cases.write_text(json.dumps(dict(QUEUE, target="es-ES", l1="ru")) + "\n", encoding="utf-8")
    assert runner.main(["--provider", "rule", "--cases", str(cases), "--out", str(tmp_path / "r")]) == 0
    files = sorted(p.name for p in (tmp_path / "r").iterdir())
    assert len(files) == 2 and files[0].endswith("-rule-none.json") and files[1].endswith(".md")
    data = json.loads((tmp_path / "r" / files[0]).read_text(encoding="utf-8"))
    assert data["meta"]["provider"] == "rule" and data["summary"]["cases"] == 1
    md = (tmp_path / "r" / files[1]).read_text(encoding="utf-8")
    assert "Category recall" in md and "`q`" in md   # miss listed


def test_main_refuses_unconfigured_gemini_without_leaking(monkeypatch, capsys):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)
    assert runner.main(["--provider", "gemini", "--model", "gemini-x"]) == 2
    assert "not configured" in capsys.readouterr().err


def test_errors_are_scrubbed_of_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "SECRET123")

    class Boom(GoldProvider):
        def generate_json(self, s, u):
            raise RuntimeError("bad key SECRET123")

    # force the exception path past LLMService's own error handling
    monkeypatch.setattr(runner.LLMService, "free_talk",
                        lambda self, **kw: (_ for _ in ()).throw(RuntimeError("bad key SECRET123")))
    report = runner.run([dict(QUEUE)], Boom([QUEUE]), retry_delay=0)
    assert "SECRET123" not in json.dumps(report) and report["cases"][0]["provider_failed"]


# --- docs/feedback/2026-11-08 ---------------------------------------------------

def test_report_names_keep_dots_and_sanitise_tags(tmp_path):
    names = set()
    for provider, model in [("gemini", "gemini-2.5-flash"), ("gemini", "gemini-2.0-flash"),
                            ("ollama", "qwen2.5:7b-instruct"), ("ollama", "qwen2.5:3b")]:
        report = {"meta": {"date": "2026-11-08", "provider": provider, "model": model},
                  "summary": aggregate([]), "cases": []}
        path = runner.write_report(report, tmp_path)
        names.add(path.name)
    assert "2026-11-08-gemini-gemini-2.5-flash.json" in names
    assert "2026-11-08-ollama-qwen2.5-7b-instruct.json" in names
    assert len(list(tmp_path.glob("*.json"))) == 4 and len(list(tmp_path.glob("*.md"))) == 4


def test_failures_are_excluded_from_metrics():
    cases = runner.load_cases(runner.CASES_DIR.glob("*.jsonl"))
    fail = {c["id"] for c in cases[:10]}
    s = runner.run(cases, GoldProvider(cases, fail_ids=fail), retry_delay=0)["summary"]
    assert s["provider_failures"] == 10 and s["answered"] == len(cases) - 10
    assert s["detection_rate"] == s["category_recall"] == 1.0   # failures are not misses


class FlakyProvider(GoldProvider):
    """Rate-limited: the first `n` calls raise 429."""
    def __init__(self, cases, n):
        super().__init__(cases)
        self.left = n

    def generate_json(self, s, u):
        if self.left:
            self.left -= 1
            raise RuntimeError("429 RESOURCE_EXHAUSTED")
        return super().generate_json(s, u)


def test_eval_backoff_retries_429_and_sleeps_between_cases():
    cases = [dict(QUEUE, target="es-ES", l1="ru"), dict(QUEUE, id="q2", original="Estoy en la línea.")]
    waits = []
    import core.llm_service as svc_mod
    orig = svc_mod.time.sleep
    svc_mod.time.sleep = waits.append
    try:
        report = runner.run(cases, FlakyProvider(cases, 3), retry_delays=[5, 15, 30],
                            sleep=4, sleeper=waits.append)
    finally:
        svc_mod.time.sleep = orig
    assert report["summary"]["provider_failures"] == 0
    assert waits == [5, 15, 30, 4]   # backoff on case 1, then the pause before case 2


def test_app_default_still_retries_once():
    cases = [dict(QUEUE, target="es-ES", l1="ru")]
    report = runner.run(cases, FlakyProvider(cases, 2), retry_delay=0)
    assert report["summary"]["provider_failures"] == 1


def test_transfer_diagnostics():
    rows = [score_case(QUEUE, corr("la línea", "la cola", "lexical", "en")),
            score_case(QUEUE, dict(corr("la línea", "la cola", "lexical"), is_transfer=True)),
            score_case(QUEUE, corr("la línea", "la cola", "lexical"))]
    s = aggregate(rows)
    assert s["transfer_flagged_rate"] == round(2 / 3, 3)
    assert s["transfer_source_filled"] == 0.5


def test_markdown_lists_failures_separately():
    cases = [dict(QUEUE, target="es-ES", l1="ru")]
    report = runner.run(cases, GoldProvider(cases, fail_ids={"q"}), retry_delay=0)
    report["meta"] = {"date": "d", "provider": "ollama", "model": "m"}
    md = runner.to_markdown(report)
    assert "Provider failures (not scored)" in md and "## Misses" not in md


def test_main_survives_cp1251_console(tmp_path, monkeypatch):
    import io, sys
    out = io.TextIOWrapper(io.BytesIO(), encoding="cp1251")
    monkeypatch.setattr(sys, "stdout", out)
    cases = [dict(QUEUE, target="es-ES", l1="ru")]

    class WrongCat(GoldProvider):   # a miss → "la línea → la cola [preposition]" in the markdown
        def generate_json(self, s, u):
            r = super().generate_json(s, u)
            r["correction"]["error_category"] = "preposition"
            return r

    monkeypatch.setattr(runner, "make_provider", lambda name, model: WrongCat(cases))
    f = tmp_path / "c.jsonl"
    f.write_text(json.dumps(cases[0]) + "\n", encoding="utf-8")
    assert runner.main(["--provider", "ollama", "--cases", str(f), "--out", str(tmp_path / "r"),
                        "--sleep", "0"]) == 0
    out.flush()
    assert "→".encode("utf-8") in out.buffer.getvalue()
