"""Learner profile + onboarding API (roadmap 1.2). No network: rule-based / fake providers only."""
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from core.profile import LearnerProfile, profile_context, profile_from_settings

ROMAN = {
    "user_id": "roman",
    "target_language": "es",
    "target_variant": "es-ES",
    "level": "A2",
    "languages": [{"code": "ru", "level": "L1"}, {"code": "en", "level": "C1"},
                  {"code": "it", "level": "A1"}],
    "goal": "relocated",
    "country": "España",
    "city": "Vitoria-Gasteiz",
    "interests": ["música", " viajes ", "Música", ""],
    "daily_goal_minutes": 10,
    "feedback_timing": "immediate",
    "ideal_self": "Quiero hablar con mis vecinos sin miedo.",
}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LINGMATE_DB_PATH", str(tmp_path / "t.sqlite3"))
    import main
    from core.storage import SqliteStore
    monkeypatch.setattr(main, "store", SqliteStore(tmp_path / "t.sqlite3"))
    return TestClient(main.app)


def test_profile_model_normalises_and_keeps_legacy_keys():
    p = LearnerProfile(**ROMAN)
    assert p.interests == ["música", "viajes"]
    assert p.native_language == "ru"
    s = p.to_settings()
    assert s["native_language"] == "ru" and s["level"] == "A2" and s["target_language"] == "es"
    assert s["onboarding_completed"] is True


def test_target_language_is_removed_from_repertoire():
    data = {**ROMAN, "languages": ROMAN["languages"] + [{"code": "ES", "level": "A2"}]}
    assert [l.code for l in LearnerProfile(**data).languages] == ["ru", "en", "it"]


@pytest.mark.parametrize("patch", [
    {"languages": [{"code": "en", "level": "C1"}]},          # no L1
    {"languages": [{"code": "es", "level": "L1"}]},          # L1 == target
    {"goal": "fun"},
    {"daily_goal_minutes": 1},
    {"level": "A3"},
    {"ideal_self": "x" * 301},
])
def test_invalid_profiles_rejected(patch):
    with pytest.raises(ValidationError):
        LearnerProfile(**{**ROMAN, **patch})


def test_profile_from_legacy_settings():
    p = profile_from_settings({"user_id": "u", "target_language": "en", "native_language": "ru",
                               "level": "B1", "interests": ["music"]})
    assert p["languages"] == [{"code": "ru", "level": "L1"}]
    assert p["goal"] is None and p["onboarding_completed"] is False
    assert profile_from_settings(None) is None


def test_profile_context_mentions_repertoire_goal_place():
    ctx = profile_context(LearnerProfile(**ROMAN).to_settings())
    assert "English (C1)" in ctx and "Italian (A1)" in ctx and "Russian" not in ctx
    assert "Vitoria-Gasteiz, España" in ctx
    assert "lives in the country" in ctx
    assert "sin miedo" in ctx
    # Legacy users: prompt unchanged.
    assert profile_context({"target_language": "es", "native_language": "ru", "level": "A1"}) == ""


def test_profile_context_reaches_the_llm_prompt():
    from core.llm_service import LLMService
    from tests.test_llm_providers import FakeProvider, PROGRESS
    fake = FakeProvider()
    LLMService(provider=fake).free_talk(settings=LearnerProfile(**ROMAN).to_settings(),
                                        progress=PROGRESS, history=[], message="hola")
    assert "Vitoria-Gasteiz" in fake.calls[0][0]


def test_onboarding_api_roundtrip(client):
    r = client.get("/api/profile/roman").json()
    assert r == {"profile": None, "onboarding_completed": False}

    r = client.post("/api/profile", json=ROMAN)
    assert r.status_code == 200
    prof = r.json()["profile"]
    assert prof["goal"] == "relocated" and prof["onboarding_completed"] is True

    got = client.get("/api/profile/roman").json()
    assert got["onboarding_completed"] is True and got["profile"]["city"] == "Vitoria-Gasteiz"

    # Chat still works with the richer settings (rule-based fallback, no keys).
    assert client.post("/api/chat", json={"user_id": "roman", "message": "No estoy en la línea."}).status_code == 200


def test_quick_setup_form_does_not_wipe_profile(client):
    client.post("/api/profile", json=ROMAN)
    r = client.post("/api/setup", json={"user_id": "roman", "target_language": "es",
                                        "native_language": "ru", "level": "B1", "interests": ["cine"]})
    s = r.json()["settings"]
    assert s["level"] == "B1" and s["interests"] == ["cine"]
    assert s["goal"] == "relocated" and s["city"] == "Vitoria-Gasteiz" and s["onboarding_completed"]
    assert {"code": "en", "level": "C1"} in s["languages"]


def test_invalid_profile_returns_422(client):
    assert client.post("/api/profile", json={**ROMAN, "goal": "fun"}).status_code == 422
