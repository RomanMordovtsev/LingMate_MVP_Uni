"""Transfer maps (roadmap 1.5; morphosyntax §7, sla §4, multilingual-education §1). No network."""
import re

import pytest

from core.feedback import ERROR_CATEGORIES
from core.pedagogy.l1_maps import _PAIRS, fold, get_map, match_rule, prompt_hints, repertoire, transfer_note
from tests.test_eval_cases import _cases
from tests.test_feedback import PROGRESS, FlakyProvider, _svc

ROMAN = {"target_language": "es", "native_language": "ru", "level": "A2", "onboarding_completed": True,
         "languages": [{"code": "en", "level": "C1"}, {"code": "ru", "level": "L1"}, {"code": "it", "level": "A1"}]}
RU_ONLY = {"target_language": "es", "native_language": "ru", "level": "A2"}


def _corr(original, corrected, category, source=None):
    return {"original": original, "corrected": corrected, "error_category": category,
            "is_transfer": source is not None, "transfer_source": source}


def _ids(note):
    return (note["contrast"] or {}).get("rule_id"), (note["bridge"] or {}).get("rule_id")


def test_all_rules_are_well_formed():
    all_rules = [r for rules in _PAIRS.values() for r in rules]
    assert len({r.id for r in all_rules}) == len(all_rules)
    for r in all_rules:
        assert r.category in ERROR_CATEGORIES and r.kind in ("negative", "bridge")
        assert r.note.get("ru") and r.source_example and r.target_example and r.title
        for m in r.original_markers + r.corrected_markers:
            re.compile(m)
            assert fold(m) == m, f"{r.id}: markers run on folded text, write them without accents"


def test_ru_es_covers_the_morphosyntax_7_list():
    cats = {r.category for r in get_map("ru", "es") if r.kind == "negative"}
    assert {"article", "ser_estar", "gender", "tense_aspect", "mood", "clitic"} <= cats
    assert get_map("ru", "es-ES") == get_map("ru", "es")
    assert get_map("xx", "es") == ()


def test_repertoire_puts_l1_first_and_drops_target():
    assert repertoire(ROMAN) == ["ru", "en", "it"]
    assert repertoire(RU_ONLY) == ["ru"]
    assert repertoire({"target_language": "es", "languages": [{"code": "es", "level": "L1"}]}) == []


@pytest.mark.parametrize("original,corrected,category,source,expected", [
    ("Esta noche ceno con pasta.", "Esta noche ceno pasta.", "preposition", "ru", "ru_es.meal_verbs"),
    ("No estoy en la línea.", "No estoy en la cola.", "lexical", "en", "en_es.linea_cola"),
    ("No estoy en la linea.", "No estoy en la cola.", "lexical", None, "en_es.linea_cola"),  # word marker, unflagged
    ("me esfuerzo practicar lo más possible", "me esfuerzo por practicar lo más posible", "preposition", "en",
     "en_es.esforzarse"),
    ("Tengo una idea possible", "Tengo una idea posible", "spelling_accent", "en", "en_es.double_consonant"),
    ("Pienso de mudarme", "Pienso en mudarme", "preposition", "en", "en_es.think_of"),
    ("Pienso de ti", "Pienso en ti", "preposition", None, "ru_es.pensar_en"),
    ("la problema", "el problema", "gender", None, "ru_es.gender_ma"),
    ("El calefacción no funciona.", "La calefacción no funciona.", "gender", None, "ru_es.gender_mismatch"),
    ("Me gusta café", "Me gusta el café", "article", None, "ru_es.article"),
    ("Soy cansado", "Estoy cansado", "ser_estar", "en", "en_es.to_be"),
    ("Soy cansado", "Estoy cansado", "ser_estar", None, "ru_es.ser_estar"),
])
def test_contrast_rule_matching(original, corrected, category, source, expected):
    assert match_rule(_corr(original, corrected, category, source), ROMAN).id == expected


def test_category_rule_from_a_non_l1_language_needs_the_flag():
    # An unflagged lexical error must not be blamed on English by guess.
    c = _corr("Perdona, ¿puedo?", "Perdone, ¿me deja pasar?", "lexical")
    assert match_rule(c, ROMAN) is None
    assert match_rule(_corr("aplicar para la beca", "solicitar la beca", "lexical", "en"), ROMAN).id == "en_es.calque"
    # A different flagged source blocks the L1 category rule.
    assert match_rule(_corr("Me gusta café", "Me gusta el café", "article", "it"), ROMAN) is None


def test_bridges_come_from_known_languages_only():
    note = transfer_note(_corr("Soy cansado", "Estoy cansado", "ser_estar"), ROMAN)
    assert _ids(note) == ("ru_es.ser_estar", "it_es.stare")
    assert transfer_note(_corr("Soy cansado", "Estoy cansado", "ser_estar"), RU_ONLY)["bridge"] is None
    # Register: Russian ты/вы is positive transfer (bus 31.10), no negative guess.
    bus = transfer_note(_corr("Perdona, ¿puedo?", "Perdone, ¿me deja pasar?", "register"), ROMAN)
    assert _ids(bus) == (None, "ru_es.tu_usted")


def test_note_uses_learner_l1_and_shape():
    note = transfer_note(_corr("la problema", "el problema", "gender"), ROMAN)["contrast"]
    assert set(note) == {"rule_id", "source", "kind", "title", "source_example", "target_example", "note"}
    assert "мужского" in note["note"] and note["source"] == "ru"
    en_learner = {"target_language": "es", "languages": [{"code": "en", "level": "L1"}]}
    c = transfer_note(_corr("No estoy en la línea", "No estoy en la cola", "lexical", "en"), en_learner)
    assert c["contrast"]["note"].startswith("'línea'")


def test_no_note_without_rule_or_settings():
    assert transfer_note(None, ROMAN) is None
    assert transfer_note(_corr("a", "b", "agreement"), ROMAN) is None
    assert transfer_note(_corr("la problema", "el problema", "gender"), None) is None


def test_every_real_roman_error_gets_a_note():
    for name, _, case in _cases():
        if name != "es_roman.jsonl":
            continue
        c = _corr(case["original"], case["acceptable"][0], case["error_categories"][0], case["transfer_source"])
        assert transfer_note(c, ROMAN), case["id"]


def test_prompt_hints_only_with_profile_and_include_each_language():
    assert prompt_hints(RU_ONLY) == ""
    hints = prompt_hints(ROMAN)
    assert "[ru]" in hints and "[en]" in hints and "[it]" in hints
    assert len(hints.splitlines()) <= 8  # short prompts (quota strategy)


def test_service_attaches_note_and_prompt_hints():
    resp = {"reply": "Vale", "vocab": [], "encouragement": "", "progress_note": "",
            "correction": {"original": "No estoy en la línea", "corrected": "No estoy en la cola",
                           "error_category": "lexical", "is_transfer": True, "transfer_source": "en"}}
    p = FlakyProvider([], resp)
    r = _svc(p).free_talk(settings=ROMAN, progress=PROGRESS, history=[], message="No estoy en la línea")
    assert r["correction"]["transfer_note"]["contrast"]["rule_id"] == "en_es.linea_cola"
    assert r["correction"]["is_transfer"] is True  # the model's flag is not altered
    assert "Likely transfer for this learner" in p.prompts[0]
    # Legacy settings: prompt unchanged, note still computed from native_language.
    p2 = FlakyProvider([], resp)
    _svc(p2).free_talk(settings=RU_ONLY, progress=PROGRESS, history=[], message="x")
    assert "Likely transfer" not in p2.prompts[0]
