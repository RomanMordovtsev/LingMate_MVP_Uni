# Agent log

Newest entries at the top. Each scheduled run appends one entry: date, roadmap item, PR link, decisions made, open questions.

---

## 2026-11-08 — docs/feedback/2026-11-08 (first local eval) fixes (scheduled run)
- Branch `agent/eval-fixes` → PR into `agent/dev`. 1.3a marked `[x]` (PR #6 merged). No open PRs, no comments.
- Feedback 2026-11-08 handled: **§1** report names: extensions appended as text (no `with_suffix`), `:`/`/` → `-`, dots kept: `2026-11-08-gemini-gemini-2.5-flash.json`, `…-ollama-qwen2.5-7b-instruct.json`; test with 4 model names. **§2** provider failures are excluded from all quality metrics (summary has `answered` + `provider_failures`; Markdown lists failures in their own section); `--sleep` between cases (default 4 s gemini, 0 otherwise); eval-only backoff 5/15/30 s on 429/503 (`LLMService.retry_delays`; the app keeps one 1.5 s retry). So the 08.11 Gemini numbers (14–17 failures scored as misses) were understated: re-run needed. **§3** noted: qwen2.5:7b-instruct = 7% detection, 18 s/answer → not usable for corrections; replacement is 5.7 scouting (next even Saturday). **§4** `eval.run` reconfigures stdout/stderr to utf-8 (`errors=replace`); test with a cp1251 console. **§5** new diagnostics `transfer_flagged_rate` / `transfer_source_filled` to see whether models set `is_transfer` and name the language at all; contract now says `transfer_source` is required when `is_transfer` is true (needs live check).
- Notion: no new entries since 07.11.
- Tests: 62 → 69. No UI changes → no Playwright pass; CLI run by hand with `--provider rule`.

## 2026-11-07 — 1.3a Evaluation harness (scheduled run)
- Branch `agent/eval-harness` → PR #6 into `agent/dev`. 1.3 marked `[x]` (PR #5 merged). No open PRs, no new comments.
- `eval/run.py` CLI: `python -m eval.run --provider gemini|ollama|rule [--model M] [--id CASE] [--cases F] [--out DIR]`. Uses `LLMService.free_talk` with the real prompts + `normalize_correction`, so the eval measures what the app does. Writes `eval/reports/<date>-<provider>-<model>.json` + `.md`. Exit 2 with a hint if the provider is not configured. Keys only from env/.env; scrubbed from error strings.
- `eval/scoring.py` (pure): detection, case-level category recall, category precision (wrong category / correction on correct input = FP), corrected-text match vs `acceptable` (punctuation-insensitive, accent-sensitive; fragment substitution), false-positive rate on correct input, transfer-source accuracy, latency; provider failures counted separately.
- Dataset: `es_synthetic.jsonl` — 25 error cases (every category ≥2) built from Roman's situations + 6 correct utterances (`expect_correction: false`, e.g. *porfa* in a café, feedback §5). Schema check extended. Total 34 cases.
- Rule baseline: 0% detection (expected: fallback never corrects) — the floor for comparisons.
- Notion: new entry 07.11 «Виды молока» → `docs/learner/roman-spanish.md` (vocabulary; feeds 4.1 café chunks).
- Docs/feedback 2026-11-05: all items already handled or moved (see 2026-11-06); nothing new.
- Tests: 51 → 62. No UI changes, so no Playwright pass this run; CLI run by hand (rule OK, ollama → exit 2).
- Open: real-model runs + weekly night task on Roman's computer (his decision).

## 2026-11-06 — 1.3 Structured corrective feedback + Roman's test findings (scheduled run)
- Branch `agent/structured-feedback` → PR into `agent/dev`. 1.2 marked `[x]` (PR #2 merged). No open PRs / comments.
- `core/feedback.py`: contract (`original`, `corrected`, `error_category` ×12, `cf_type` ×5, `is_transfer`, `transfer_source`, `explanation` in L1) + tolerant `normalize_correction` (legacy strings, aliases like "spelling"→`spelling_accent`, bad enums → safe defaults, self-identical "corrections" dropped). Both system prompts get the same contract block.
- Feedback 2026-11-05 handled: **§1** one retry with 1.5 s backoff on 503/429/UNAVAILABLE before the next provider; responses carry `source` + `model`; UI label under replies with `?debug=1`. **§4** prompt: correct only the current `message`, never earlier turns. **§5** prompt: colloquial forms (*porfa*, tú with a barman) are not register errors. **§3** partly: free-talk prompt asks to respond to the learner's content, not repeat itself, not assert unsure cultural facts (needs live check). **§2** covered by contract (EN calques as lexical transfer) — needs live check. **§6, §7** moved into roadmap 4.1 / 4.2.
- Progress log still stores one readable line per correction (`original → corrected — explanation [category]`); the structured error log is 1.6.
- Notion: 3 new entries (05.11 cenar, 06.11 postal, 06.11 calefacción) → `docs/learner/roman-spanish.md`; vocabulary questions, no eval cases.
- Tests: 36 → 51.
- Open: whether real models follow the contract (Gemini / qwen2.5) — Roman's local check; then 1.3a.

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
