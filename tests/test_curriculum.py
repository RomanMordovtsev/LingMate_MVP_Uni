"""Curriculum map (roadmap C.1): unit schema, cross-unit checks, links to scenarios / learner
situations / error categories, next-unit logic and API. No network."""
import re
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from core.curriculum import (CURRICULUM_DIR, CurriculumError, Unit, load_units, next_units,
                             units_for_category, validate_units)
from core.feedback import ERROR_CATEGORIES
from core.scenarios import SCENARIOS

ROOT = Path(__file__).resolve().parent.parent
UNITS = load_units("es")


def _raw(**over):
    data = yaml.safe_load((CURRICULUM_DIR / "es/units/01-a2-en-el-bar.yaml").read_text(encoding="utf-8"))
    data.update(over)
    return data


def test_es_units_load_in_order():
    assert len(UNITS) >= 5
    assert [u.order for u in UNITS] == sorted(u.order for u in UNITS)
    assert UNITS[0].id == "es-a2-en-el-bar"
    assert {u.level for u in UNITS} <= {"A2", "B1"}  # Roman's path first (C.1: start with A2 → B1)


def test_every_unit_is_a_full_task_unit():
    for u in UNITS:
        assert 1 <= len(u.can_do) <= 3, u.id                 # syllabus-design §8
        assert 3 <= len(u.chunks) <= 8, u.id                 # §3: key chunks
        assert all(g.tip_ru for g in u.grammar), u.id        # §3: one form tip
        assert u.situations.scenarios or u.situations.learner or u.situations.seeds, u.id
        assert u.culture_ru, u.id                            # multilingual-education §2
        assert set(u.error_categories) <= set(ERROR_CATEGORIES)


def test_linked_scenarios_exist_and_match_language():
    for u in UNITS:
        for sid in u.situations.scenarios:
            assert sid in SCENARIOS, (u.id, sid)
            assert SCENARIOS[sid]["target_language"] == u.language


def test_learner_situations_point_to_real_entries():
    headings = [line[4:] for line in (ROOT / "docs/learner/roman-spanish.md").read_text(encoding="utf-8").splitlines()
                if line.startswith("### ")]
    for u in UNITS:
        for ref in u.situations.learner:
            assert any(h.startswith(ref) for h in headings), (u.id, ref)


def test_pcic_numbers_only_when_verified():
    with pytest.raises(ValueError):
        Unit.model_validate(_raw(pcic=[{"inventory": "gramatica", "band": "A1-A2", "title": "Presente", "section": "9.1"}]))
    for u in UNITS:
        for ref in u.pcic:
            assert ref.section is None or ref.verified
            if ref.section:
                assert re.fullmatch(r"\d+(\.\d+)*", ref.section)


def test_sources_doc_lists_every_verified_section():
    sources = (CURRICULUM_DIR / "es/SOURCES.md").read_text(encoding="utf-8")
    for u in UNITS:
        for ref in u.pcic:
            if ref.verified:
                assert f"{ref.section} *" in sources, (u.id, ref.section)


@pytest.mark.parametrize("over", [
    {"id": "Bar"},                                   # bad id shape
    {"id": "es-b1-en-el-bar"},                       # id says B1, level says A2
    {"level": "Z9"},
    {"can_do": []},
    {"chunks": [{"es": "Hola", "ru": "Привет"}]},    # < 3 chunks
    {"grammar": [{"id": "x", "label_ru": "abc", "tip_ru": "достаточно длинный совет", "examples": ["a"],
                  "error_categories": ["spelling"]}]},  # unknown category
])
def test_schema_rejects_bad_units(over):
    with pytest.raises(ValueError):
        Unit.model_validate(_raw(**over))


def test_cross_unit_checks():
    a = Unit.model_validate(_raw())
    b = Unit.model_validate(_raw(id="es-a2-otra", order=2, prerequisites=["es-a2-en-el-bar"]))
    assert [u.id for u in validate_units([b, a])] == ["es-a2-en-el-bar", "es-a2-otra"]
    with pytest.raises(CurriculumError):
        validate_units([a, Unit.model_validate(_raw(order=2))])                         # duplicate id
    with pytest.raises(CurriculumError):
        validate_units([a, Unit.model_validate(_raw(id="es-a2-otra", order=1))])        # duplicate order
    with pytest.raises(CurriculumError):
        validate_units([a, Unit.model_validate(_raw(id="es-a2-otra", order=2, prerequisites=["es-a2-nada"]))])
    with pytest.raises(CurriculumError):  # prerequisite later in the course (also rules out cycles)
        validate_units([Unit.model_validate(_raw(prerequisites=["es-a2-otra"])),
                        Unit.model_validate(_raw(id="es-a2-otra", order=2))])
    with pytest.raises(CurriculumError):  # B1 unit cannot be a prerequisite of an A2 one
        validate_units([Unit.model_validate(_raw(id="es-b1-x", level="B1")),
                        Unit.model_validate(_raw(id="es-a2-otra", order=2, prerequisites=["es-b1-x"]))])


def test_load_units_from_other_folder(tmp_path):
    folder = tmp_path / "it" / "units"
    folder.mkdir(parents=True)
    (folder / "u.yaml").write_text(yaml.safe_dump(_raw(id="it-a2-al-bar", language="it", variant="it-IT")),
                                   encoding="utf-8")
    assert [u.id for u in load_units("it", root=tmp_path)] == ["it-a2-al-bar"]
    assert load_units("fr", root=tmp_path) == []
    (folder / "bad.yaml").write_text(yaml.safe_dump(_raw()), encoding="utf-8")  # language es in folder it
    with pytest.raises(CurriculumError):
        load_units("it", root=tmp_path)


def test_next_units_follow_prerequisites_and_level():
    first = [u.id for u in next_units(UNITS, [])]
    assert "es-a2-en-el-bar" in first and "es-a2-ayer-en-el-taller" not in first
    after = [u.id for u in next_units(UNITS, ["es-a2-hoy-he-hecho"])]
    assert "es-a2-ayer-en-el-taller" in after and "es-a2-hoy-he-hecho" not in after
    # an A1 learner is not offered B1 units yet (morphosyntax §10: up to the next stage)
    assert all(u.level != "B1" for u in next_units(UNITS, ["es-a2-en-el-bar"], level="A1"))
    assert any(u.level == "B1" for u in next_units(UNITS, ["es-a2-en-el-bar"], level="A2"))


def test_units_for_error_category():
    assert "es-b1-buenos-deseos" in [u.id for u in units_for_category(UNITS, "mood")]


@pytest.fixture
def client():
    import main
    return TestClient(main.app)


def test_api_curriculum(client):
    r = client.get("/api/curriculum/es")
    assert r.status_code == 200
    body = r.json()
    assert body["units"][0]["id"] == "es-a2-en-el-bar"
    assert {"title_ru", "can_do", "grammar", "error_categories", "prerequisites"} <= set(body["units"][0])
    assert "es-a2-ayer-en-el-taller" not in body["next"]
    r = client.get("/api/curriculum/es", params={"done": "es-a2-hoy-he-hecho", "level": "A2"})
    assert "es-a2-ayer-en-el-taller" in r.json()["next"]
    assert client.get("/api/curriculum/xx").json()["units"] == []


def test_api_unit(client):
    r = client.get("/api/curriculum/es/units/es-a2-en-casa")
    assert r.status_code == 200
    assert r.json()["chunks"][0]["es"]
    assert client.get("/api/curriculum/es/units/es-a2-nada").status_code == 404
