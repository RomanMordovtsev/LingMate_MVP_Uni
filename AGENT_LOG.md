# Agent log

Newest entries at the top. Each scheduled run appends one entry: date, roadmap item, PR link, decisions made, open questions.

---

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
