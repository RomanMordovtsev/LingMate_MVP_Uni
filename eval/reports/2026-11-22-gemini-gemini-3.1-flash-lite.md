# Eval 2026-11-22 — gemini / gemini-3.1-flash-lite

Profile: none (legacy prompts, no profile context or transfer hints).

Cases: 39, answered: 39 (33 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 91% |
| Category recall | 85% |
| Category precision | 93% |
| Corrected text matches gold | 70% |
| False positives on correct input | 0% |
| Transfer source right | 46% |
| Transfer flagged (gold transfer, detected) | 92% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 6.477 / 2.761 / 38.851 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 100% | 100% | 2 | 0 | 0 |
| article | 100% | 100% | 1 | 0 | 0 |
| clitic | 100% | 100% | 1 | 0 | 0 |
| gender | 100% | 100% | 3 | 0 | 0 |
| lexical | 100% | 62% | 5 | 0 | 3 |
| mood | 100% | 100% | 4 | 0 | 0 |
| preposition | 60% | 100% | 3 | 2 | 0 |
| register | 100% | 33% | 1 | 0 | 2 |
| ser_estar | 100% | 100% | 2 | 0 | 0 |
| spelling_accent | 100% | 100% | 2 | 0 | 0 |
| tense_aspect | 100% | 50% | 1 | 0 | 1 |
| word_order | 100% | 100% | 3 | 0 | 0 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: no correction
- `roman-2026-10-queue` gold ['lexical']: en la línea → en la cola / al teléfono [lexical]
- `roman-2026-11-14-lift` gold ['gender', 'lexical']: a la cero → a las doce [lexical]
- `syn-article-1` gold ['article', 'gender']: la máster → el máster [gender]
- `syn-tense-2` gold ['tense_aspect']: no correction
- `syn-lexical-3` gold ['lexical']: a la ventana → por la ventana [preposition]
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: dámelo → por favor, ¿podría dármelo? [register]
- `syn-lexical-en-3` gold ['lexical']: comprometer → conectar con [lexical]
- `syn-lexical-en-4` gold ['lexical']: presume → presume de [preposition]
