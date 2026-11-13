"""eval.run --profile (docs/feedback/2026-11-11 §1): prompts with profile context + transfer hints."""
import json

import pytest

from core.llm.base import LLMProvider
from eval import run as runner

QUEUE = {"id": "q", "original": "No estoy en la línea.", "target": "es-ES", "l1": "ru",
         "acceptable": ["No estoy en la cola."], "error_categories": ["lexical"],
         "is_transfer": True, "transfer_source": "en"}


class SpyProvider(LLMProvider):
    name = "ollama"
    model_name = "mock:3b"

    def __init__(self):
        self.prompts = []

    def is_configured(self):
        return True

    def generate_json(self, system_prompt, user_prompt):
        self.prompts.append(system_prompt)
        return {"reply": "Vale.", "vocab": [], "encouragement": "",
                "correction": {"original": "línea", "corrected": "cola", "error_category": "lexical",
                               "cf_type": "recast", "is_transfer": True, "transfer_source": "en",
                               "explanation": "x"}}


def test_roman_fixture_is_valid_and_has_no_italian():
    s = runner.load_profile("roman")
    codes = {l["code"]: l["level"] for l in s["languages"]}
    assert codes == {"ru": "L1", "en": "C1"}          # Roman doesn't remember Italian
    assert s["target_language"] == "es" and s["target_variant"] == "es-ES" and s["level"] == "A2"
    assert s["goal"] == "relocated" and s["city"] == "Vitoria-Gasteiz"
    assert s["onboarding_completed"] and s["profile_name"] == "roman"


def test_every_profile_fixture_validates():
    for path in runner.PROFILES_DIR.glob("*.json"):
        assert runner.load_profile(path.stem)["onboarding_completed"]


def test_unknown_profile_names_available_ones():
    with pytest.raises(FileNotFoundError, match="roman"):
        runner.load_profile("nobody")


def test_profile_adds_context_and_hints_to_prompts_without_it_legacy():
    plain, spied = SpyProvider(), SpyProvider()
    runner.run([QUEUE], plain, retry_delay=0)
    report = runner.run([QUEUE], spied, retry_delay=0, profile=runner.load_profile("roman"))
    assert "Likely transfer" not in plain.prompts[0] and "Learner profile" not in plain.prompts[0]
    p = spied.prompts[0]
    assert "Learner profile" in p and "Vitoria-Gasteiz" in p and "English (C1)" in p
    assert "Likely transfer" in p and "[en]" in p and "Italian" not in p
    assert report["summary"]["profile_cases"] == 1
    # the app's transfer note is attached too, as for an onboarded learner
    assert report["cases"][0]["correction"].get("transfer_note")


def test_case_in_other_target_language_keeps_its_own_settings():
    profile = runner.load_profile("roman")
    other = dict(QUEUE, target="it-IT")
    assert runner.settings_for(other, profile)["target_language"] == "it"
    assert runner.settings_for(QUEUE, profile) is profile


def test_main_profile_in_report_name_and_markdown(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    cases = tmp_path / "c.jsonl"
    cases.write_text(json.dumps(QUEUE) + "\n", encoding="utf-8")
    out = tmp_path / "r"
    assert runner.main(["--provider", "rule", "--cases", str(cases), "--out", str(out), "--profile", "roman"]) == 0
    assert runner.main(["--provider", "rule", "--cases", str(cases), "--out", str(out)]) == 0
    names = sorted(p.name for p in out.iterdir())
    assert any(n.endswith("-rule-none-roman.json") for n in names)
    assert any(n.endswith("-rule-none.json") for n in names)       # no-profile run not overwritten
    data = json.loads(next(out.glob("*-roman.json")).read_text(encoding="utf-8"))
    assert data["meta"]["profile"] == "roman"
    md = next(out.glob("*-roman.md")).read_text(encoding="utf-8")
    assert "profile roman" in md and "Profile: **roman**" in md
    md_plain = next(p for p in out.glob("*.md") if not p.name.endswith("-roman.md")).read_text(encoding="utf-8")
    assert "Profile: none" in md_plain


def test_main_bad_profile_exits_2(tmp_path, capsys):
    assert runner.main(["--provider", "rule", "--profile", "nobody", "--out", str(tmp_path)]) == 2
    assert "bad profile" in capsys.readouterr().err


def _report(tmp, model, profile, det, lex, fp, answered=30):
    from eval import compare  # noqa: F401
    meta = {"date": "2026-11-16", "provider": "ollama", "model": model, "profile": profile}
    summary = {"answered": answered, "detection_rate": det, "category_recall": det, "text_match_rate": 0.5,
               "false_positive_rate": fp, "transfer_accuracy": None,
               "per_category": {"lexical": {"recall": lex}, "register": {"recall": 0.0}}}
    stem = runner.report_stem(meta)
    (tmp / f"{stem}.json").write_text(json.dumps({"meta": meta, "summary": summary, "cases": []}), encoding="utf-8")


def test_compare_pairs_profile_runs_and_marks_direction(tmp_path):
    from eval import compare
    _report(tmp_path, "m:3b", None, 0.5, 0.0, 0.2)
    _report(tmp_path, "m:3b", "roman", 0.75, 0.5, 0.0)
    _report(tmp_path, "solo:1b", None, 0.1, 0.0, 0.0)
    (tmp_path / "junk.json").write_text("[]", encoding="utf-8")
    md = compare.compare(compare.load_reports(tmp_path))
    row = next(l for l in md.splitlines() if l.startswith("| ollama/m:3b"))
    assert "| roman |" in row and "50% → 75% (+25 ↑)" in row
    assert "20% → 0% (-20 ↑)" in row          # fewer false positives is better
    assert "0% → 50% (+50 ↑)" in row          # lexical recall
    assert "Not compared" in md and "solo:1b" in md


def test_compare_main_writes_file_and_picks_latest_date(tmp_path, capsys):
    from eval import compare
    _report(tmp_path, "m:3b", None, 0.5, 0.0, 0.0)
    _report(tmp_path, "m:3b", "roman", 0.5, 0.0, 0.0)
    out = tmp_path / "cmp.md"
    assert compare.main(["--reports", str(tmp_path), "--out", str(out)]) == 0
    assert "2026-11-16" in out.read_text(encoding="utf-8") and "(=)" in capsys.readouterr().out
    assert "No reports" in compare.compare(compare.load_reports(tmp_path, "2020-01-01"))
