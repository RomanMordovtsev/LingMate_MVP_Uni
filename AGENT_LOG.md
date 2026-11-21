# Agent log

Newest entries at the top. Each scheduled run appends one entry: date, roadmap item, PR link, decisions made, open questions.

---

## 2026-11-21 — C.2 Placement + diagnosis, slice 1 (scheduled run)
- Branch `agent/placement` → PR into `agent/dev`. No open PRs, no comments; #18, #19 merged. docs/feedback: nothing new after 2026-11-16. Notion: no new entries since 19.11. Saturday of odd ISO week 47 → ordinary day. Roman's 20.11 note: C.2 before more units, never assume a level.
- `curriculum/es/placement.yaml`: 29 receptive items (A1 6, A2 9, B1 7, B2 7; gap-fill + "what does it mean"), 12 built from `docs/learner` (se me han olvidado, traje/dejé in the repair shop, ¿me pones…?, Perdone with an older woman, la calefacción, quitar la calefacción, que te vaya bien, espero que haga, aunque llueva, presuntamente, implicar al público); each item → error category (1.3 contract) and, when a unit exists, its grammar point. 4 production prompts A1–B2.
- `core/placement.py` (pure): staircase 4 items/level, +2 when 2/4, pass ≥ 3/4 (or ≥ 4/6) → up, fail → down, stop between passed and failed level; start = profile level (only a starting point). Diagnosis: gaps up to the next stage (morphosyntax §10), suggested-known units (below the placed level or all their grammar answered right; receptive ≠ production, sla §6 → only suggested), start unit = first open unit with a gap at/below the placed level, else the next open unit. Stored in `settings.placement` with answers and production texts; `apply_level` is explicit.
- API: `POST /api/placement/{lang}/next` (stateless, answer key never sent), `/finish`, `GET /api/placement/{user}`. UI: card «Тест уровня» (options + «Не знаю», production textareas, checkbox «Поставить уровень в профиль»).
- Tests: 232 → 264 (staircase finds every level from every start, beginner, borderline block, gap → unit 2, API keeps the profile level unless asked).
- Playwright: A2-like learner who misses *se me han olvidado* → 8 questions, A2, start «Что случилось сегодня», no console errors; phone width checked.
- Open for Roman: item wording/level placement (his judgement), the production answers are stored but not scored yet (needs LLM → next slice).

