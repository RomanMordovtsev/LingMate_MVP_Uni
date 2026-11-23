"""Placement + diagnosis (roadmap C.2): item bank, adaptive staircase, gaps → start unit, API.
No network, no LLM."""
import os
import re
import tempfile
from pathlib import Path

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


# --- generic entry test (docs/feedback/2026-11-21) -------------------------------------

ROOT = Path(__file__).resolve().parents[1]


def _norm(text):
    return " ".join(re.sub(r"[^\w\s]", " ", text.lower()).split())


def _filled(item):
    return item.stem.replace("___", item.answer) if item.kind == "gap" else item.stem


def test_no_item_comes_from_docs_learner():
    learner = _norm((ROOT / "docs/learner/roman-spanish.md").read_text(encoding="utf-8")
                    + (ROOT / "eval/cases/es_roman.jsonl").read_text(encoding="utf-8"))
    raw = (ROOT / "curriculum/es/placement.yaml").read_text(encoding="utf-8")
    assert "from_learner" not in raw and "docs/learner" not in raw.split("items:")[1]
    for item in BANK.items:
        words = _norm(_filled(item)).split()
        shared = [" ".join(words[k:k + 4]) for k in range(len(words) - 3)
                  if " " + " ".join(words[k:k + 4]) + " " in " " + learner + " "]
        assert not shared, (item.id, shared)       # no 4-word chunk of Roman's situations
        assert "docs/learner" not in item.source and "roman" not in item.source.lower(), item.id
        # neutral contexts: nothing personal or tied to one city
        assert not re.search(r"roman|vitoria|gasteiz|pintxo|euskera|rusia", _filled(item).lower()), item.id


def test_items_cite_a_descriptor_at_their_level():
    for item in BANK.items:
        assert item.source.startswith(("PCIC ", "CEFR ")), item.id
        if item.source.startswith("PCIC"):
            assert item.source.split()[1] == item.level, item.id


def test_bank_is_balanced_and_l1_neutral():
    for lvl in TEST_LEVELS:
        items = [i for i in BANK.items if i.level == lvl]
        assert len(items) >= BLOCK + EXTRA, lvl
        assert len({i.category for i in items}) >= 3, lvl
    assert len({i.category for i in BANK.items}) >= 8
    cyrillic = re.compile("[а-яё]", re.I)
    for item in BANK.items:     # answering never needs the learner's L1
        assert not cyrillic.search(item.stem) and not any(cyrillic.search(o) for o in item.options), item.id


def test_stale_learner_flag_rejected_and_levels_provisional():
    raw = BANK.model_dump()
    raw["items"][0]["from_learner"] = True
    with pytest.raises(ValueError):
        PlacementBank.model_validate(raw)
    raw = BANK.model_dump()
    raw["items"][0]["source"] = "docs/learner/roman-spanish.md"
    with pytest.raises(ValueError):
        PlacementBank.model_validate(raw)
    assert BANK.calibration == "provisional"


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
    # A2 learner who failed the se le ha roto item → starts at unit 2, not unit 1.
    _, answers = run("A2", "A2", wrong={"a2-se-le-roto"})
    res = diagnose(BANK, answers, UNITS, "A2")
    assert res["level"] == "A2"
    assert res["start_unit"] == "es-a2-hoy-he-hecho" and res["start_reason"] == "gap"
    gap = next(g for g in res["gaps"] if g["item_id"] == "a2-se-le-roto")
    assert gap["correct"] == "ha roto" and gap["category"] == "agreement"
    assert res["provisional"] is True
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


@pytest.mark.parametrize("position", [0, 1, 2, 3])
def test_clicking_one_button_position_does_not_pass_levels(position):
    """Answer keys sat mostly at option 2 in the YAML; the shown order is shuffled per item."""
    for start in TEST_LEVELS:
        answers = []
        for _ in range(40):
            res = step(BANK, answers, start)
            if res["done"]:
                break
            opts = res["item"]["options"]
            answers.append({"item_id": res["item"]["id"], "choice": opts[min(position, len(opts) - 1)]})
        assert res["done"] and res["beginner"], (position, start, res)
    item = BANK.items[0]
    assert sorted(item.public()["options"]) == sorted(item.options)
    assert item.public()["options"] == item.public()["options"]      # stable between requests


def test_gap_in_new_a2_unit_sets_start_unit():
    """An A2 learner who gets everything right except «su» with usted starts at the trámites unit
    (the first open unit with a gap at the placed level), not at the first unit of the course."""
    known_a2 = [i for i in BANK.items if i.level in ("A1", "A2")]
    answers = [{"item_id": i.id, "choice": i.answer if i.id != "a2-su-usted"
                else next(o for o in i.options if o != i.answer)} for i in known_a2]
    answers += [{"item_id": i.id, "choice": None} for i in BANK.items if i.level == "B1"][:4]
    res = diagnose(BANK, answers, UNITS, start_level="A2")
    assert res["level"] == "A2"
    assert res["start_unit"] == "es-a2-tramites" and res["start_reason"] == "gap"
