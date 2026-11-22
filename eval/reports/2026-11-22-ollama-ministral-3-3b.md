# Eval 2026-11-22 — ollama / ministral-3:3b

Profile: none (legacy prompts, no profile context or transfer hints).

Cases: 39, answered: 39 (33 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 42% |
| Category recall | 9% |
| Category precision | 21% |
| Corrected text matches gold | 12% |
| False positives on correct input | 17% |
| Transfer source right | 0% |
| Transfer flagged (gold transfer, detected) | 12% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 14.147 / 12.726 / 32.08 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 50% | 67% | 2 | 2 | 1 |
| article | — | 0% | 0 | 0 | 2 |
| clitic | — | 0% | 0 | 0 | 2 |
| gender | — | 0% | 0 | 0 | 4 |
| lexical | 0% | 0% | 0 | 1 | 8 |
| mood | 0% | 0% | 0 | 1 | 4 |
| preposition | 33% | 25% | 1 | 2 | 3 |
| register | — | 0% | 0 | 0 | 3 |
| ser_estar | — | 0% | 0 | 0 | 2 |
| spelling_accent | 0% | 0% | 0 | 3 | 3 |
| tense_aspect | — | 0% | 0 | 0 | 2 |
| word_order | 0% | 0% | 0 | 2 | 3 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: puedo → puedes [agreement]
- `roman-2026-10-queue` gold ['lexical']: no correction
- `roman-2026-10-compliment` gold ['preposition', 'spelling_accent']: possible → más [lexical]
- `roman-2026-11-14-lift` gold ['gender', 'lexical']: no correction
- `syn-article-1` gold ['article', 'gender']: no correction
- `syn-article-2` gold ['article']: Busco piso cerca de universidad. → Busco piso **cerca de** la universidad. [preposition]
- `syn-gender-1` gold ['gender']: no correction
- `syn-gender-2` gold ['gender']: no correction
- `syn-serestar-1` gold ['ser_estar']: cansado → cansado [spelling_accent]
- `syn-serestar-2` gold ['ser_estar']: en el centro → en el corazón [preposition]
- `syn-tense-1` gold ['tense_aspect']: no correction
- `syn-tense-2` gold ['tense_aspect']: no correction
- `syn-mood-1` gold ['mood']: no correction
- `syn-mood-2` gold ['mood']: no correction
- `syn-prep-1` gold ['preposition']: pasta → pasta **al** carbonara/pasta con *salsa* de tomate [word_order]
- `syn-prep-2` gold ['preposition']: de → a [preposition]
- `syn-clitic-1` gold ['clitic', 'word_order']: ayer → ayer [spelling_accent]
- `syn-clitic-2` gold ['clitic']: no correction
- `syn-order-1` gold ['word_order']: no correction
- `syn-order-2` gold ['word_order', 'agreement']: un muy bueno profesor → un *buen* profesor [None]
- `syn-lexical-1` gold ['lexical', 'preposition']: no correction
- `syn-lexical-2` gold ['lexical']: embarazado → te sientes culpable [mood]
- `syn-lexical-3` gold ['lexical']: no correction
- `syn-accent-1` gold ['spelling_accent']: no correction
- `syn-accent-2` gold ['spelling_accent']: no correction
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: no correction
- `syn-clean-porfa` gold none: porfa → por favor [spelling_accent]
- `syn-mood-3` gold ['mood']: no correction
- `syn-lexical-en-3` gold ['lexical']: no correction
- `syn-mood-4` gold ['mood']: sale → vaya [word_order]
- `syn-lexical-en-4` gold ['lexical']: no → hay [agreement]