## 2026-11-19 — C.1 Curriculum map, slice 1 (scheduled run)
- Branch `agent/curriculum-a2` → PR into `agent/dev`. Open PR #18 (eval night fixes, Roman's session, no comments) — independent, not touched. docs/feedback: 2026-11-16 handled in #17/#18; nothing else new.
- `core/curriculum.py`: pydantic `Unit` (id `es-a2-topic`, level, order, RU/ES titles, 1–3 can-do lines with CEFR CV 2020 scale + level, PCIC refs by inventory + band + item name, grammar points with one RU form tip + error categories from the 1.3 contract, 3–8 chunks, vocabulary, situations = existing scenario ids / headings in `docs/learner/` / seeds for 4.3, culture note, prerequisites). Cross checks: unique ids/orders, prerequisites earlier and not higher level. `next_units(done, level)` = open units up to the learner's next stage (morphosyntax §10); `units_for_category` links the error log (1.6) to units for C.4.
- Content: 5 units A2→B1 built from Roman's Notion situations: *En el bar* (¿me pones…?, tú/usted), *¿Qué has hecho hoy?* (perfecto for today, se me ha olvidado), *Ayer dejé una mochila* (indefinido irregular, dejar/traer/llevar), *En casa* (gender -ción / floors, poner/quitar la calefacción), *¡Que te vaya bien!* (B1: que + subjuntivo, espero que, ojalá).
- PCIC: grammar/nociones pages are blocked for automated reading (robots.txt); only *Funciones* (3.8, 4.3, 5.17) verified → section numbers only there (`verified: true`), others cited by name; `curriculum/es/SOURCES.md` says what is checked.
- New dependency: PyYAML (small, pure-Python fallback; the roadmap asks for YAML units).
- API: `GET /api/curriculum/{lang}?done=&level=`, `GET /api/curriculum/{lang}/units/{id}`. No UI yet → checked with uvicorn + curl, not Playwright.
- Notion: 2 new entries 19.11 («allegedly» → presuntamente/supuestamente; «надеюсь» → espero que + subj.) → `docs/learner` + synthetic eval cases `syn-mood-4`, `syn-lexical-en-4` (37 → 39) + transfer rule `en_es.presumir` (presumir = to boast).
- Tests: 202 → 222.
- Open for Roman: unit order and choice (is this the right A2→B1 path?), PCIC grammar numbers.
## 2026-11-16 — docs/feedback/2026-11-16 (eval night 15.11) fixes (scheduled run)
- Branch `agent/eval-night-fixes` → PR into `agent/dev`. No open PRs, no comments; #16 and #17 merged. Feedback 2026-11-16 is the task of this run (before new features). Notion: no new entries since 15.11.
- **§5** the 17% false positives of gemini-3.1-flash-lite (with and without profile) are one case, `syn-clean-aproveche`: the model "adds" the `¡` that `¡Que aproveche!` already has (original `Que aproveche!` / `Que` → `¡Que`). New `core.feedback.is_phantom_correction`: the `corrected` span is in the learner's message and every occurrence of `original` sits inside it → correction dropped in `LLMService._finish` (chat, lesson and eval). Replayed on all 163 saved corrections in `eval/reports/`: drops exactly these 2, no real detection lost; gold pairs of all eval cases are never flagged.
- **§3** `scripts/pull_candidates.ps1`: downloads missing candidates (list read from `origin/agent/dev`), `Start-Process` (no NativeCommandError noise), output through `python -m eval.logfilter` (keeps status lines and one 100% line per layer) into `pull-<date>.log`. The nightly no longer pulls first: it evaluates installed candidates, logs `not installed yet`, and calls the pull script at the end (`-PullFirst` = old order).
- **§1** `-MaxHours 9`: no new model run starts after the budget, compare/hybrid still written. **§4** archive moves only untracked reports that `origin/agent/dev` already has; `eval.run --date` + `compare/hybrid --date` keep one date per night.
- Not run on Windows (no PowerShell in the cloud) — needs Roman's next Sunday run. §2 (pause slow models) was already done in #17.
- Tests: 202 → 212. No UI change → no Playwright pass.

## 2026-11-15 — 5.7 LanguageTool pre-check + Roman's scouting answers (scheduled run)
- Branch `agent/languagetool` → PR into `agent/dev`. No open PRs; PR #15 merged. docs/feedback/2026-11-14 handled: §1 and §4 already done by Roman/Claude on agent/dev; **§3** `aya-expanse:8b` added to `eval/model_candidates.txt` with «NC licence — comparison only, not for production»; **§2** LanguageTool (this PR).
- `core/checkers/languagetool.py`: `LanguageToolChecker` (httpx, `LANGUAGETOOL_URL`, default public API; waits 3.5 s between calls on the public API, local server no wait; ≤2000 chars, only the sentence + `language` + `motherTongue`); `classify` maps LT rule/category + changed words to our categories (accent/¿¡/typos → spelling_accent, el↔la / a la↔al → gender, ser↔estar, articles, prepositions, clitics, other grammar → agreement, false friends → lexical + transfer), drops style/typography/colloquialisms; `combine` = policy "fill" (LLM wins, LT fills).
- `eval.run`: `--provider languagetool` (alone) and `--precheck languagetool` (live hybrid; LT failure does not fail the case; report counts filled turns; file `…-lt`). `eval/hybrid.py`: LLM alone → hybrid table from one night's saved reports (no extra model calls) with spelling_accent / agreement / gender recall and FP guard. `eval.compare` keeps precheck runs apart. Nightly: one LT run after Gemini + `hybrid-<date>.md` at the end (`-NoLanguageTool` to skip).
- The public LT API is not reachable from the cloud (proxy 403): mapping checked against LT's documented response shape + a local fake server; real rule ids may need tuning after Monday's report.
- Notion: 2 new entries 15.11 («even if» → aunque + subjuntivo; «engage the audience» → implicar al público, comprometer false friend) → `docs/learner` + 2 synthetic eval cases (`syn-mood-3`, `syn-lexical-en-3`; eval set 35 → 37) + transfer rule `en_es.comprometer`.
- Tests: 177 → 202. No UI change → no Playwright pass; CLI run by hand against a fake LT server.

