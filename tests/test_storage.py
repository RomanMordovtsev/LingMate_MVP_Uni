"""SQLite storage (roadmap 1.1): same behaviour as JsonStore + JSON migration. No network."""
import json

import pytest

from core import storage
from core.migrate_json import main as migrate_main
from core.storage import JsonStore, SqliteStore, make_store, migrate_json_to_sqlite


@pytest.fixture
def json_dir(tmp_path, monkeypatch):
    """Point JsonStore's module-level paths at a temp dir."""
    d = tmp_path / "data"
    d.mkdir()
    for name in ["SETTINGS_PATH", "HISTORY_PATH", "PROGRESS_PATH", "LESSONS_PATH"]:
        monkeypatch.setattr(storage, name, d / getattr(storage, name).name)
    monkeypatch.setattr(storage, "DATA_DIR", d)
    return d


def _exercise(store):
    store.save_settings("roman", {"user_id": "roman", "target_language": "es", "level": "A2"})
    store.save_settings("roman", {"user_id": "roman", "target_language": "es", "level": "B1"})
    for i in range(15):
        store.add_message("roman", "user" if i % 2 == 0 else "bot", f"msg {i} — ñ", mode="free_talk")
    store.add_message("ana", "user", "hola", mode="lesson")
    store.save_progress_note("roman", {"mistakes": ["línea → cola"], "vocabulary": ["la cola", "el asiento"]})
    store.save_progress_note("roman", {"mistakes": [], "vocabulary": ["la ventanilla"],
                                       "completed_scenarios": ["es_cafe"]})
    store.save_progress_note("roman", {"completed_scenarios": ["es_cafe", "es_bus"]})
    store.save_active_lesson("roman", {"scenario_id": "es_cafe", "title": "Café"})
    store.save_active_lesson("roman", {"scenario_id": "es_bus", "title": "Bus"})


def _snapshot(store):
    out = {}
    for user in ["roman", "ana", "nobody"]:
        hist = [{k: v for k, v in m.items() if k != "timestamp"} for m in store.get_history(user)]
        out[user] = (store.get_settings(user), hist, store.get_progress(user), store.get_active_lesson(user))
    out["limit3"] = [m["message"] for m in store.get_history("roman", limit=3)]
    return out


def test_sqlite_matches_json_store(json_dir, tmp_path):
    js, sq = JsonStore(), SqliteStore(tmp_path / "t.sqlite3")
    _exercise(js)
    _exercise(sq)
    assert _snapshot(sq) == _snapshot(js)


def test_sqlite_basic_shapes(tmp_path):
    sq = SqliteStore(tmp_path / "t.sqlite3")
    assert sq.is_empty()
    assert sq.get_settings("x") is None
    assert sq.get_active_lesson("x") is None
    assert sq.get_progress("x") == {"mistakes": [], "vocabulary": [], "completed_scenarios": []}
    _exercise(sq)
    assert not sq.is_empty()
    assert sq.get_history("roman", limit=3)[-1]["message"] == "msg 14 — ñ"
    assert sq.get_progress("roman")["completed_scenarios"] == ["es_cafe", "es_bus"]
    assert sq.get_settings("roman")["level"] == "B1"


def test_data_survives_reopen_and_structured_mistakes(tmp_path):
    db = tmp_path / "t.sqlite3"
    correction = {"original": "la línea", "corrected": "la cola", "error_category": "lexical"}
    SqliteStore(db).save_progress_note("roman", {"mistakes": [correction]})
    assert SqliteStore(db).get_progress("roman")["mistakes"] == [correction]


def test_migration_copies_everything_and_keeps_json(json_dir, tmp_path):
    js = JsonStore()
    _exercise(js)
    before = {p.name: p.read_text(encoding="utf-8") for p in json_dir.glob("*.json")}

    sq = SqliteStore(tmp_path / "m.sqlite3")
    counts = migrate_json_to_sqlite(sq, json_dir)

    assert counts == {"users": 1, "messages": 16, "mistakes": 1, "vocabulary": 3,
                      "completed_scenarios": 2, "active_lessons": 1}
    assert _snapshot(sq) == _snapshot(js)
    # timestamps preserved
    assert sq.get_history("ana")[0]["timestamp"] == js.get_history("ana")[0]["timestamp"]
    # JSON untouched
    assert {p.name: p.read_text(encoding="utf-8") for p in json_dir.glob("*.json")} == before


def test_migration_tolerates_broken_json(json_dir, tmp_path):
    (json_dir / "chat_history.json").write_text("{not json", encoding="utf-8")
    (json_dir / "user_settings.json").write_text(json.dumps({"a": {"level": "A1"}}), encoding="utf-8")
    sq = SqliteStore(tmp_path / "m.sqlite3")
    counts = migrate_json_to_sqlite(sq, json_dir)
    assert counts["users"] == 1 and counts["messages"] == 0


def test_cli_refuses_non_empty_db(json_dir, tmp_path):
    JsonStore().save_settings("roman", {"level": "A2"})
    db = tmp_path / "cli.sqlite3"
    assert migrate_main(["--db", str(db), "--data-dir", str(json_dir)]) == 0
    assert SqliteStore(db).get_settings("roman") == {"level": "A2"}
    assert migrate_main(["--db", str(db), "--data-dir", str(json_dir)]) == 1


def test_make_store_auto_imports_once(json_dir, tmp_path, monkeypatch):
    JsonStore().save_settings("roman", {"level": "A2"})
    db = tmp_path / "app.sqlite3"
    monkeypatch.delenv("LINGMATE_STORAGE", raising=False)
    monkeypatch.setenv("LINGMATE_DB_PATH", str(db))

    store = make_store()
    assert isinstance(store, SqliteStore)
    assert store.get_settings("roman") == {"level": "A2"}
    store.add_message("roman", "user", "hola", "free_talk")
    make_store()  # second start: no re-import, no duplicates
    assert len(SqliteStore(db).get_history("roman")) == 1

    monkeypatch.setenv("LINGMATE_STORAGE", "json")
    assert isinstance(make_store(), JsonStore)
