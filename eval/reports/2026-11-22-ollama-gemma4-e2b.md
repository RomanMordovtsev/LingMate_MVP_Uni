# Eval 2026-11-22 — ollama / gemma4:e2b

Profile: none (legacy prompts, no profile context or transfer hints).

Cases: 39, answered: 39 (33 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 33% |
| Category recall | 24% |
| Category precision | 67% |
| Corrected text matches gold | 27% |
| False positives on correct input | 17% |
| Transfer source right | 23% |
| Transfer flagged (gold transfer, detected) | 100% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 24.659 / 24.438 / 34.984 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 67% | 67% | 2 | 1 | 1 |
| article | 100% | 50% | 1 | 0 | 1 |
| clitic | — | 0% | 0 | 0 | 1 |
| gender | 50% | 25% | 1 | 1 | 3 |
| lexical | 0% | 0% | 0 | 1 | 8 |
| mood | — | 0% | 0 | 0 | 4 |
| preposition | 100% | 25% | 1 | 0 | 3 |
| register | — | 0% | 0 | 0 | 3 |
| ser_estar | — | 0% | 0 | 0 | 2 |
| spelling_accent | 100% | 33% | 1 | 0 | 2 |
| tense_aspect | 100% | 50% | 1 | 0 | 1 |
| word_order | 50% | 33% | 1 | 1 | 2 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: no correction
- `roman-2026-10-queue` gold ['lexical']: no correction
- `roman-2026-10-compliment` gold ['preposition', 'spelling_accent']: lo más possible → lo más posible [lexical]
- `roman-2026-11-14-lift` gold ['gender', 'lexical']: no correction
- `syn-article-1` gold ['article', 'gender']: no correction
- `syn-gender-1` gold ['gender']: no correction
- `syn-serestar-1` gold ['ser_estar']: no correction
- `syn-serestar-2` gold ['ser_estar']: no correction
- `syn-tense-2` gold ['tense_aspect']: no correction
- `syn-mood-1` gold ['mood']: no correction
- `syn-mood-2` gold ['mood']: no correction
- `syn-prep-1` gold ['preposition']: no correction
- `syn-prep-2` gold ['preposition']: Pienso de mudarme a otro piso. → Estoy pensando en mudarme a otro piso. [preposition]
- `syn-clitic-2` gold ['clitic']: A mi hermana gusta la música → A mi hermana le gusta la música [agreement]
- `syn-order-1` gold ['word_order']: no correction
- `syn-order-2` gold ['word_order', 'agreement']: no correction
- `syn-lexical-1` gold ['lexical', 'preposition']: no correction
- `syn-lexical-2` gold ['lexical']: Estoy embarazado → Estoy embarazada [gender]
- `syn-lexical-3` gold ['lexical']: no correction
- `syn-accent-2` gold ['spelling_accent']: no correction
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: no correction
- `syn-clean-cola` gold none: ¿quién es el último? → ¿Quién es el último de la fila? [word_order]
- `syn-mood-3` gold ['mood']: no correction
- `syn-lexical-en-3` gold ['lexical']: no correction
- `syn-mood-4` gold ['mood']: no correction
- `syn-lexical-en-4` gold ['lexical']: no correction
