"""
Smoke-тест провайдера Ollama с реальным сервером.

Запускать из корня репозитория ПОСЛЕ того, как:
  1. Установлена Ollama (https://ollama.com/download)
  2. Запущена `ollama serve` (или приложение Ollama в фоне)
  3. Скачана модель: `ollama pull qwen2.5:7b-instruct`

Запуск:
    LLM_PROVIDER=ollama python tests/smoke_ollama.py

Тест НЕ запускается в обычном pytest — это интеграционный smoke-чек
для разработчика, который дёргает настоящую модель и печатает её ответы.
"""

import json
import os
import sys

# Так чтобы импорты работали при запуске из корня
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm.ollama_provider import OllamaProvider
from core.llm_service import LLMService


def main():
    print("=" * 60)
    print("Ollama smoke test")
    print("=" * 60)

    provider = OllamaProvider()
    print(f"Host: {provider.host}")
    print(f"Model: {provider.model_name}")
    print(f"Configured: {provider.is_configured()}")

    if not provider.is_configured():
        print("\nFAIL: Ollama не отвечает или модель не скачана.")
        print(f"Проверь: curl {provider.host}/api/tags")
        print(f"Скачай модель: ollama pull {provider.model_name}")
        sys.exit(1)

    # 1) Прямой вызов generate_json
    print("\n--- 1. Прямой вызов generate_json ---")
    try:
        result = provider.generate_json(
            "You are a helpful assistant. Always reply with JSON: {\"greeting\": \"...\"}",
            "Say hello in Spanish."
        )
        print("OK:", json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # 2) free_talk через LLMService
    print("\n--- 2. free_talk через LLMService ---")
    svc = LLMService(provider=provider)
    result = svc.free_talk(
        settings={"target_language": "es", "native_language": "ru", "level": "A1"},
        progress={"mistakes": [], "vocabulary": [], "completed_scenarios": []},
        history=[],
        message="Hola, me llamo Roman. Estoy aprendiendo español.",
    )
    print(f"Source: {result.get('source')}")
    print(f"Reply: {result.get('reply')}")
    print(f"Vocab: {result.get('vocab')}")
    print(f"Correction: {result.get('correction')}")

    # 3) lesson_turn (coffee_shop)
    print("\n--- 3. lesson_turn (кофейня на испанском) ---")
    lesson = {
        "scenario_id": "coffee_shop_es",
        "title": "Cafetería",
        "goal": "Pedir un café en español de forma educada",
        "situation": "Estás en una cafetería en Madrid. Quieres pedir un café.",
    }
    result = svc.lesson_turn(
        settings={"target_language": "es", "native_language": "ru", "level": "A1"},
        lesson=lesson,
        history=[],
        message="Hola, quiero un café por favor.",
    )
    print(f"Source: {result.get('source')}")
    print(f"Roleplay reply: {result.get('roleplay_reply')}")
    print(f"Correction: {result.get('correction')}")
    print(f"Should finish: {result.get('should_finish')}")

    print("\n" + "=" * 60)
    print("Smoke test PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
