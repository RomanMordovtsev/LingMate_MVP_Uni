# Eval 2026-11-15 — ollama / gemma4:e2b — profile roman

Profile: **roman** (prompts include the profile context and transfer hints; 35/35 cases match its target language).

Cases: 35, answered: 35 (29 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 55% |
| Category recall | 38% |
| Category precision | 69% |
| Corrected text matches gold | 45% |
| False positives on correct input | 0% |
| Transfer source right | 18% |
| Transfer flagged (gold transfer, detected) | 50% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 31.667 / 31.475 / 46.662 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 100% | 67% | 2 | 0 | 1 |
| article | 100% | 50% | 1 | 0 | 1 |
| clitic | — | 0% | 0 | 0 | 1 |
| gender | 50% | 33% | 1 | 1 | 2 |
| lexical | 33% | 17% | 1 | 2 | 5 |
| mood | — | 0% | 0 | 0 | 2 |
| preposition | 100% | 25% | 1 | 0 | 3 |
| register | — | 0% | 0 | 0 | 3 |
| ser_estar | 50% | 50% | 1 | 1 | 1 |
| spelling_accent | 100% | 33% | 1 | 0 | 2 |
| tense_aspect | 100% | 50% | 1 | 0 | 1 |
| word_order | 67% | 67% | 2 | 1 | 1 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: no correction
- `roman-2026-10-queue` gold ['lexical']: no correction
- `roman-2026-10-compliment` gold ['preposition', 'spelling_accent']: lo más possible → lo más posible [lexical]
- `roman-2026-11-14-lift` gold ['gender', 'lexical']: a la cero → desde cero [lexical]
- `syn-article-1` gold ['article', 'gender']: no correction
- `syn-gender-1` gold ['gender']: no correction
- `syn-serestar-2` gold ['ser_estar']: no correction
- `syn-tense-2` gold ['tense_aspect']: no correction
- `syn-mood-1` gold ['mood']: no correction
- `syn-mood-2` gold ['mood']: no correction
- `syn-prep-1` gold ['preposition']: Esta noche ceno con pasta. → Esta noche voy a cenar pasta. [lexical]
- `syn-clitic-2` gold ['clitic']: A mi hermana gusta la música → A mi hermana le gusta la música [ser_estar]
- `syn-order-2` gold ['word_order', 'agreement']: no correction
- `syn-lexical-1` gold ['lexical', 'preposition']: no correction
- `syn-lexical-2` gold ['lexical']: Estoy embarazado → Estoy embarazada [gender]
- `syn-lexical-3` gold ['lexical']: no correction
- `syn-accent-2` gold ['spelling_accent']: Donde esta la estacion de autobuses? → ¿Dónde está la estación de autobuses? [word_order]
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: no correction