## 2026-11-14 — 5.7 Model scouting (scheduled run, Saturday of even ISO week 46)
- Branch `agent/model-scouting-2026-11-14` → PR into `agent/dev` «Модели: кандидаты на 14.11». No open PRs, no comments; PR #14 merged → 1.6 marked `[x]`. docs/feedback: nothing new.
- `docs/models/scouting-2026-11-14.md`: 09.11 reports reviewed (flash-lite 86% detection / 0.9 s is the reference; qwen2.5:7b 14% / 13 s → dropped; gemini-2.5-flash answered 6/34 on the free quota). Local candidates (≤ 6.1 GB, Apache 2.0): gemma4:e2b, gemma4:e4b-it-qat, qwen3.5:4b-q4_K_M, ministral-3:3b, granite4.1:3b, ministral-3:8b. Skipped: aya-expanse (CC-BY-NC), Salamandra (not in the Ollama library), over-size tags. Evidence: 2505.06004 (Gemma line best small GEC), 2609.10810 (minimal-edit + few-shot), La Leaderboard. Free no-card APIs for 5.8: Groq and GitHub Models look best; Gemini/Mistral free tiers use prompts for training. Hybrid designs (LanguageTool pre-check, local dialogue + cloud correction) written down, not built.
- Tags/sizes came from the `registry.ollama.ai` mirror (ollama.com is not reachable from the cloud); not pulled here.
- `core/llm/ollama_provider.py`: `OLLAMA_THINK` (auto → `think: false` for qwen3*/deepseek-r1/magistral, otherwise field not sent); exact tag match in `_ping` (family-only match made `gemma4:e2b` look installed when only `gemma4:e4b-it-qat` was).
- Notion: new 14.11 «¿Abajo?» in the lift (*Sí, a la cero.*) → `docs/learner` + eval case `roman-2026-11-14-lift` (gender, lexical) + transfer rule `ru_es.gender_numbers_floors` (al cero / a la primera, planta baja = RU 1st floor); 06.11 heating entry got a 14.11 addition (*poner / quitar la calefacción*).
- Tests: 161 → 177. No UI change → no Playwright pass.
- Open: held-out set (5.7) before any prompt tuning; Roman's choice on gemini-2.5-flash in the nightly and on LanguageTool.

## 2026-11-13 — 1.6 Error log as learner corpus (scheduled run)
- Branch `agent/error-log` → PR into `agent/dev`. No open PRs, no comments; PR #13 merged. docs/feedback: nothing new (2026-11-11 handled in #13).
- Storage: new `error_log` table (`user_id`, `error_category`, `created_at`, JSON payload; index on user+category), `SCHEMA_VERSION` 2 — additive, v1 databases get the table on start; `JsonStore` gets `error_log.json`; JSON→SQLite migration copies it. `add_error` / `get_errors` on both stores (parity test). One-time backfill: mistake lines written since 1.3 (`orig → corr — expl [category]`) are parsed into the log; pre-1.3 free text is skipped; `mistakes` untouched.
- `main.py`: chat + lesson log the full structured correction (category, cf_type, transfer source, message, mode, scenario) — not fallback replies. `GET /api/progress/{user}/errors?window_days=7`.
- `core/error_log.py` (pure): per-category counts, trend (last window vs previous: up/down/flat/new), transfer sources, examples; **persistent** (sla §5): ≥3 distinct days, span ≥7 days, seen in the last 14 days — or the same original→corrected form on ≥2 days; **possibly avoided** (sla §4): A2/B1 structures (perfecto, indefinido, imperfecto, clitics, future, subjuntivo, condicional) with no surface marker in the learner's messages; only after ≥30 messages and only up to the learner's next stage (morphosyntax §10). Markers err towards "used" (false alarms are worse than misses).
- UI: card «Над чем поработать» under the dashboard: top categories with count + trend, a friendly "повторяется — потренируем отдельно" line, ≤3 possibly avoided structures (engagement §3: no guilt).
- Notion: 5 new entries 13.11 (Kinder labels, backpack repair, la percha, fíjate, se me ha olvidado) → `docs/learner/roman-spanish.md`; no utterances of Roman's own → no eval cases (the *me olvidé el paraguas* error on the page is a candidate synthetic case).
- Tests: 147 → 161. Playwright: seeded DB (5 errors over 12 days + 32 messages), 2 messages from `es_roman.jsonl` via the rule fallback, card rendered, no console errors.
- Open: thresholds (3 days / 7 days / 30 messages) are a first guess — Roman's judgement after a couple of weeks of real use.

