"""
Unit-тесты для LLM-провайдеров и LLMService.

Запуск из корня репозитория:
    python -m pytest tests/test_llm_providers.py -v

Тесты используют моки — реальная сеть и Gemini/Ollama не нужны.
"""

import json
import os
from unittest.mock import patch, MagicMock

import pytest

from core.llm.base import LLMProvider
from core.llm.factory import make_provider
from core.llm.gemini_provider import GeminiProvider
from core.llm.ollama_provider import OllamaProvider
from core.llm_service import LLMService


# ---------------------------------------------------------------------------
# Фейковый провайдер для проверки LLMService в изоляции
# ---------------------------------------------------------------------------

class FakeProvider(LLMProvider):
    name = "fake"

    def __init__(self, configured=True, response=None, raises=None):
        self._configured = configured
        self._response = response or {"reply": "ok", "correction": None, "vocab": [], "encouragement": ""}
        self._raises = raises
        self.calls = []

    def is_configured(self) -> bool:
        return self._configured

    def generate_json(self, system_prompt, user_prompt):
        self.calls.append((system_prompt, user_prompt))
        if self._raises:
            raise self._raises
        return self._response


# ---------------------------------------------------------------------------
# LLMService: free_talk
# ---------------------------------------------------------------------------

SETTINGS = {"target_language": "es", "native_language": "ru", "level": "A1"}
PROGRESS = {"mistakes": [], "vocabulary": [], "completed_scenarios": []}


def test_free_talk_uses_provider_when_configured():
    fake = FakeProvider(response={
        "reply": "¡Hola!", "correction": None, "vocab": ["hola"], "encouragement": "good"
    })
    svc = LLMService(provider=fake)

    result = svc.free_talk(settings=SETTINGS, progress=PROGRESS, history=[], message="hi")

    assert result["reply"] == "¡Hola!"
    assert result["source"] == "fake"
    assert len(fake.calls) == 1


def test_free_talk_falls_back_when_provider_unconfigured():
    fake = FakeProvider(configured=False)
    svc = LLMService(provider=fake)

    result = svc.free_talk(settings=SETTINGS, progress=PROGRESS, history=[], message="hi")

    assert result["source"] == "fallback"
    assert "reply" in result
    assert len(fake.calls) == 0  # не звали провайдера


def test_free_talk_falls_back_on_provider_error():
    fake = FakeProvider(raises=RuntimeError("boom"))
    svc = LLMService(provider=fake)

    result = svc.free_talk(settings=SETTINGS, progress=PROGRESS, history=[], message="hi")

    assert result["source"] == "fallback"
    assert "reply" in result


def test_free_talk_falls_back_on_invalid_response():
    # Провайдер вернул что-то, в чём нет ключа "reply".
    fake = FakeProvider(response={"unexpected": True})
    svc = LLMService(provider=fake)

    result = svc.free_talk(settings=SETTINGS, progress=PROGRESS, history=[], message="hi")

    assert result["source"] == "fallback"


# ---------------------------------------------------------------------------
# LLMService: lesson_turn
# ---------------------------------------------------------------------------

LESSON = {"scenario_id": "coffee_shop", "title": "Coffee shop", "goal": "Order"}


def test_lesson_turn_uses_provider():
    fake = FakeProvider(response={
        "roleplay_reply": "Hi!",
        "correction": None,
        "vocab": [],
        "progress_note": "ok",
        "should_finish": False,
    })
    svc = LLMService(provider=fake)

    result = svc.lesson_turn(settings=SETTINGS, lesson=LESSON, history=[], message="hi")

    assert result["roleplay_reply"] == "Hi!"
    assert result["source"] == "fake"


def test_lesson_turn_fallback_on_missing_roleplay_reply():
    fake = FakeProvider(response={"reply": "wrong shape"})
    svc = LLMService(provider=fake)

    result = svc.lesson_turn(settings=SETTINGS, lesson=LESSON, history=[], message="hello")

    assert result["source"] == "fallback"
    assert "roleplay_reply" in result


# ---------------------------------------------------------------------------
# OllamaProvider: проверяем формирование запроса
# ---------------------------------------------------------------------------

