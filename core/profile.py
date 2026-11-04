"""Learner profile (roadmap 1.2).

The profile is stored inside the existing `user_settings` JSON payload (no schema change):
`to_settings()` keeps the legacy keys (`target_language`, `native_language`, `level`,
`interests`) so the LLM prompts and old endpoints keep working.

Grounding: sla.md §1 (Ideal L2 Self: ask *who* the learner wants to be), §4 (store the whole
repertoire: multilingual learners transfer from all their languages), syllabus-design.md §1
(curriculum generated from goal, place and interests), engagement.md §1 (learner-set daily goal).
Everything is profile-driven so other languages, places and goals plug in without code changes.
"""
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

CEFR = Literal["A1", "A2", "B1", "B2", "C1", "C2"]
Goal = Literal["relocated", "planning_move", "travel", "work", "study", "partner_family", "hobby"]
GOALS: tuple = Goal.__args__  # type: ignore[attr-defined]

# English phrasing used in the LLM prompt (UI labels live in the frontend, in Russian).
GOAL_PROMPT = {
    "relocated": "lives in the country where the language is spoken and needs it for everyday life",
    "planning_move": "is planning to move abroad and prepares for calls, emails and first weeks there",
    "travel": "wants to travel and handle trips on their own",
    "work": "needs the language for work",
    "study": "studies or will study in the language",
    "partner_family": "wants to talk with a partner or family",
    "hobby": "learns for pleasure and personal interest",
}

LANGUAGE_NAMES = {
    "ru": "Russian", "en": "English", "es": "Spanish", "it": "Italian", "fr": "French",
    "de": "German", "pt": "Portuguese", "tr": "Turkish", "uk": "Ukrainian", "eu": "Basque",
    "ca": "Catalan", "zh": "Chinese", "ja": "Japanese", "ar": "Arabic", "pl": "Polish",
}


def language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code, code)


class KnownLanguage(BaseModel):
    code: str = Field(min_length=2, max_length=10)
    level: Literal["L1", "A1", "A2", "B1", "B2", "C1", "C2"]

    @field_validator("code")
    @classmethod
    def _norm(cls, v: str) -> str:
        return v.strip().lower()


class LearnerProfile(BaseModel):
    user_id: str = Field(min_length=1)
    target_language: str = Field(min_length=2, max_length=10)
    target_variant: Optional[str] = None          # e.g. "es-ES"; regional variant for scenarios/TTS
    level: CEFR                                    # current level in the target language
    languages: List[KnownLanguage] = Field(min_length=1)  # whole repertoire except the target
    goal: Goal
    country: Optional[str] = None
    city: Optional[str] = None
    interests: List[str] = []
    daily_goal_minutes: int = Field(default=10, ge=5, le=60)
    feedback_timing: Literal["immediate", "end_of_session"] = "immediate"
    ideal_self: str = Field(default="", max_length=300)  # "who do you want to be in this language"

    @field_validator("target_language")
    @classmethod
    def _norm_target(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("interests")
    @classmethod
    def _clean_interests(cls, v: List[str]) -> List[str]:
        out: List[str] = []
        for item in v:
            item = item.strip()
            if item and item.lower() not in {x.lower() for x in out}:
                out.append(item)
        return out[:12]

    @model_validator(mode="after")
    def _check_languages(self) -> "LearnerProfile":
        if not any(lang.level == "L1" for lang in self.languages):
            raise ValueError("at least one language must be marked as L1 (native)")
        # The target lives in target_language/level, not in the repertoire list.
        self.languages = [lang for lang in self.languages if lang.code != self.target_language]
        seen, unique = set(), []
        for lang in self.languages:
            if lang.code not in seen:
                seen.add(lang.code)
                unique.append(lang)
        if not unique:
            raise ValueError("the native language cannot be the target language")
        self.languages = unique
        for text_field in ("country", "city", "target_variant"):
            value = getattr(self, text_field)
            setattr(self, text_field, value.strip() or None if isinstance(value, str) else value)
        self.ideal_self = self.ideal_self.strip()
        return self

    @property
    def native_language(self) -> str:
        return next(lang.code for lang in self.languages if lang.level == "L1")

    def to_settings(self) -> Dict[str, Any]:
        """Settings payload: legacy keys + full profile + onboarding flag."""
        data = self.model_dump()
        data["native_language"] = self.native_language
        data["onboarding_completed"] = True
        return data


def profile_from_settings(settings: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Best-effort profile view of stored settings (also for legacy settings saved by /api/setup)."""
    if not settings:
        return None
    native = settings.get("native_language") or "ru"
    languages = settings.get("languages") or [{"code": native, "level": "L1"}]
    return {
        "user_id": settings.get("user_id"),
        "target_language": settings.get("target_language", "en"),
        "target_variant": settings.get("target_variant"),
        "level": settings.get("level", "A1"),
        "languages": languages,
        "goal": settings.get("goal"),
        "country": settings.get("country"),
        "city": settings.get("city"),
        "interests": settings.get("interests", []),
        "daily_goal_minutes": settings.get("daily_goal_minutes", 10),
        "feedback_timing": settings.get("feedback_timing", "immediate"),
        "ideal_self": settings.get("ideal_self", ""),
        "onboarding_completed": bool(settings.get("onboarding_completed")),
    }


def profile_context(settings: Optional[Dict[str, Any]]) -> str:
    """Extra system-prompt lines built from the profile. Empty for legacy settings,
    so prompts for users without onboarding stay exactly as before."""
    if not settings or not settings.get("onboarding_completed"):
        return ""
    lines = ["", "Learner profile (use it to choose topics, examples and comparisons):"]
    others = [l for l in settings.get("languages", []) if l.get("level") != "L1"]
    if others:
        known = ", ".join(f"{language_name(l['code'])} ({l['level']})" for l in others)
        lines.append(f"- Also knows: {known}. When it helps, compare with the closest of these "
                     f"languages; errors may transfer from any of them, not only the native one.")
    goal = settings.get("goal")
    if goal in GOAL_PROMPT:
        lines.append(f"- Goal: the learner {GOAL_PROMPT[goal]}.")
    place = ", ".join(p for p in (settings.get("city"), settings.get("country")) if p)
    if place:
        lines.append(f"- Place: {place}. Prefer situations, names and customs from there.")
    if settings.get("interests"):
        lines.append(f"- Interests: {', '.join(settings['interests'])}.")
    if settings.get("ideal_self"):
        lines.append(f"- Who they want to be in the language (their own words): \"{settings['ideal_self']}\".")
    return "\n".join(lines) + "\n" if len(lines) > 2 else ""