## 2026-11-12 — docs/feedback/2026-11-11: eval with a learner profile (scheduled run)
- Branch `agent/eval-profile` → PR into `agent/dev`. No open PRs, no comments; PR #12 merged. Feedback 2026-11-11 (§1–3) is the task of this run, before 1.6.
- **§1** `eval.run --profile <name|path>`: `eval/profiles/roman.json` (ru L1, en C1, es-ES A2, relocated, Vitoria-Gasteiz, no Italian) validated as `LearnerProfile` → settings with `onboarding_completed`, so prompts get `profile_context` + `prompt_hints` and corrections get `transfer_note`, exactly as in the app. Cases in another target language keep their own settings. Report: header line «Profile: roman / none», `meta.profile`, file name `…-<model>-roman.json` (no-profile file unchanged, both kept). Unknown profile → exit 2 listing the available ones.
- **§2** `scripts/nightly_eval.ps1`: `-Profiles @("", "roman")` — every model runs without and with the profile; at the end `eval.compare` writes `eval/reports/compare-<date>.md`. Not run on Windows here (no PowerShell in the cloud) — needs Roman's next nightly.
- **§3** `eval/compare.py`: pairs reports of one date by provider/model, table without → with (detection, category recall, text match, false positives, transfer source, `lexical` + `register` recall, answered) with ↑/↓ direction. Caveat in the table: the `en` hints name *línea*, so `roman-*` cases are partly taught to the test.
- Notion: new entry 12.11 «abrigo / abogado / aguacate» → `docs/learner/roman-spanish.md` (vocabulary, no utterance → no eval case; SRS with pictures, candidate RU false-friend rule).
- docs/feedback: 2026-11-11 handled (this PR). 1.5 marked `[x]`.
- Tests: 138 → 147. No UI changes → no Playwright pass; CLI run by hand with `--provider rule` with/without profile + `eval.compare`.

