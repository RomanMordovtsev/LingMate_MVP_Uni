"""Controlled practice (roadmap C.3 slice 1): exercise bank, checker, graded hints, API. No network."""
import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from core.curriculum import curriculum, get_unit
from core.practice import (MAX_ATTEMPTS, Exercise, PracticeError, PracticeSet, check, cue, normalize,
                           practice_for, summarize, validate_set)

UNIT_IDS = ["es-a2-en-el-bar", "es-a2-hoy-he-hecho", "es-a2-ayer-en-el-taller"]


def ex(**kw):
    base = dict(id="t-1", kind="gap", grammar="perfecto_hoy", instruction_ru="Заполни пропуск.",
                prompt="Hoy ___ a clase.", answers=["he ido"], hint_ru="Сегодня → perfecto.",
                explain_ru="hoy → he + participio.")
    base.update(kw)
    return Exercise(**base)


@pytest.mark.parametrize("unit_id", UNIT_IDS)
def test_sets_load_and_cover_every_grammar_point(unit_id):
    ps = practice_for("es", unit_id)
    unit = get_unit("es", unit_id)
    assert ps is not None and len(ps.exercises) >= 5
    assert {e.grammar for e in ps.exercises} == {g.id for g in unit.grammar}
    assert len({e.kind for e in ps.exercises}) >= 3          # varied practice, not one drill type


@pytest.mark.parametrize("unit_id", UNIT_IDS)
def test_every_answer_is_accepted_and_public_view_hides_the_key(unit_id):
    for e in practice_for("es", unit_id).exercises:
        pub = e.public()
        assert "answers" not in pub and "hint_ru" not in pub and "explain_ru" not in pub
        for a in e.answers:
            assert check(e, a, 1)["result"] == "correct", (e.id, a)
        if e.kind == "order":
            assert normalize(" ".join(pub["tokens"])) != normalize(e.answers[0])
            assert sorted(normalize(" ".join(pub["tokens"])).split()) == sorted(normalize(e.answers[0]).split())
            assert all(not t[-1] in ".,?!" for t in pub["tokens"])   # punctuation would leak the order


def test_units_without_practice_return_none_and_map_lists_practice():
    with_practice = [u.id for u in curriculum("es") if practice_for("es", u.id)]
    assert with_practice == UNIT_IDS


def test_normalize_ignores_case_punctuation_and_spaces():
    assert normalize("  ¿Me PONES   un cortado? ") == normalize("me pones un cortado")
    assert normalize("está") != normalize("esta")


def test_graded_hints_then_reveal():
    e = ex()
    r1 = check(e, "fui", 1)
    assert r1["result"] == "wrong" and not r1["done"] and r1["hint_ru"] and "cue" not in r1 and "answer" not in r1
    r2 = check(e, "fui", 2)
    assert r2["cue"] == "h_ i__" and "answer" not in r2
    r3 = check(e, "fui", 3)
    assert r3["result"] == "revealed" and r3["done"] and r3["answer"] == "he ido" and r3["explain_ru"]
    assert r3["full_answer"] == "Hoy he ido a clase."
    assert any(s["op"] == "ins" for s in r3["diff"])


def test_accent_only_mistake_is_accepted_with_a_note():
    e = ex(prompt="Ayer les ___ una mochila.", answers=["dejé"], grammar="indefinido_ayer")
    r = check(e, "deje", 1)
    assert r["result"] == "accent" and r["done"] and r["note_ru"] and r["answer"] == "dejé"
    assert r["diff"]


def test_choose_reveals_after_two_attempts_and_order_accepts_token_list():
    c = ex(kind="choose", prompt="Se me ___ olvidado las llaves.", options=["ha", "han"], answers=["han"],
           grammar="se_me_accidental")
    assert MAX_ATTEMPTS["choose"] == 2
    assert check(c, "ha", 1)["result"] == "wrong"
    assert check(c, "ha", 2)["result"] == "revealed"
    o = ex(kind="order", prompt="Сегодня у меня был длинный день.", answers=["Hoy he tenido un día largo."])
    assert check(o, ["hoy", "he", "tenido", "un", "día", "largo"], 1)["result"] == "correct"
    assert check(o, ["he", "hoy", "tenido", "un", "día", "largo"], 2)["cue"] == "Hoy he …"


def test_empty_answer_is_wrong_not_correct():
    assert check(ex(), "", 1)["result"] == "wrong"
    assert check(ex(), None, 3)["diff"] == []


