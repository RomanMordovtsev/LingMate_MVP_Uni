"""Placement + diagnosis (roadmap C.2): item bank, adaptive staircase, gaps → start unit, API.
No network, no LLM."""
import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from core.curriculum import load_units
from core.placement import BLOCK, EXTRA, TEST_LEVELS, PlacementBank, diagnose, load_bank, score, step

BANK = load_bank("es")
UNITS = load_units("es")
ITEMS = BANK.by_id()


def run(true_level, start=None, wrong=(), right=()):
    """Simulated learner: right up to `true_level`, wrong above; `wrong`/`right` override items."""
    answers = []
    for _ in range(40):
        res = step(BANK, answers, start)
        if res["done"]:
            return res, answers
        item = ITEMS[res["item"]["id"]]
        ok = TEST_LEVELS.index(item.level) <= TEST_LEVELS.index(true_level) if true_level else False
        ok = (ok or item.id in right) and item.id not in wrong
        choice = item.answer if ok else next(o for o in item.options if o != item.answer)
        answers.append({"item_id": item.id, "choice": choice})
    raise AssertionError("placement did not settle")


def test_bank_valid_and_linked_to_units():
    grammar_ids = {g.id for u in UNITS for g in u.grammar}
    for item in BANK.items:
        assert item.grammar is None or item.grammar in grammar_ids, item.id
    linked = {i.grammar for i in BANK.items if i.grammar}
    assert linked == grammar_ids          # every unit grammar point is diagnosable
    assert {p.level for p in BANK.production} == set(TEST_LEVELS)
    assert sum(i.from_learner for i in BANK.items) >= 8   # Roman's real situations


def test_public_item_hides_answer():
    pub = BANK.items[0].public()
    assert "answer" not in pub and "category" not in pub


def test_invalid_items_rejected():
    raw = BANK.model_dump()
    raw["items"][0]["answer"] = "not an option"
    with pytest.raises(ValueError):
        PlacementBank.model_validate(raw)
    raw = BANK.model_dump()
    raw["items"] = [i for i in raw["items"] if i["level"] != "B2"][:]
    with pytest.raises(ValueError):
        PlacementBank.model_validate(raw)


@pytest.mark.parametrize("true_level", ["A1", "A2", "B1", "B2"])
@pytest.mark.parametrize("start", ["A1", "A2", "B1", "B2", None])
def test_staircase_finds_level_from_any_start(true_level, start):
    res, answers = run(true_level, start)
    assert res["level"] == true_level and not res["beginner"]
    assert len(answers) <= 3 * (BLOCK + EXTRA)


def test_total_beginner():
    res, _ = run(None, "A2")
    assert res == {**res, "done": True, "level": "A1", "beginner": True}


def test_borderline_block_gets_extra_items():
    a2 = [i for i in BANK.items if i.level == "A2"]
    answers = [{"item_id": i.id, "choice": i.answer if n < 2 else "x"} for n, i in enumerate(a2[:BLOCK])]
    res = step(BANK, answers, "A2")
    assert not res["done"] and res["item"]["level"] == "A2"


def test_score_drops_unknown_and_repeats():
    first = BANK.items[0]
    graded = score(BANK, [{"item_id": "zz"}, {"item_id": first.id, "choice": first.answer},
                          {"item_id": first.id, "choice": "x"}])
    assert graded == [{"item_id": first.id, "level": first.level, "choice": first.answer, "correct": True}]


def test_unit_start_is_first_open_unit_with_gap():
    # A2 learner who failed the se me han olvidado item → starts at unit 2, not unit 1.
    _, answers = run("A2", "A2", wrong={"a2-se-me-llaves"})
    res = diagnose(BANK, answers, UNITS, "A2")
    assert res["level"] == "A2"
    assert res["start_unit"] == "es-a2-hoy-he-hecho" and res["start_reason"] == "gap"
    gap = next(g for g in res["gaps"] if g["item_id"] == "a2-se-me-llaves")
    assert gap["correct"] == "han olvidado" and gap["category"] == "agreement"
    assert "es-a2-hoy-he-hecho" not in res["suggested_known"]
    assert {p["level"] for p in res["production_prompts"]} == {"A2", "B1"}


def test_a1_learner_starts_at_first_unit():
    _, answers = run("A1", "A2")
    res = diagnose(BANK, answers, UNITS, "A2")
    assert res["level"] == "A1" and res["suggested_known"] == []
    assert res["start_unit"] == UNITS[0].id


def test_b2_learner_lower_units_suggested_known():
    _, answers = run("B2", "B1")
    res = diagnose(BANK, answers, UNITS, "B1")
    assert res["level"] == "B2" and res["gaps"] == []
    assert {u.id for u in UNITS if u.level == "A2"} <= set(res["suggested_known"])


def test_diagnose_requires_finished_test():
    with pytest.raises(ValueError):
        diagnose(BANK, [], UNITS, "A2")


@pytest.fixture()
def client(monkeypatch):
    tmp = tempfile.mkdtemp()
    monkeypatch.setenv("LINGMATE_DB_PATH", os.path.join(tmp, "t.db"))
    import importlib
    import main
    importlib.reload(main)
    return TestClient(main.app)


def test_api_flow_stores_result_and_keeps_profile_level(client):
    client.post("/api/setup", json={"user_id": "u1", "target_language": "es", "level": "B1"})
    answers = []
    for _ in range(40):
        r = client.post("/api/placement/es/next", json={"user_id": "u1", "answers": answers}).json()
        if r["done"]:
            break
        item = ITEMS[r["item"]["id"]]
        assert "answer" not in r["item"]
        ok = item.level in ("A1", "A2")
        answers.append({"item_id": item.id, "choice": item.answer if ok else item.options[-1]
                        if item.options[-1] != item.answer else item.options[0]})
    assert r["done"] and r["level"] == "A2" and r["production_prompts"]
    prod = [{"prompt_id": r["production_prompts"][0]["id"], "text": "Hoy he ido a clase."}]
    fin = client.post("/api/placement/es/finish",
                      json={"user_id": "u1", "answers": answers, "production": prod}).json()
    assert fin["level"] == "A2" and fin["start_unit"] and not fin["applied_level"]
    stored = client.get("/api/placement/u1").json()["placement"]
    assert stored["profile_level_before"] == "B1" and stored["production"][0]["text"] == "Hoy he ido a clase."
    assert client.get("/api/profile/u1").json()["profile"]["level"] == "B1"   # not assumed
    client.post("/api/placement/es/finish", json={"user_id": "u1", "answers": answers, "apply_level": True})
    assert client.get("/api/profile/u1").json()["profile"]["level"] == "A2"


def test_api_errors(client):
    assert client.post("/api/placement/xx/next", json={"user_id": "u"}).status_code == 404
    assert client.post("/api/placement/es/finish", json={"user_id": "u", "answers": []}).status_code == 400
    assert client.get("/api/placement/nobody").json() == {"placement": None}
