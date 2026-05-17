"""
Абстрактный интерфейс LLM-провайдера.

Каждый провайдер (Gemini, Ollama, OpenAI...) реализует этот интерфейс.
Это позволяет LingMate работать как с облачными API, так и с локально
развёрнутыми моделями, не завися от квот конкретного сервиса.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class LLMProvider(ABC):
    """
    Базовый класс для любого LLM-провайдера.

    Контракт минимальный: уметь сгенерировать JSON-ответ по system + user
    промптам и сообщить, готов ли провайдер к работе.
    """

    name: str = "base"

    @abstractmethod
    def is_configured(self) -> bool:
        """
        Готов ли провайдер обрабатывать запросы (есть ключ, доступен сервер).
        Если False — LLMService переключается на rule-based fallback.
        """
        ...

    @abstractmethod
    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Сгенерировать ответ в JSON-формате.

        Returns:
            dict — распарсенный JSON-ответ модели.

        Raises:
            RuntimeError — при сетевых ошибках, невалидном JSON,
            недоступности модели и т.п. LLMService ловит исключение
            и переключается на fallback.
        """
        ...
