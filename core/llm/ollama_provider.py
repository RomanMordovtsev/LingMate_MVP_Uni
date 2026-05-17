"""
Ollama-провайдер: локально развёрнутая LLM (Llama 3.1, Qwen 2.5, Mistral...).

Снимает зависимость от облачных квот. Ollama должна быть установлена
и запущена отдельно (https://ollama.com), модель — скачана через
`ollama pull qwen2.5:7b-instruct` (или другую).

Переменные окружения:
- OLLAMA_HOST    : URL сервера, по умолчанию http://localhost:11434
- OLLAMA_MODEL   : имя модели, по умолчанию qwen2.5:7b-instruct
- OLLAMA_TIMEOUT : таймаут одного запроса в секундах, по умолчанию 120
"""

import json
import os
from typing import Any, Dict

import httpx

from .base import LLMProvider


# Маленькие открытые модели (7B-8B) хуже Gemini следуют JSON-схеме,
# поэтому важно а) ставить format=json на стороне Ollama,
# б) явно напоминать про ключи в самом промпте.
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
                # Имя модели в /api/tags может содержать тег ":latest",
                # сравниваем по префиксу.
                base = self.model_name.split(":")[0]
                return any(m.split(":")[0] == base for m in models)
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
