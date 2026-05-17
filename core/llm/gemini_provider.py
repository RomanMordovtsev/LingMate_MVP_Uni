"""
Gemini-провайдер.

Использует google-genai SDK. Требует GEMINI_API_KEY в окружении.
Бесплатная квота на gemini-2.5-flash достаточна для разработки,
но не для продакшена — отсюда и абстракция провайдеров.
"""

import json
import os
from typing import Any, Dict

from .base import LLMProvider

try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        enabled = os.getenv("GEMINI_ENABLED", "true").strip().lower() == "true"

        self.client = None
        if enabled and self.api_key and genai is not None:
            self.client = genai.Client(api_key=self.api_key)

    def is_configured(self) -> bool:
        return self.client is not None

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        if self.client is None:
            raise RuntimeError("Gemini client is not configured")

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    response_mime_type="application/json",
                ),
                contents=user_prompt,
            )
            text = response.text or "{}"
            return json.loads(text)
        except Exception as e:
            raise RuntimeError(f"Gemini request failed: {e}") from e
