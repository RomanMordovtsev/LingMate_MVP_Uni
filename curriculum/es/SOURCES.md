# Curriculum es-ES: sources and how references are checked

Units: `units/*.yaml` (shape and validation in `core/curriculum.py`, roadmap C.1).

## Plan Curricular del Instituto Cervantes (PCIC)
- Online: https://cvc.cervantes.es/ensenanza/biblioteca_ele/plan_curricular/ (inventories by band A1-A2, B1-B2, C1-C2).
- Every unit cites PCIC items by **inventory + band + item name**. A **section number** is written only with `verified: true`, i.e. after it was checked on the PCIC page itself. Unchecked numbers are never guessed.
- Checked 2026-11-19 on *5. Funciones. Introducción* (`05_funciones_introduccion.htm`):
  - 3.8 *Expresar deseos*: A1 *Quiero + SN / inf.*, B1 *Quiero que + pres. subj.*
  - 4.3 *Pedir objetos*: A2 (*¿Me traes + SN?*)
  - 5.17 *Formular buenos deseos*: A2 *¡Que aproveche!* as a fixed formula; the generative *que + presente de subjuntivo* only at B1, when the present subjunctive is introduced.
- Not checked yet (the grammar and nociones inventory pages refuse automated reading): section numbers in *Gramática*, *Nociones generales*, *Nociones específicas*, *Saberes y comportamientos socioculturales*. Item names in the units follow the PCIC wording as far as known; **Roman, if you open the PCIC pages, add the numbers and set `verified: true`.**

## CEFR Companion Volume (2020)
- `can_do` lines are short Russian paraphrases of the illustrative descriptors; `cefr_scale` is the CV scale name, `cefr_level` its level. Not official translations.

## Roman's real situations
- `situations.learner` = heading prefixes in `docs/learner/roman-spanish.md` (tests check they exist). Units are chosen from what Roman actually needed (syllabus-design §1: backward design from real needs).
