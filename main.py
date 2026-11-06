from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from core.models import UserSettings, ChatRequest, LessonStartRequest, LessonMessageRequest
from core.storage import make_store
from core.profile import LearnerProfile, profile_from_settings
from core.scenarios import SCENARIOS
from core.llm_service import LLMService
from core.feedback import correction_to_text

from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LingMate MVP", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = make_store()  # SQLite by default; LINGMATE_STORAGE=json for the old files
llm = LLMService()
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def clean_correction(correction: dict | str | None) -> list[str]:
    # Structured corrections (roadmap 1.3) are logged as one readable line for now;
    # the full object goes to the error log in 1.6.
    text = correction_to_text(correction) if isinstance(correction, dict) else correction
    if not text:
        return []

    lowered = text.lower()
    banned_parts = [
        "gemini временно недоступен",
        "локальный резервный ответ",
        "внешней модели",
        "резервном режиме",
    ]

    if any(part in lowered for part in banned_parts):
        return []

    return [text]


def clean_vocab(vocab: list | None) -> list[str]:
    if not vocab:
        return []

    cleaned = []
    seen = set()

    for item in vocab:
        if not item:
            continue

        if isinstance(item, dict):
            text = (
                item.get("phrase")
                or item.get("word")
                or item.get("text")
                or item.get("label")
                or ""
            )
        else:
            text = str(item).strip()

        if not text:
            continue

        key = text.lower()
        if key in seen:
            continue

        seen.add(key)
        cleaned.append(text)

    return cleaned


@app.get("/")
def root() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/status")
def status():
    return {
        "ok": True,
        # Имя текущего провайдера: gemini, ollama, ... — для отладки и UI.
        "llm_provider": llm.provider_name,
        # Готов ли провайдер обрабатывать запросы.
        "llm_configured": llm.is_configured(),
        # Старое поле сохраняется для обратной совместимости с index.html.
        # Истинно, когда выбран Gemini И он настроен.
        "gemini_configured": llm.provider_name == "gemini" and llm.is_configured(),
        "scenarios": [{"id": key, **value} for key, value in SCENARIOS.items()]
    }


@app.post("/api/setup")
def setup_user(settings: UserSettings):
    # Merge: the quick settings form must not wipe the onboarding profile (roadmap 1.2).
    merged = {**(store.get_settings(settings.user_id) or {}), **settings.model_dump()}
    if merged.get("languages"):
        # Keep the repertoire's L1 in sync with the quick form's native language.
        others = [l for l in merged["languages"] if l.get("level") != "L1"
                  and l.get("code") != merged["native_language"]]
        merged["languages"] = [{"code": merged["native_language"], "level": "L1"}] + others
    store.save_settings(settings.user_id, merged)
    return {"ok": True, "settings": merged}


@app.get("/api/profile/{user_id}")
def get_profile(user_id: str):
    profile = profile_from_settings(store.get_settings(user_id))
    return {"profile": profile, "onboarding_completed": bool(profile and profile["onboarding_completed"])}


@app.post("/api/profile")
def save_profile(profile: LearnerProfile):
    settings = {**(store.get_settings(profile.user_id) or {}), **profile.to_settings()}
    store.save_settings(profile.user_id, settings)
    return {"ok": True, "profile": profile_from_settings(settings)}


@app.post("/api/chat")
def chat(req: ChatRequest):
    settings = store.get_settings(req.user_id)
    if not settings:
        raise HTTPException(status_code=400, detail="Сначала нажми Save settings")

    progress = store.get_progress(req.user_id)
    history = store.get_history(req.user_id)

    result = llm.free_talk(
        settings=settings,
        progress=progress,
        history=history,
        message=req.message
    )

    store.add_message(req.user_id, "user", req.message, mode="free_talk")
    store.add_message(req.user_id, "bot", result["reply"], mode="free_talk")

    progress_note = {
        # Сохраняем коррекции от любой настоящей модели (gemini, ollama, ...),
        # но не от rule-based fallback — он не делает реальных коррекций.
        "mistakes": clean_correction(result.get("correction")) if result.get("source") != "fallback" else [],
        "vocabulary": clean_vocab(result.get("vocab", []))
    }
    store.save_progress_note(req.user_id, progress_note)

    return result


@app.post("/api/lesson/start")
def lesson_start(req: LessonStartRequest):
    settings = store.get_settings(req.user_id)
    if not settings:
        raise HTTPException(status_code=400, detail="Сначала нажми Save settings")

    if req.scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail="Scenario not found")

    lesson = SCENARIOS[req.scenario_id]
    store.save_active_lesson(req.user_id, {"scenario_id": req.scenario_id, **lesson})

    intro = {
        "title": lesson["title"],
        "goal": lesson["goal"],
        "situation": lesson["situation"],
        "example_dialogue": lesson["example_dialogue"],
        "key_phrases": lesson["key_phrases"]
    }
    return intro


@app.post("/api/lesson/message")
def lesson_message(req: LessonMessageRequest):
    settings = store.get_settings(req.user_id)
    lesson = store.get_active_lesson(req.user_id)

    if not settings or not lesson:
        raise HTTPException(status_code=400, detail="Сначала начни урок")

    history = store.get_history(req.user_id)
    result = llm.lesson_turn(
        settings=settings,
        lesson=lesson,
        history=history,
        message=req.message
    )

    store.add_message(req.user_id, "user", req.message, mode="lesson")
    store.add_message(req.user_id, "bot", result["roleplay_reply"], mode="lesson")

    progress_note = {
        "mistakes": clean_correction(result.get("correction")) if result.get("source") != "fallback" else [],
        "vocabulary": clean_vocab(result.get("vocab", [])),
        "completed_scenarios": [lesson["scenario_id"]] if result.get("should_finish") else []
    }
    store.save_progress_note(req.user_id, progress_note)

    return result


@app.get("/api/progress/{user_id}")
def progress(user_id: str):
    settings = store.get_settings(user_id)
    return {
        "settings": settings,
        "progress": store.get_progress(user_id),
        "history": store.get_history(user_id, limit=20)
    }

@app.get("/api/test-llm")
def test_llm():
    """Универсальный тест текущего LLM-провайдера."""
    try:
        result = llm._call_gemini(
            "You are a test. Return JSON.",
            '{"message": "Hello"}'
        )
        return {"ok": True, "provider": llm.provider_name, "result": result}
    except Exception as e:
        return {"ok": False, "provider": llm.provider_name, "error": str(e)}


# Старое имя — оставлено для обратной совместимости.
@app.get("/api/test-gemini")
def test_gemini():
    return test_llm()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)