def test_ollama_provider_pings_on_init(monkeypatch):
    """При инициализации провайдер дёргает /api/tags чтобы понять, доступна ли модель."""
    captured = {}

    class FakeResponse:
        status_code = 200
        def json(self):
            return {"models": [{"name": "qwen2.5:7b-instruct"}]}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass
        def get(self, url):
            captured["ping_url"] = url
            return FakeResponse()

    monkeypatch.setenv("OLLAMA_HOST", "http://localhost:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
    monkeypatch.setattr("core.llm.ollama_provider.httpx.Client", FakeClient)

    provider = OllamaProvider()

    assert provider.is_configured() is True
    assert captured["ping_url"] == "http://localhost:11434/api/tags"


def test_ollama_provider_unconfigured_when_model_missing(monkeypatch):
    class FakeResponse:
        status_code = 200
        def json(self):
            return {"models": [{"name": "llama3.1:8b"}]}  # другая модель

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass
        def get(self, url):
            return FakeResponse()

    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
    monkeypatch.setattr("core.llm.ollama_provider.httpx.Client", FakeClient)

    provider = OllamaProvider()
    assert provider.is_configured() is False


def test_ollama_provider_unconfigured_when_server_down(monkeypatch):
    import httpx

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass
        def get(self, url):
            raise httpx.ConnectError("connection refused")

    monkeypatch.setattr("core.llm.ollama_provider.httpx.Client", FakeClient)

    provider = OllamaProvider()
    assert provider.is_configured() is False


def test_ollama_provider_generate_json_parses_response(monkeypatch):
    import httpx

    # Сначала ping (через GET), потом chat (через POST).
    state = {"phase": "ping"}

    class FakeResponse:
        def __init__(self, status_code, payload):
            self.status_code = status_code
            self._payload = payload
        def json(self):
            return self._payload
        def raise_for_status(self):
            if self.status_code >= 400:
                raise httpx.HTTPStatusError("err", request=None, response=None)

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass
        def get(self, url):
            return FakeResponse(200, {"models": [{"name": "qwen2.5:7b-instruct"}]})
        def post(self, url, json=None):
            assert json["format"] == "json"
            assert json["model"] == "qwen2.5:7b-instruct"
            assert json["stream"] is False
            assert any(m["role"] == "system" for m in json["messages"])
            assert any(m["role"] == "user" for m in json["messages"])
            return FakeResponse(200, {
                "message": {"content": '{"reply": "Hola!", "correction": null, "vocab": [], "encouragement": "ok"}'}
            })

    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
    monkeypatch.setattr("core.llm.ollama_provider.httpx.Client", FakeClient)

    provider = OllamaProvider()
    result = provider.generate_json("system", "user")

    assert result["reply"] == "Hola!"


def test_ollama_provider_raises_on_non_json_content(monkeypatch):
    """Если модель проигнорировала format=json и вернула текст — ловим RuntimeError."""

    class FakeResponse:
        def __init__(self, status_code, payload):
            self.status_code = status_code
            self._payload = payload
        def json(self):
            return self._payload
        def raise_for_status(self):
            pass

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass
        def get(self, url):
            return FakeResponse(200, {"models": [{"name": "qwen2.5:7b-instruct"}]})
        def post(self, url, json=None):
            return FakeResponse(200, {"message": {"content": "I am sorry, I cannot help."}})

    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
    monkeypatch.setattr("core.llm.ollama_provider.httpx.Client", FakeClient)

    provider = OllamaProvider()
    with pytest.raises(RuntimeError):
        provider.generate_json("system", "user")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def test_factory_default_is_gemini(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    provider = make_provider()
    assert provider.name == "gemini"


def test_factory_explicit_ollama(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    # Подсовываем фейк для httpx, чтобы инициализация не висла.
    import httpx

    class FakeClient:
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def get(self, url):
            raise httpx.ConnectError("nope")

    monkeypatch.setattr("core.llm.ollama_provider.httpx.Client", FakeClient)

    provider = make_provider()
    assert provider.name == "ollama"


def test_factory_auto_falls_back_to_gemini_when_ollama_down(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "auto")
    import httpx

    class FakeClient:
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def get(self, url):
            raise httpx.ConnectError("nope")

    monkeypatch.setattr("core.llm.ollama_provider.httpx.Client", FakeClient)

    provider = make_provider()
    assert provider.name == "gemini"