@pytest.mark.parametrize("bad", [
    dict(prompt="Hoy a clase."),                                     # gap without ___
    dict(kind="choose", prompt="Hoy ___ a clase.", options=["fui"]),  # one option, answer missing
    dict(options=["he ido", "fui"]),                                  # options on a gap
    dict(hint_ru="Ответ: he ido, конечно."),                          # hint gives the answer away
    dict(kind="order", prompt="Сегодня", answers=["Hoy fui"]),         # too short to order
    dict(extra_field=1),
])
def test_invalid_exercises_are_rejected(bad):
    with pytest.raises(ValueError):
        ex(**bad)


def test_set_must_use_known_grammar_and_cover_all_points():
    unit = get_unit("es", "es-a2-hoy-he-hecho")
    only_one = PracticeSet(unit=unit.id, exercises=[ex(id=f"t-{i}") for i in range(3)])
    with pytest.raises(PracticeError):
        validate_set(only_one, unit)                                   # se_me_accidental not practised
    unknown = PracticeSet(unit=unit.id, exercises=[ex(id="a"), ex(id="b", grammar="se_me_accidental"),
                                                   ex(id="c", grammar="ser_estar")])
    with pytest.raises(PracticeError):
        validate_set(unknown, unit)


def test_cue_masks_all_but_first_letters():
    assert cue("se me ha olvidado") == "s_ m_ h_ o_______"
    assert cue("y a") == "y a"


def test_summary_counts_and_never_marks_unit_done():
    unit = get_unit("es", "es-a2-hoy-he-hecho")
    ps = practice_for("es", unit.id)
    ids = [e.id for e in ps.exercises]
    results = [{"exercise_id": ids[0], "result": "correct", "attempts": 1},
               {"exercise_id": ids[1], "result": "accent", "attempts": 1},
               {"exercise_id": ids[3], "result": "correct", "attempts": 2},
               {"exercise_id": ids[4], "result": "revealed", "attempts": 2},
               {"exercise_id": "nope", "result": "correct", "attempts": 1}]
    s = summarize(ps, results, unit)
    assert (s["answered"], s["first_try"], s["with_help"], s["revealed"]) == (4, 2, 1, 1)
    assert [w["grammar"] for w in s["weak"]] == ["se_me_accidental"]
    assert s["status"] == "practised" and s["total"] == len(ids)


@pytest.fixture()
def client(monkeypatch):
    tmp = tempfile.mkdtemp()
    monkeypatch.setenv("LINGMATE_DB_PATH", os.path.join(tmp, "t.db"))
    import importlib
    import main
    importlib.reload(main)
    return TestClient(main.app)


def test_api_flow(client):
    base = "/api/curriculum/es/units/es-a2-hoy-he-hecho/practice"
    data = client.get(base).json()
    assert data["exercises"] and all("answers" not in e for e in data["exercises"])
    assert {g["id"] for g in data["grammar"]} == {"perfecto_hoy", "se_me_accidental"}
    first = data["exercises"][0]
    r = client.post(base + "/check", json={"exercise_id": first["id"], "response": "xx", "attempt": 1}).json()
    assert r["result"] == "wrong" and "answer" not in r
    assert client.post(base + "/check", json={"exercise_id": "nope", "response": "x"}).status_code == 404
    s = client.post(base + "/finish", json={"user_id": "u1", "results": [
        {"exercise_id": first["id"], "result": "revealed", "attempts": 3}]}).json()
    assert s["revealed"] == 1
    stored = client.get("/api/practice/u1").json()["practice"]["es-a2-hoy-he-hecho"]
    assert stored["revealed"] == 1 and stored["status"] == "practised" and stored["weak"] == ["perfecto_hoy"]
    assert client.get("/api/curriculum/es/units/es-a2-tramites/practice").status_code == 404
    assert client.get("/api/curriculum/es").json()["practice"] == UNIT_IDS


def test_finish_keeps_other_settings(client):
    client.post("/api/setup", json={"user_id": "u2", "target_language": "es", "level": "A2"})
    client.post("/api/curriculum/es/units/es-a2-en-el-bar/practice/finish", json={"user_id": "u2", "results": []})
    from main import store
    st = store.get_settings("u2")
    assert st["level"] == "A2" and "es-a2-en-el-bar" in st["practice"]
