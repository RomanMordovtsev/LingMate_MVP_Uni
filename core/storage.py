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


# ---------------------------------------------------------------------------
# SQLite storage (roadmap 1.1). Same public interface as JsonStore.
# ---------------------------------------------------------------------------
import os
import sqlite3
from contextlib import contextmanager

DB_PATH = DATA_DIR / "lingmate.sqlite3"

_EMPTY_PROGRESS = {"mistakes": [], "vocabulary": [], "completed_scenarios": []}

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS user_settings (
    user_id TEXT PRIMARY KEY,
    settings TEXT NOT NULL,              -- JSON object (profile grows in roadmap 1.2)
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    sender TEXT NOT NULL,
    message TEXT NOT NULL,
    mode TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id, id);
CREATE TABLE IF NOT EXISTS mistakes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    payload TEXT NOT NULL,               -- JSON: string today, structured object from roadmap 1.3
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mistakes_user ON mistakes(user_id, id);
CREATE TABLE IF NOT EXISTS vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    payload TEXT NOT NULL,               -- JSON: string or object
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_vocabulary_user ON vocabulary(user_id, id);
CREATE TABLE IF NOT EXISTS completed_scenarios (
    user_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    PRIMARY KEY (user_id, scenario_id)
);
CREATE TABLE IF NOT EXISTS active_lessons (
    user_id TEXT PRIMARY KEY,
    lesson TEXT NOT NULL,                -- JSON object
    updated_at TEXT NOT NULL
);
"""
SCHEMA_VERSION = 1


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class SqliteStore:
    """SQLite-backed store with the same methods and return shapes as JsonStore.

    One short-lived connection per call keeps it safe for FastAPI's threadpool.
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as conn:
            conn.executescript(SCHEMA)
            if conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0] == 0:
                conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def is_empty(self) -> bool:
        with self._conn() as conn:
            tables = ["user_settings", "messages", "mistakes", "vocabulary",
                      "completed_scenarios", "active_lessons"]
            return all(conn.execute(f"SELECT 1 FROM {t} LIMIT 1").fetchone() is None for t in tables)

    # --- settings -----------------------------------------------------------
    def save_settings(self, user_id: str, settings: Dict[str, Any]) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO user_settings (user_id, settings, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET settings = excluded.settings, updated_at = excluded.updated_at",
                (user_id, json.dumps(settings, ensure_ascii=False), _now()),
            )

    def get_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute("SELECT settings FROM user_settings WHERE user_id = ?", (user_id,)).fetchone()
        return json.loads(row[0]) if row else None

    # --- history ------------------------------------------------------------
    def add_message(self, user_id: str, sender: str, message: str, mode: str,
                    timestamp: Optional[str] = None) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO messages (user_id, sender, message, mode, timestamp) VALUES (?, ?, ?, ?, ?)",
                (user_id, sender, message, mode, timestamp or _now()),
            )

    def get_history(self, user_id: str, limit: int = 12) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT sender, message, mode, timestamp FROM messages WHERE user_id = ? "
                "ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        return [{"sender": s, "message": m, "mode": md, "timestamp": ts} for s, m, md, ts in reversed(rows)]

    # --- progress -----------------------------------------------------------
    def save_progress_note(self, user_id: str, note: Dict[str, Any]) -> None:
        now = _now()
        with self._conn() as conn:
            conn.executemany(
                "INSERT INTO mistakes (user_id, payload, created_at) VALUES (?, ?, ?)",
                [(user_id, json.dumps(m, ensure_ascii=False), now) for m in note.get("mistakes", [])],
            )
            conn.executemany(
                "INSERT INTO vocabulary (user_id, payload, created_at) VALUES (?, ?, ?)",
                [(user_id, json.dumps(v, ensure_ascii=False), now) for v in note.get("vocabulary", [])],
            )
            conn.executemany(
                "INSERT OR IGNORE INTO completed_scenarios (user_id, scenario_id, completed_at) VALUES (?, ?, ?)",
                [(user_id, s, now) for s in note.get("completed_scenarios", [])],
            )

    def get_progress(self, user_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            mistakes = [json.loads(r[0]) for r in conn.execute(
                "SELECT payload FROM mistakes WHERE user_id = ? ORDER BY id", (user_id,))]
            vocabulary = [json.loads(r[0]) for r in conn.execute(
                "SELECT payload FROM vocabulary WHERE user_id = ? ORDER BY id", (user_id,))]
            scenarios = [r[0] for r in conn.execute(
                "SELECT scenario_id FROM completed_scenarios WHERE user_id = ? ORDER BY rowid", (user_id,))]
        return {"mistakes": mistakes, "vocabulary": vocabulary, "completed_scenarios": scenarios}

    # --- active lesson ------------------------------------------------------
    def save_active_lesson(self, user_id: str, lesson: Dict[str, Any]) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO active_lessons (user_id, lesson, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET lesson = excluded.lesson, updated_at = excluded.updated_at",
                (user_id, json.dumps(lesson, ensure_ascii=False), _now()),
            )

    def get_active_lesson(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute("SELECT lesson FROM active_lessons WHERE user_id = ?", (user_id,)).fetchone()
        return json.loads(row[0]) if row else None


# ---------------------------------------------------------------------------
# JSON → SQLite migration (non-destructive: JSON files are only read)
# ---------------------------------------------------------------------------
def _read_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def migrate_json_to_sqlite(store: SqliteStore, data_dir: Optional[Path] = None) -> Dict[str, int]:
    """Copy all JsonStore data into `store`. Returns counts per table. JSON files are left untouched."""
    d = Path(data_dir) if data_dir else DATA_DIR
    counts = {"users": 0, "messages": 0, "mistakes": 0, "vocabulary": 0,
              "completed_scenarios": 0, "active_lessons": 0}

    for user_id, settings in _read_json(d / SETTINGS_PATH.name).items():
        store.save_settings(user_id, settings)
        counts["users"] += 1

    for user_id, messages in _read_json(d / HISTORY_PATH.name).items():
        for msg in messages or []:
            store.add_message(user_id, msg.get("sender", ""), msg.get("message", ""),
                              msg.get("mode", ""), timestamp=msg.get("timestamp"))
            counts["messages"] += 1

    for user_id, prog in _read_json(d / PROGRESS_PATH.name).items():
        prog = prog or {}
        store.save_progress_note(user_id, prog)
        counts["mistakes"] += len(prog.get("mistakes", []))
        counts["vocabulary"] += len(prog.get("vocabulary", []))
        counts["completed_scenarios"] += len(set(prog.get("completed_scenarios", [])))

    for user_id, lesson in _read_json(d / LESSONS_PATH.name).items():
        store.save_active_lesson(user_id, lesson)
        counts["active_lessons"] += 1

    return counts


def make_store():
    """Store used by the app. LINGMATE_STORAGE=json keeps the old JSON files; default is SQLite.

    On first start with an empty database, existing JSON data is imported automatically.
    """
    if os.getenv("LINGMATE_STORAGE", "sqlite").lower() == "json":
        return JsonStore()
    db_path = os.getenv("LINGMATE_DB_PATH")
    store = SqliteStore(Path(db_path) if db_path else None)
    if store.is_empty() and any(p.exists() for p in [SETTINGS_PATH, HISTORY_PATH, PROGRESS_PATH, LESSONS_PATH]):
        migrate_json_to_sqlite(store)
    return store
