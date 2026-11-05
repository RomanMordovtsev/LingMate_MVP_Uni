# `data/` — runtime state

This directory holds per-user data created at runtime:

- `user_settings.json` — saved profiles (target language, level, interests)
- `chat_history.json` — Free-Talk and Lesson conversation logs
- `progress.json` — vocabulary, completed scenarios, progress notes
- `active_lessons.json` — currently-open scenario for each user

These files are **gitignored** because they belong to whoever is running the
app, not to the source tree. They are created automatically on first startup
by `core/storage.py` — you do not need to seed them manually.

Only `.gitkeep` and this README are versioned, so that the directory exists
after `git clone`.
