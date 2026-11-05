import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

SETTINGS_PATH = DATA_DIR / "user_settings.json"
HISTORY_PATH = DATA_DIR / "chat_history.json"
PROGRESS_PATH = DATA_DIR / "progress.json"
LESSONS_PATH = DATA_DIR / "active_lessons.json"

class JsonStore:
    def __init__(self) -> None:
        for path in [SETTINGS_PATH, HISTORY_PATH, PROGRESS_PATH, LESSONS_PATH]:
            if not path.exists():
                path.write_text("{}", encoding="utf-8")

    def _load(self, path: Path) -> Dict[str, Any]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self, path: Path, payload: Dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def save_settings(self, user_id: str, settings: Dict[str, Any]) -> None:
        data = self._load(SETTINGS_PATH)
        data[user_id] = settings
        self._save(SETTINGS_PATH, data)

    def get_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._load(SETTINGS_PATH).get(user_id)

    def add_message(self, user_id: str, sender: str, message: str, mode: str) -> None:
        data = self._load(HISTORY_PATH)
        data.setdefault(user_id, []).append({
            "sender": sender,
            "message": message,
            "mode": mode,
            "timestamp": datetime.now().isoformat(timespec="seconds")
        })
        self._save(HISTORY_PATH, data)

    def get_history(self, user_id: str, limit: int = 12) -> List[Dict[str, Any]]:
        return self._load(HISTORY_PATH).get(user_id, [])[-limit:]

    def save_progress_note(self, user_id: str, note: Dict[str, Any]) -> None:
        data = self._load(PROGRESS_PATH)
        data.setdefault(user_id, {"mistakes": [], "vocabulary": [], "completed_scenarios": []})
        data[user_id]["mistakes"].extend(note.get("mistakes", []))
        data[user_id]["vocabulary"].extend(note.get("vocabulary", []))
        for scenario in note.get("completed_scenarios", []):
            if scenario not in data[user_id]["completed_scenarios"]:
                data[user_id]["completed_scenarios"].append(scenario)
        self._save(PROGRESS_PATH, data)

    def get_progress(self, user_id: str) -> Dict[str, Any]:
        return self._load(PROGRESS_PATH).get(user_id, {"mistakes": [], "vocabulary": [], "completed_scenarios": []})

    def save_active_lesson(self, user_id: str, lesson: Dict[str, Any]) -> None:
        data = self._load(LESSONS_PATH)
        data[user_id] = lesson
        self._save(LESSONS_PATH, data)

    def get_active_lesson(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._load(LESSONS_PATH).get(user_id)
