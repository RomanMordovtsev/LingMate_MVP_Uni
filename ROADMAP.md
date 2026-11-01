# LingMate Roadmap

## Vision
LingMate is an AI language-learning companion for adults who want to **actually use** a language: people who have moved abroad, are planning a move, travel, work with the language, or simply love it. Practice is built around real-life tasks from the learner's own life, grounded in SLA research, and designed to become a daily habit. Yuji (the mascot, `static/yuji-lingmate.png`) is the face of the app and stays.

**Reference user (dogfooding):** Roman — Russian L1, English C1, Italian A1, Spanish A2 → B1/B2, living in Vitoria-Gasteiz (Spain), LAMS master's student. Spanish (es-ES) for a relocated learner is the first fully polished path. Design every data model and scenario so other languages, places and goals plug in later without rewrites (profile-driven, template-based), but don't spend runs building content for other user types before Roman's path works end to end.

Pedagogy: `docs/research/` (morphosyntax.md, sla.md, syllabus-design.md, engagement.md). Cite sections in PRs.

## Rules for the roadmap
- Work top to bottom. One item (or a coherent slice of one) per agent run.
- Mark items `[x]` when merged into `agent/dev`, `[~]` when in progress, `[?]` when waiting for Roman's decision.
- Roman may reorder or add items at any time. His edits win.

## Phase 1 — Foundations
- [ ] **1.1 SQLite storage.** Replace JSON files with SQLite (keep the `JsonStore` interface; migration script for existing data). Needed for profiles, error tracking and spaced repetition.
- [ ] **1.2 Learner profile + onboarding.** Profile: all languages with levels (L1 + others), target language/variant, goal (`relocated` | `planning_move` | `travel` | `work` | `study` | `partner_family` | `hobby`), place (country/city, optional), interests, daily-goal minutes, preferred feedback timing. Short onboarding flow in the UI (Russian labels), including the "who do you want to be in this language" question. (sla §1, syllabus-design §1)
- [ ] **1.3 Structured corrective feedback.** LLM JSON contract: `correction` → object with `original`, `corrected`, `error_category` (article, gender, agreement, ser_estar, tense_aspect, mood, preposition, clitic, word_order, lexical, spelling_accent), `cf_type` (recast | explicit | metalinguistic | elicitation | clarification), `is_transfer` + `transfer_source` language, `explanation` (short, learner's L1). Backward compatible frontend. (morphosyntax §2, §7; sla §4)
- [ ] **1.4 Noticeable feedback in the UI.** Highlight changed morphemes (diff view) in corrections. (morphosyntax §2, §6)
- [ ] **1.5 Transfer maps.** `core/pedagogy/l1_maps/` with `ru_es.py` first (articles, ser/estar, gender mismatches, preterite/imperfect, subjunctive, clitics) and an interface for other pairs; may reference other known languages (IT↔ES). (morphosyntax §7, sla §4)
- [ ] **1.6 Error log as learner corpus.** Store each structured correction; `/api/progress/{user}/errors` with per-category counts, trends, and *persistent* errors (fossilization risk) and avoided structures. (morphosyntax §10, sla §5)

## Phase 2 — Daily habit and Yuji
- [ ] **2.1 Daily goal + forgiving streak.** Learner-set daily goal; streak with automatic rest days (or weekly streak option); totals never reset. (engagement §1–2)
- [ ] **2.2 Session shape + home screen.** Warm-up review → main task → wrap-up (1 highlight, 1 thing to remember) → teaser. Home screen shows today's plan, streak, next real-life task. (engagement §6)
- [ ] **2.3 Yuji reactions.** Mascot states (greeting, thinking, celebrating, encouraging) and short messages tied to effort and milestones; occasional "how languages are learned" facts from the readings. Never guilt-tripping. Reuse the existing Yuji art; ask Roman before generating new art. (engagement §3, sla §2)
- [ ] **2.4 Reminders.** [?] needs a decision on delivery (browser notifications / PWA / email / Telegram bot). Agent: draft options with pros/cons in the PR, don't implement until Roman chooses.

## Phase 3 — Adaptive practice
- [ ] **3.1 Spaced repetition** (SM-2 or FSRS-lite) for vocabulary, chunks and recurrent error categories; daily review queue feeds the warm-up.
- [ ] **3.2 Feedback policy engine.** Pure, unit-tested module choosing CF type per error: prompts for forms the learner has produced correctly before; explicit/metalinguistic for new, transfer or persistent errors; ignore errors beyond current stage; graded hints. (morphosyntax §2, §10; syllabus-design §5–6; sla §5)
- [ ] **3.3 Pre-task focus-on-form tip** from the learner's most frequent relevant error category. (morphosyntax §5)
- [ ] **3.4 Scenario repetition scheduling** with varied details. (morphosyntax §5)
- [ ] **3.5 "¿Cómo se dice…?" / L1 word drop-in** inside the chat. (morphosyntax §8–9)

## Phase 4 — Real-life tasks
- [ ] **4.1 Task cycle.** Every scenario = pre-task (goal, key chunks, form tip) → task (dialogue with explicit non-linguistic `outcome`, checked by the model) → post-task (feedback summary, items to review). (syllabus-design §3, morphosyntax §4)
- [ ] **4.2 Scenario templates.** Scenarios defined as templates with variables (country, city, institution names, currency, register tú/usted, regional variant) + CEFR descriptors + complexity level. Migrate existing 4×6 scenarios to the format. (syllabus-design §1–3, §8)
- [ ] **4.3 Relocation pack, seeded for Spain / Vitoria-Gasteiz (es-ES).** Bank appointment, empadronamiento, renting / talking to a landlord, doctor (centro de salud), university secretariat, bar de pintxos, train/bus tickets, phone/SIM shop. Same templates must work for "planning to move" (calls/emails from abroad) and for other countries later. B1-oriented.
- [ ] **4.4 Information-gap scenarios.** Bot holds hidden facts the learner must elicit. (morphosyntax §3)
- [ ] **4.5 Mini-projects.** Multi-day sequences with a final product (email to landlord, trip plan, voice message). (syllabus-design §7)
- [ ] **4.6 Content mode (CLIL-style)** for hobby learners: discuss short texts on the learner's interests. (syllabus-design §7)
- [ ] **4.7 Collaborative writing / dictogloss mode.** (morphosyntax §1, §6)

## Phase 5 — Measuring progress
- [ ] **5.1 CEFR can-do tracker** (CEFR CV 2020 descriptors) with evidence from completed tasks. (syllabus-design §8, sla §3)
- [ ] **5.2 Weekly progress report + reflection prompt** (accuracy per category, words retained, tasks done, "what was hard / what next"). (sla §8)
- [ ] **5.3 Evaluation harness** for correction quality (fixed learner utterances with known errors; precision/recall per category) to compare prompts/models objectively.
- [ ] **5.4 Engagement metrics** (D1/D7/D30, sessions/week) reported next to learning metrics. (engagement §9)

## Later / ideas (need Roman's approval before starting)
- Pronunciation feedback (after Phonetics course material), Basque mini-module, PWA/mobile, deploy to a free host, multi-user auth, more target languages polished to Spanish's level.

## Waiting for input
- Material from Multilingual Education and Phonetics → new files in `docs/research/`.
