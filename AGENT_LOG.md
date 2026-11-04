# Agent log

Newest entries at the top. Each scheduled run appends one entry: date, roadmap item, PR link, decisions made, open questions.

---

## 2026-11-04 — 1.2 Learner profile + onboarding (scheduled run)
- Branch `agent/learner-profile` → PR into `agent/dev`. 1.1 marked `[x]` (PR #1 merged).
- `core/profile.py`: `LearnerProfile` (whole repertoire with levels incl. L1, target + variant + level, goal enum, country/city, interests, daily goal 5–60 min, feedback timing, "who do you want to be" ≤300 chars). Stored inside the existing `user_settings` JSON (no schema change); legacy keys kept so prompts/old endpoints work.
- API: `GET /api/profile/{user}`, `POST /api/profile`; `/api/setup` now **merges** into existing settings so the quick form does not wipe the profile.
- Prompts: `profile_context()` appends repertoire (other languages as possible transfer sources), goal, place, interests and ideal self to free-talk and lesson system prompts; empty for users without onboarding (prompts unchanged).
- UI: onboarding card (Russian labels) shown on first visit / until completed; «Мой профиль» button reopens it. Self-tested with Playwright: no console errors.
- `feedback_timing` is stored but not yet acted on: the feedback policy (3.2) will use it.
- Notion: new entry 03.11 «adelante» added to `docs/learner/roman-spanish.md` (comprehension question, no eval case).
- Tests: 22 → 36 passing.
- Open: none blocking; see PR «Что проверить руками».

## 2026-11-02 — 1.1 SQLite storage (scheduled run)
- Branch `agent/sqlite-storage` → PR into `agent/dev`.
- `SqliteStore` in `core/storage.py` with the exact `JsonStore` interface; `make_store()` picks SQLite by default (`LINGMATE_STORAGE=json` keeps the old files, `LINGMATE_DB_PATH` moves the DB). Auto-imports old JSON on first start with an empty DB; JSON files are only read. Manual: `python -m core.migrate_json`.
- Decision: mistakes/vocabulary/settings/lessons stored as JSON payload columns, so structured corrections (1.3) and the richer profile (1.2) need no schema change; 1.6 can add indexed category columns later. `schema_version` table for future migrations.
- Notion: new situation 02.11 «¡Que aproveche!» added to `docs/learner/roman-spanish.md` (no utterance → no eval case).
- Tests: 15 → 22 passing (parity test JsonStore vs SqliteStore, migration, CLI, auto-import).
- Open: none.

## 2026-11-01 — Learner data, reminders decision, model comparison (manual session with Roman)
- Added `docs/learner/roman-spanish.md` (from Notion page 40afd66e…, plus errors from chats) and `eval/cases/es_roman.jsonl` (3 gold cases) with `tests/test_eval_cases.py`. 15 tests passing.
- Roman decided reminders (2.4, `[?]` removed): browser push 3–4/day + one daily email (~15:00 or ~20:00).
- New 5.6 model comparison; Research Methods project note (Roman writes it himself).
- Finding: many of Roman's errors transfer from English, not Russian.

## 2026-11-01 — More research (manual session with Roman)
- Added `docs/research/multilingual-education.md`, `phonetics.md`, `research-methods.md`.
- Roadmap: repertoire drop-in (3.5), real-life missions (4.8), intercultural notes (4.9), data ethics (5.5), new Phase 6 pronunciation.
- These three courses are still running; more material may come.

## 2026-11-01 — Research + roadmap update (manual session with Roman)
- Added `docs/research/sla.md`, `docs/research/syllabus-design.md`, `docs/research/engagement.md`.
- Roadmap restructured: product vision for general users (Roman = reference user), new Phase 1.2 learner profile/onboarding, Phase 2 daily habit + Yuji, scenario templates parametrised by place/goal.
- Roman's decisions: keep Yuji; Spanish/Roman path first, generalisation later but designed in.
- Open: reminder delivery channel (roadmap 2.4); Multilingual Education and Phonetics material still to come.

## 2026-11-01 — Setup (manual session with Roman)
- Created `agent/dev` from `main` (main = defended bachelor's thesis version, frozen).
- Added `CLAUDE.md` (agent rules), `ROADMAP.md`, `docs/research/morphosyntax.md` (distilled from the LAMS course *The Acquisition of Morphosyntax*).
- Baseline: 14 tests passing.
- Schedule: Mon/Wed/Fri 22:00 Europe/Madrid.
- Open: material from the other LAMS courses (SLA, Syllabus Design, Multilingual Education, Phonetics) still to be added to `docs/research/`.
