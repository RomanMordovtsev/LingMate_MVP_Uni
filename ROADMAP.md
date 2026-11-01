# LingMate Roadmap

## North star
Roman (Russian L1, English C1, Spanish A2, living in Vitoria-Gasteiz) learns Spanish to B1 → B2 **through LingMate itself**.
Every feature is judged by one question: *does this make Roman's daily Spanish practice more effective?*
Pedagogy comes from SLA research covered in Roman's LAMS master's — see `docs/research/`.

## Rules for the roadmap
- Work top to bottom. One item (or a coherent slice of one) per agent run.
- Mark items `[x]` when merged into `agent/dev`, `[~]` when in progress, `[?]` when waiting for Roman's decision.
- Roman may reorder or add items at any time. His edits win.

## Phase 1 — Foundations for a real learner (Spanish first)
- [ ] **1.1 SQLite storage.** Replace JSON files with SQLite (keep `JsonStore` interface; migration script for existing data). Needed for per-form error tracking and spaced repetition.
- [ ] **1.2 Structured corrective feedback.** Extend the LLM JSON contract: `correction` → object with `original`, `corrected`, `error_category` (article, gender, agreement, ser_estar, tense_aspect, mood, preposition, clitic, word_order, lexical, spelling_accent), `cf_type` (recast | explicit | metalinguistic | elicitation | clarification), `is_l1_transfer`, `explanation_ru` (optional, short). Keep backward compatibility in the frontend. (Research §2, §7)
- [ ] **1.3 Noticeable feedback in the UI.** Highlight the changed morphemes in corrections (diff view). (Research §2, §6)
- [ ] **1.4 Russian→Spanish difficulty map.** `core/pedagogy/l1_maps/ru_es.py`: known transfer areas with short RU-vs-ES contrast explanations used by prompts. (Research §7)
- [ ] **1.5 Error log as learner corpus.** Store every structured correction with timestamp and category; endpoint `/api/progress/{user}/errors` with per-category counts and trend. (Research §10)

## Phase 2 — Adaptive practice
- [ ] **2.1 Spaced repetition for vocabulary and recurrent errors.** SM-2 or FSRS-lite over vocab items and error categories. Daily review queue.
- [ ] **2.2 Feedback policy engine.** Choose CF type per error: prompts for forms the learner has produced correctly before (performance error), explicit/metalinguistic for new or transfer errors, ignore errors beyond current stage. Make it a pure, unit-tested Python module. (Research §2, §10)
- [ ] **2.3 Pre-task focus-on-form tip.** Before a scenario, show a 1–2 line tip on the learner's most frequent error category relevant to that scenario. (Research §5)
- [ ] **2.4 Scenario repetition scheduling.** Re-offer completed scenarios after N days with varied details. (Research §5)
- [ ] **2.5 "¿Cómo se dice…?" / L1 word drop-in.** Learner can write a Russian word inside a Spanish sentence or ask how to say something; bot answers inline and logs the word. (Research §8, §9)

## Phase 3 — Real-life tasks (Vitoria-Gasteiz)
- [ ] **3.1 Task outcomes.** Each scenario gets an explicit non-linguistic outcome checked by the model (`outcome_achieved`). (Research §4)
- [ ] **3.2 Information-gap scenarios.** Bot holds hidden facts the learner must elicit. (Research §3)
- [ ] **3.3 Spain/Vitoria scenario pack (es-ES).** Bank appointment, empadronamiento at the ayuntamiento, renting a room / talking to the landlord, doctor (Osakidetza), university secretariat, ordering at a bar de pintxos, buying a train ticket (Renfe/Alsa), phone/SIM shop. B1-oriented.
- [ ] **3.4 Collaborative writing / dictogloss mode.** Bot reads (TTS) a short text twice, learner reconstructs it, bot discusses differences. (Research §1, §6)

## Phase 4 — Measuring progress
- [ ] **4.1 CEFR can-do tracker** for Spanish A2→B2 with evidence from completed tasks.
- [ ] **4.2 Weekly progress report** (accuracy per error category, new vocab retained, tasks completed).
- [ ] **4.3 Evaluation harness.** Fixed set of learner utterances with known errors; script that scores the model's corrections (precision/recall per category) so prompt changes can be compared objectively.

## Later / ideas (need Roman's approval before starting)
- Pronunciation feedback (Phonetics course material), Basque mini-module, mobile-friendly PWA, deploy to a free host, multi-user auth.

## Waiting for input
- More course material (SLA, Syllabus Design, Multilingual Education, Phonetics) → new files in `docs/research/`.
