from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from core.models import UserSettings, ChatRequest, LessonStartRequest, LessonMessageRequest
from core.storage import JsonStore
from core.scenarios import SCENARIOS
from core.llm_service import LLMService

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

store = JsonStore()
llm = LLMService()
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def clean_correction(text: str | None) -> list[str]:
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
        "gemini_configured": llm.is_configured(),
        "scenarios": [{"id": key, **value} for key, value in SCENARIOS.items()]
    }


@app.post("/api/setup")
def setup_user(settings: UserSettings):
    store.save_settings(settings.user_id, settings.model_dump())
    return {"ok": True, "settings": settings.model_dump()}


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
        "mistakes": clean_correction(result.get("correction")) if result.get("source") == "gemini" else [],
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
        "mistakes": clean_correction(result.get("correction")) if result.get("source") == "gemini" else [],
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

@app.get("/api/test-gemini")
def test_gemini():
    try:
        result = llm._call_gemini(
            "You are a test. Return JSON.",
            '{"message": "Hello"}'
        )
        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)