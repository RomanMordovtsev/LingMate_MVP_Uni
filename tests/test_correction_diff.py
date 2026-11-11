"""Diff view for corrections (roadmap 1.4; morphosyntax §2, §6). No network."""
import json

import pytest

from core.feedback import correction_diff
from tests.test_eval_cases import _cases
from tests.test_feedback import SETTINGS, PROGRESS, FlakyProvider, _svc


def _sides(segments):
    old = "".join(s["text"] for s in segments if s["op"] in ("equal", "del"))
    new = "".join(s["text"] for s in segments if s["op"] in ("equal", "ins"))
    return old, new


def _changed(segments, op):
    return [s["text"] for s in segments if s["op"] == op]


def test_empty_or_identical_gives_no_diff():
    assert correction_diff("", "algo") == []
    assert correction_diff("hola", "") == []
    assert correction_diff("Hola", "Hola") == []


def test_ending_change_marks_only_the_morpheme():
    d = correction_diff("Estoy cansado", "Estoy cansada")
    assert _changed(d, "del") == ["o"] and _changed(d, "ins") == ["a"]
    assert d[0] == {"op": "equal", "text": "Estoy cansad"}


def test_accent_marks_only_the_letter():
    d = correction_diff("Ayer fuí al cine", "Ayer fui al cine")
    assert _changed(d, "del") == ["í"] and _changed(d, "ins") == ["i"]


def test_different_words_are_swapped_whole():
    d = correction_diff("la problema", "el problema")
    assert _changed(d, "del") == ["la"] and _changed(d, "ins") == ["el"]
    d = correction_diff("Soy en Vitoria", "Estoy en Vitoria")
    assert _changed(d, "del") == ["Soy"] and _changed(d, "ins") == ["Estoy"]


def test_inverted_marks_and_accents_align_with_words():
    d = correction_diff("Donde esta la estacion", "¿Dónde está la estación?")
    assert _changed(d, "ins") == ["¿", "ó", "á", "ó", "?"]
    assert _changed(d, "del") == ["o", "a", "o"]


def test_insertions_and_phrase_swaps():
    d = correction_diff("me gusta mucho", "me gustan mucho los libros")
    assert _changed(d, "ins") == ["n", " los libros"] and _changed(d, "del") == []
    d = correction_diff("Perdona, ¿puedo?", "Perdone, ¿me deja pasar?")
    assert "puedo" in _changed(d, "del") and "me deja pasar" in _changed(d, "ins")


def test_adjacent_segments_are_merged():
    d = correction_diff("Quiero una Coca-Cola", "¿Me pones una Coca-Cola?")
    ops = [s["op"] for s in d]
    assert all(a != b for a, b in zip(ops, ops[1:]))


@pytest.mark.parametrize("case", [c for _, _, c in _cases()], ids=lambda c: c["id"])
def test_diff_reconstructs_both_sides_on_eval_cases(case):
    original, corrected = case["original"], case["acceptable"][0]
    d = correction_diff(original, corrected)
    if original.strip() == corrected.strip():
        assert d == []
    else:
        assert _sides(d) == (original.strip(), corrected.strip())


def test_service_attaches_diff_to_correction():
    p = FlakyProvider([], {"reply": "¡Vale!", "vocab": [], "encouragement": "",
                           "correction": {"original": "esta bien", "corrected": "está bien",
                                          "error_category": "spelling_accent"}})
    r = _svc(p).free_talk(settings=SETTINGS, progress=PROGRESS, history=[], message="esta bien")
    assert _changed(r["correction"]["diff"], "ins") == ["á"]


def test_legacy_string_correction_has_empty_diff():
    p = FlakyProvider([], {"reply": "¡Vale!", "correction": "Mejor: está bien"})
    r = _svc(p).free_talk(settings=SETTINGS, progress=PROGRESS, history=[], message="esta bien")
    assert r["correction"]["diff"] == []


def test_api_returns_diff_and_log_has_no_diff(tmp_path, monkeypatch):
    monkeypatch.setenv("LINGMATE_DB_PATH", str(tmp_path / "t.db"))
    import importlib
    import main
    importlib.reload(main)
    from fastapi.testclient import TestClient
    main.llm = _svc(FlakyProvider([], {"reply": "Vale.", "vocab": [], "encouragement": "",
                                       "correction": {"original": "la línea", "corrected": "la cola",
                                                      "error_category": "lexical"}}))
    client = TestClient(main.app)
    client.post("/api/setup", json={"user_id": "u", "target_language": "es"})
    body = client.post("/api/chat", json={"user_id": "u", "message": "Estoy en la línea."}).json()
    assert body["correction"]["diff"][0] == {"op": "equal", "text": "la "}
    mistakes = client.get("/api/progress/u").json()["progress"]["mistakes"]
    assert '"op"' not in json.dumps(mistakes)
