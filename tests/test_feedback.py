"""Structured corrective feedback (roadmap 1.3) and provider retry (docs/feedback/2026-11-05 §1).
No network: providers are fakes."""
import json

from core.feedback import (CF_TYPES, ERROR_CATEGORIES, correction_contract,
                           correction_to_text, normalize_correction)
from core.llm.base import LLMProvider
from core.llm_service import LLMService
from tests.test_eval_cases import _cases

SETTINGS = {"target_language": "es", "native_language": "ru", "level": "A2"}
PROGRESS = {"mistakes": [], "vocabulary": [], "completed_scenarios": []}


class FlakyProvider(LLMProvider):
    name = "flaky"
    model_name = "flaky-1"

    def __init__(self, errors, response):
        self.errors = list(errors)
        self.response = response
        self.calls = 0
        self.prompts = []

    def is_configured(self):
        return True

    def generate_json(self, system_prompt, user_prompt):
        self.calls += 1
        self.prompts.append(system_prompt)
        if self.errors:
            raise self.errors.pop(0)
        return self.response


def _svc(provider):
    svc = LLMService(provider=provider)
    svc.retry_delay = 0
    return svc


# --- normalize_correction ---------------------------------------------------

def test_none_and_empty_mean_no_correction():
    for raw in (None, "", "  ", "null", {}, {"original": "hola"}, []):
        assert normalize_correction(raw) is None


def test_full_object_kept():
    raw = {"original": "No estoy en la línea.", "corrected": "No estoy en la cola.",
           "error_category": "lexical", "cf_type": "explicit", "is_transfer": True,
           "transfer_source": "EN", "explanation": "«línea» — калька с английского line."}
    c = normalize_correction(raw)
    assert c == {**raw, "transfer_source": "en"}


def test_legacy_string_becomes_explanation():
    c = normalize_correction("Se dice «está bien», con tilde.")
    assert c["explanation"].startswith("Se dice")
    assert c["error_category"] is None and c["cf_type"] == "explicit"


def test_aliases_and_bad_enums_are_coerced():
    c = normalize_correction({"original": "possible", "corrected": "posible",
                              "category": "Spelling", "cf_type": "shout"})
    assert c["error_category"] == "spelling_accent"
    assert c["cf_type"] == "recast"
    assert normalize_correction({"corrected": "x", "error_category": "nonsense"})["error_category"] is None


def test_transfer_source_implies_transfer_and_is_dropped_without_it():
    assert normalize_correction({"corrected": "x", "transfer_source": "en"})["is_transfer"] is True
    c = normalize_correction({"corrected": "x", "is_transfer": False, "transfer_source": ""})
    assert c["is_transfer"] is False and c["transfer_source"] is None


def test_self_identical_correction_is_dropped():
    assert normalize_correction({"original": "Está bien.", "corrected": "Está bien."}) is None


def test_list_takes_first_item():
    c = normalize_correction([{"corrected": "la cola", "error_category": "lexical"}, {"corrected": "y"}])
    assert c["corrected"] == "la cola"


def test_correction_to_text():
    c = normalize_correction({"original": "esforzo practicar", "corrected": "me esfuerzo por practicar",
                              "error_category": "preposition", "explanation": "esforzarse por + inf."})
    assert correction_to_text(c) == "esforzo practicar → me esfuerzo por practicar — esforzarse por + inf. [preposition]"
    assert correction_to_text(None) == ""


def test_eval_cases_use_contract_categories():
    for name, n, case in _cases():
        assert set(case["error_categories"]) <= set(ERROR_CATEGORIES), f"{name}:{n}"


def test_contract_prompt_lists_enums_and_current_turn_rule():
    text = correction_contract(SETTINGS)
    assert all(f'"{c}"' in text for c in ERROR_CATEGORIES + CF_TYPES)
    assert 'CURRENT "message"' in text and "history" in text
    assert "porfa" in text  # register must not be over-prescriptive (feedback §5)
    assert "{" in text and "{{" not in text  # braces rendered once


# --- LLMService integration ---------------------------------------------------

def test_free_talk_and_lesson_prompts_include_contract_and_normalise():
    resp = {"reply": "¡Vale!", "roleplay_reply": "¿Algo más?", "vocab": [], "encouragement": "",
            "progress_note": "", "should_finish": False,
            "correction": {"original": "esta bien", "corrected": "está bien", "error_category": "accent"}}
    p = FlakyProvider([], resp)
    svc = _svc(p)
    r1 = svc.free_talk(settings=SETTINGS, progress=PROGRESS, history=[], message="esta bien")
    r2 = svc.lesson_turn(settings=SETTINGS, lesson={"scenario_id": "coffee_shop"}, history=[], message="esta bien")
    for r in (r1, r2):
        assert r["correction"]["error_category"] == "spelling_accent"
        assert r["source"] == "flaky" and r["model"] == "flaky-1"
    assert all("error_category" in sp for sp in p.prompts)
    assert "correction must be a plain string" not in p.prompts[1]


def test_retries_once_on_503_then_succeeds():
    p = FlakyProvider([RuntimeError("Gemini request failed: 503 UNAVAILABLE")],
                      {"reply": "hola", "correction": None})
    r = _svc(p).free_talk(settings=SETTINGS, progress=PROGRESS, history=[], message="hola")
    assert p.calls == 2 and r["source"] == "flaky" and r["correction"] is None


def test_no_retry_on_non_transient_error_falls_through_chain():
    bad = FlakyProvider([RuntimeError("invalid JSON")], {})
    good = FlakyProvider([], {"reply": "hola", "correction": None})
    good.name, good.model_name = "backup", "b-1"
    svc = _svc(bad)
    svc.providers = [bad, good]
    r = svc.free_talk(settings=SETTINGS, progress=PROGRESS, history=[], message="hola")
    assert bad.calls == 1 and r["source"] == "backup" and r["model"] == "b-1"


def test_two_503s_fall_back_to_rules():
    p = FlakyProvider([RuntimeError("429 RESOURCE_EXHAUSTED")] * 2, {"reply": "x"})
    r = _svc(p).free_talk(settings=SETTINGS, progress=PROGRESS, history=[], message="hola")
    assert p.calls == 2 and r["source"] == "fallback"


def test_api_logs_structured_correction_as_text(tmp_path, monkeypatch):
    monkeypatch.setenv("LINGMATE_DB_PATH", str(tmp_path / "t.db"))
    import importlib
    import main
    importlib.reload(main)
    from fastapi.testclient import TestClient
    main.llm = _svc(FlakyProvider([], {"reply": "Vale.", "vocab": [], "encouragement": "",
                                       "correction": {"original": "la línea", "corrected": "la cola",
                                                      "error_category": "lexical", "is_transfer": True,
                                                      "transfer_source": "en", "explanation": "калька"}}))
    client = TestClient(main.app)
    client.post("/api/setup", json={"user_id": "u", "target_language": "es"})
    body = client.post("/api/chat", json={"user_id": "u", "message": "No estoy en la línea."}).json()
    assert body["correction"]["transfer_source"] == "en"
    mistakes = client.get("/api/progress/u").json()["progress"]["mistakes"]
    assert any("la línea → la cola" in json.dumps(m, ensure_ascii=False) for m in mistakes)
