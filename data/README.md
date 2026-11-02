# `data/` — runtime state

This directory holds per-user data created at runtime.

Since roadmap 1.1 the app stores everything in **`lingmate.sqlite3`** (SQLite,
tables: `user_settings`, `messages`, `mistakes`, `vocabulary`,
`completed_scenarios`, `active_lessons`). On the first start with an empty
database, the old JSON files below are imported automatically; they are never
modified or deleted. Manual import: `python -m core.migrate_json`.
Set `LINGMATE_STORAGE=json` to keep using the JSON files, or
`LINGMATE_DB_PATH=...` to put the database elsewhere.

Legacy JSON files (still created by `JsonStore`):

- `user_settings.json` — saved profiles (target language, level, interests)
- `chat_history.json` — Free-Talk and Lesson conversation logs
- `progress.json` — vocabulary, completed scenarios, progress notes
- `active_lessons.json` — currently-open scenario for each user

These files (and `*.sqlite3`) are **gitignored** because they belong to whoever is running the
app, not to the source tree. They are created automatically on first startup
by `core/storage.py` — you do not need to seed them manually.

Only `.gitkeep` and this README are versioned, so that the directory exists
after `git clone`.
