# Eval 2026-11-22 — ollama / gemma4:e2b — profile roman

Profile: **roman** (prompts include the profile context and transfer hints; 39/39 cases match its target language).

Cases: 39, answered: 39 (33 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 48% |
| Category recall | 33% |
| Category precision | 69% |
| Corrected text matches gold | 27% |
| False positives on correct input | 0% |
| Transfer source right | 23% |
| Transfer flagged (gold transfer, detected) | 80% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 32.043 / 31.211 / 48.89 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 100% | 67% | 2 | 0 | 1 |
| article | 100% | 100% | 2 | 0 | 0 |
| clitic | — | 0% | 0 | 0 | 1 |
| gender | 50% | 33% | 1 | 1 | 2 |
| lexical | 33% | 12% | 1 | 2 | 7 |
| mood | — | 0% | 0 | 0 | 4 |
| preposition | — | 0% | 0 | 0 | 4 |
| register | 100% | 33% | 1 | 0 | 2 |
| ser_estar | — | 0% | 0 | 0 | 2 |
| spelling_accent | 100% | 67% | 2 | 0 | 1 |
| tense_aspect | 100% | 50% | 1 | 0 | 1 |
| word_order | 33% | 33% | 1 | 2 | 2 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: no correction
- `roman-2026-10-queue` gold ['lexical']: no correction
- `roman-2026-10-compliment` gold ['preposition', 'spelling_accent']: lo más possible → lo más posible [lexical]
- `roman-2026-11-14-lift` gold ['gender', 'lexical']: no correction
- `syn-article-2` gold ['article']: Busco piso cerca de universidad. → Busco un piso cerca de la universidad. [article]
- `syn-gender-1` gold ['gender']: no correction
- `syn-serestar-1` gold ['ser_estar']: no correction
- `syn-serestar-2` gold ['ser_estar']: no correction
- `syn-tense-2` gold ['tense_aspect']: no correction
- `syn-mood-1` gold ['mood']: no correction
- `syn-mood-2` gold ['mood']: no correction
- `syn-prep-1` gold ['preposition']: no correction
- `syn-prep-2` gold ['preposition']: Pienso de mudarme a otro piso. → Estoy pensando en mudarme a otro piso. [word_order]
- `syn-clitic-1` gold ['clitic', 'word_order']: encendí la ayer → encendí la calefacción ayer [word_order]
- `syn-clitic-2` gold ['clitic']: A mi hermana gusta la música → A mi hermana le gusta la música [word_order]
- `syn-order-1` gold ['word_order']: no correction
- `syn-order-2` gold ['word_order', 'agreement']: no correction
- `syn-lexical-1` gold ['lexical', 'preposition']: no correction
- `syn-lexical-2` gold ['lexical']: Estoy embarazado → Estoy embarazada [gender]
- `syn-lexical-3` gold ['lexical']: ¿Me deja pasar a la ventana? → ¿Puedo pasar a la ventana? [lexical]
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: dámelo → dame/me puede dar [register]
- `syn-mood-3` gold ['mood']: incluso si haga cero grados fuera → incluso si hace cero grados afuera [lexical]
- `syn-lexical-en-3` gold ['lexical']: no correction
- `syn-mood-4` gold ['mood']: no correction
- `syn-lexical-en-4` gold ['lexical']: no correction
