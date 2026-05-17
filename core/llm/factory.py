"""
Фабрика провайдеров.

Выбор провайдера управляется переменной окружения LLM_PROVIDER:
- "gemini" (по умолчанию) — только облачный Gemini API
- "ollama"               — только локальная модель через Ollama
- "auto"                 — пробуем Gemini первым (выше качество), при
                           недоступности (нет ключа, geo-блок, сетевая
                           ошибка, ошибка квоты) автоматически переходим
                           к Ollama. Если упали оба — LLMService уйдёт
                           в rule-based fallback.

В режиме "auto" LLMService использует chain: при ошибке первого
провайдера прозрачно пробует следующего, и только когда упали все —
включает rule-based fallback.
"""

import os
from typing import List

from .base import LLMProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider


def make_provider_chain() -> List[LLMProvider]:
    """Возвращает упорядоченный список провайдеров для попыток.

    В режиме "auto" возвращаются оба провайдера: сначала Gemini (выше
    качество ответов), затем Ollama (локальный резерв). LLMService
    при ошибке/неконфигурированности первого автоматически переходит
    к следующему в цепочке.
    """
    choice = os.getenv("LLM_PROVIDER", "gemini").strip().lower()

    if choice == "ollama":
        return [OllamaProvider()]

    if choice == "auto":
        return [GeminiProvider(), OllamaProvider()]

    # gemini — дефолт и одновременно явный выбор
    return [GeminiProvider()]


def make_provider() -> LLMProvider:
    """Обратно-совместимое API: возвращает первый провайдер цепочки.

    Старые места кода (тесты, эндпоинт /api/test-gemini) продолжают
    работать с одним провайдером без изменений.
    """
    return make_provider_chain()[0]