## 2026-11-11 — 1.5 Transfer maps (scheduled run)
- Branch `agent/transfer-maps` → PR into `agent/dev`. No open PRs, no comments; PR #11 merged. Notion: no new entries since 07.11. docs/feedback: nothing new. Roman's C.8 hosting decisions (commit 5065a78) read; not started this run (roadmap order: 1.5 first).
- `core/pedagogy/l1_maps/`: `TransferRule` (category, RU title, source/target example, note per L1, prompt hint, markers on accent-folded text, kind `negative` | `bridge`). Maps: `ru_es` (articles, ser/estar, gender -ma and mismatches, aspect, subjunctive, clitics, pensar en, meal verbs + bridge ты/вы → tú/usted), `en_es` (línea/cola, embarazada, actualmente, realizar, librería, double consonants, esforzarse por, depender de, pensar en, to be, calques — from Roman's real errors), `it_es` (burro, salire + bridges stare, articles, congiuntivo, imperfetto, clitics). Another pair = one module.
- Matching: word-marker rules first; category-level contrast only from the source the model flagged, or the L1 when nothing was flagged (no guessing "English" for an unflagged error); bridges from any known language. `is_transfer` stays the model's call.
- `LLMService._finish` adds `correction.transfer_note`; prompts get `prompt_hints` (≤3 per language, ≤7 lines) only for onboarded learners — legacy and eval prompts unchanged.
- UI: contrast line ("по-английски «stand in line» → la cola" + note) and "Подсказка" line under the correction (chat + lesson share `renderCorrection`).
- Tests: 116 → 138 (all 3 real Roman errors get a note). Playwright with a fake provider: 3 messages from eval cases, notes rendered, no console errors.
- Grounding: morphosyntax §7, sla §4, multilingual-education §1.

## 2026-11-10 — 1.4 Noticeable feedback: diff view (scheduled run)
- Branch `agent/correction-diff` → PR into `agent/dev`. No open PRs, no comments; PRs #8–#10 merged. Notion: no new entries since 07.11. docs/feedback: nothing new.
- `core/feedback.correction_diff(original, corrected)` → segments `equal/del/ins`. Words are aligned ignoring case and accents (so `Donde esta` → `¿Dónde está` marks only `¿`, `ó`, `á`); a word with the same stem is refined to letters (`cansado` → `cansada` marks `o`→`a`); different words are swapped whole (`la` → `el`, `Soy` → `Estoy`). Grounding: morphosyntax §2 (recasts of morphosyntax go unnoticed unless the changed morpheme is marked), §6 (textual enhancement).
- `LLMService._finish` adds `correction["diff"]` (empty for legacy string corrections); the progress log is unchanged (one text line).
- UI: correction block under the reply with struck red deletions, bold green insertions, full corrected sentence, category/transfer tags and explanation; legacy corrections keep the old text.
- Tests: 72 → 116 (diff reconstructs both sides on all 34 eval cases). Playwright: rule fallback + 3 mocked corrections, no console errors.
- Decision: 1.4 left `[~]` — the "consistently highlight target forms in bot replies over weeks" half of §6 needs the error log (1.6) to know the learner's target forms.

## 2026-11-09 (2) — C.8 step 1: hosting comparison (same scheduled run)
- Branch `agent/hosting-comparison` → PR #10 into `agent/dev` (docs only, independent of PR #9).
- `docs/hosting/comparison-2026-11-09.md`: Render+Neon, Hetzner VPS, Fly.io, Oracle Always Free, Render+Supabase, Koyeb — cost, card, sleep/cold start, EU, backups, code changes, ops. Facts from vendor docs + 2026 third-party write-ups (some pages blocked: Fly docs, Render regions — marked as unverified).
- Recommendation: €0 start = Render free web + Neon free Postgres (Frankfurt) + own nightly export (needs a `PostgresStore`); always-on ≈€3–8/month = Hetzner/Fly + SQLite as is. Not: Oracle (idle reclaim, 2026 cut), Supabase (weekly pause), Render Postgres (deleted after 30 days).
- C.8 marked `[?]`: 4 questions for Roman in the doc.

## 2026-11-09 — Daily-quota stop for eval + app (scheduled run)
- Branch `agent/eval-quota-stop` → PR #9 into `agent/dev`. Open PR #8 (Roman's nightly reports, no comments) read: its finding 2 (gemini-2.5-flash: 20 req/day free tier, then 28 cases × ~51 s of useless retries) handled here.
- `core/llm_service.quota_pause_s()`: a 429 whose RetryInfo/`retry in …` is > 5 min, or a per-day quota, is not retried; the provider is skipped until the reset time (default 1 h). Short per-minute 429s and 503s keep the old backoff. In the app: no wasted call per message once the daily quota is gone (next provider in the chain / fallback).
- `eval.run`: after a per-day quota the remaining cases are marked `skipped` (provider failures, not scored), summary `quota_stopped`, Markdown says "Stopped early".
- Not done (later, needs live check): PR #8 finding 3 (all models miss `register` + `lexical`) → prompt examples; PowerShell `NativeCommandError` noise in `nightly_eval.ps1`.
- Notion: no new entries since 07.11. docs/feedback: nothing new.
- Tests: 69 → 72. No UI changes → no Playwright pass; CLI run by hand with `--provider rule`.

## 2026-11-08 — docs/feedback/2026-11-08 (first local eval) fixes (scheduled run)
- Branch `agent/eval-fixes` → PR #7 into `agent/dev`. 1.3a marked `[x]` (PR #6 merged). No open PRs, no comments.
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
