"""
Ollama-провайдер: локально развёрнутая LLM (Llama 3.1, Qwen 2.5, Mistral...).

Снимает зависимость от облачных квот. Ollama должна быть установлена
и запущена отдельно (https://ollama.com), модель — скачана через
`ollama pull qwen2.5:7b-instruct` (или другую).

Переменные окружения:
- OLLAMA_HOST    : URL сервера, по умолчанию http://localhost:11434
- OLLAMA_MODEL   : имя модели, по умолчанию qwen2.5:7b-instruct
- OLLAMA_TIMEOUT : таймаут одного запроса в секундах, по умолчанию 120
- OLLAMA_THINK   : auto (по умолчанию: thinking выключен у qwen3*/deepseek-r1),
                   false / true — всегда отправлять это значение
"""

import json
import os
from typing import Any, Dict, Optional

import httpx

from .base import LLMProvider


# Маленькие открытые модели (7B-8B) хуже Gemini следуют JSON-схеме,
# поэтому важно а) ставить format=json на стороне Ollama,
# б) явно напоминать про ключи в самом промпте.
# Модели с режимом «размышления» (thinking). У qwen3/qwen3.5 он включён
# по умолчанию: ответ на CPU растягивается в разы, а для короткой
# реплики и JSON-исправления рассуждения не нужны (scouting 2026-11-14).
# Ollama принимает "think": false в /api/chat; моделям без thinking
# параметр не шлём, чтобы старые версии Ollama не ругались.
_THINKING_FAMILIES = ("qwen3", "qwen3.5", "qwen3.6", "deepseek-r1", "magistral")


def _think_setting(model_name: str) -> Optional[bool]:
    """Значение поля ``think`` для запроса или None (не отправлять).

    ``OLLAMA_THINK``: ``auto`` (по умолчанию — выключить для известных
    thinking-семейств), ``false`` / ``true`` — всегда отправлять это значение.
    """
    mode = os.getenv("OLLAMA_THINK", "auto").strip().lower()
    if mode in ("0", "false", "off", "no"):
        return False
    if mode in ("1", "true", "on", "yes"):
        return True
    family = model_name.split(":")[0].lower()
    return False if family in _THINKING_FAMILIES else None


def _tag_matches(wanted: str, installed: str) -> bool:
    """Точное сравнение тегов Ollama с учётом неявного ``:latest``.

    Раньше сравнивали только семейство (до двоеточия), и при скачанной
    ``gemma4:e4b-it-qat`` модель ``gemma4:e2b`` считалась доступной —
    eval потом получал 404 на каждый кейс.
    """
    def norm(tag: str) -> str:
        tag = tag.strip()
        return tag if ":" in tag else f"{tag}:latest"
    return norm(wanted) == norm(installed)


_JSON_REMINDER = (
    "\n\nIMPORTANT: respond with a single valid JSON object only, "
    "no prose before or after, no markdown fences."
)


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self) -> None:
        self.host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        self.model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
        try:
            self.timeout = float(os.getenv("OLLAMA_TIMEOUT", "120"))
        except ValueError:
            self.timeout = 120.0

        # При старте проверяем доступность Ollama-сервера. Делаем это
        # лениво и без падения: если сервер недоступен, is_configured
        # вернёт False, и LLMService сам перейдёт на fallback.
        self._available = self._ping()

    def _ping(self) -> bool:
        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.get(f"{self.host}/api/tags")
                if response.status_code != 200:
                    return False
                # Дополнительно проверяем, что нужная модель скачана.
                # Если нет — пользователь увидит понятную ошибку при
                # первом запросе, а не молчаливый fallback.
                payload = response.json()
                models = [m.get("name", "") for m in payload.get("models", [])]
                # Имя модели в /api/tags может содержать тег ":latest".
                return any(_tag_matches(self.model_name, m) for m in models)
        except Exception:
            return False

    def is_configured(self) -> bool:
        return self._available

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        if not self._available:
            # Возможно, Ollama стартовала позже LingMate — даём второй шанс.
            self._available = self._ping()
            if not self._available:
                raise RuntimeError(
                    f"Ollama is not reachable at {self.host} "
                    f"or model '{self.model_name}' is not pulled"
                )

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt + _JSON_REMINDER},
                {"role": "user", "content": user_prompt},
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.7,
                # num_ctx по умолчанию 2048 — для нашей истории диалога
                # этого мало. 4096 безопасно для большинства 7B-моделей
                # на 16 GB RAM; на 8 GB — снизить до 2048.
                "num_ctx": 4096,
            },
        }

        think = _think_setting(self.model_name)
        if think is not None:
            payload["think"] = think

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.host}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"Ollama request failed: {e}") from e

        # Ollama возвращает ответ в формате {"message": {"content": "..."}}.
        content = (data.get("message") or {}).get("content", "").strip()
        if not content:
            raise RuntimeError("Ollama returned empty response")

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Ollama returned non-JSON content: {content[:200]}"
            ) from e
