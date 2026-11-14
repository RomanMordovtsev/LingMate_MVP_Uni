"""Ollama: точное сравнение тегов и выключение thinking (scouting 2026-11-14)."""

import pytest

from core.llm.ollama_provider import OllamaProvider, _tag_matches, _think_setting


class _Resp:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        pass


def _fake_client(installed, captured):
    class FakeClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def get(self, url):
            return _Resp({"models": [{"name": n} for n in installed]})

        def post(self, url, json=None):
            captured["payload"] = json
            return _Resp({"message": {"content": '{"reply": "Hola"}'}})

    return FakeClient


@pytest.mark.parametrize("wanted,installed,ok", [
    ("gemma4:e2b", "gemma4:e2b", True),
    ("gemma4:e2b", "gemma4:e4b-it-qat", False),
    ("gemma3", "gemma3:latest", True),
    ("gemma3:latest", "gemma3", True),
    ("gemma3:4b", "gemma3:latest", False),
    ("qwen3.5:4b-q4_K_M", "qwen3.5:4b-q4_K_M", True),
])
def test_tag_matches(wanted, installed, ok):
    assert _tag_matches(wanted, installed) is ok


def test_other_tag_of_same_family_is_not_configured(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "gemma4:e2b")
    monkeypatch.setattr("core.llm.ollama_provider.httpx.Client",
                        _fake_client(["gemma4:e4b-it-qat"], {}))
    assert OllamaProvider().is_configured() is False


@pytest.mark.parametrize("model,expected", [
    ("qwen3.5:4b-q4_K_M", False),
    ("qwen3:4b", False),
    ("deepseek-r1:7b", False),
    ("gemma4:e2b", None),
    ("qwen2.5:7b-instruct", None),
])
def test_think_auto(monkeypatch, model, expected):
    monkeypatch.delenv("OLLAMA_THINK", raising=False)
    assert _think_setting(model) is expected


def test_think_env_override(monkeypatch):
    monkeypatch.setenv("OLLAMA_THINK", "false")
    assert _think_setting("gemma4:e2b") is False
    monkeypatch.setenv("OLLAMA_THINK", "true")
    assert _think_setting("qwen3.5:4b") is True


@pytest.mark.parametrize("model,has_think", [
    ("qwen3.5:4b-q4_K_M", True),
    ("gemma4:e2b", False),
])
def test_payload_think_field(monkeypatch, model, has_think):
    monkeypatch.delenv("OLLAMA_THINK", raising=False)
    monkeypatch.setenv("OLLAMA_MODEL", model)
    captured = {}
    monkeypatch.setattr("core.llm.ollama_provider.httpx.Client",
                        _fake_client([model], captured))
    assert OllamaProvider().generate_json("sys", "user") == {"reply": "Hola"}
    if has_think:
        assert captured["payload"]["think"] is False
    else:
        assert "think" not in captured["payload"]
