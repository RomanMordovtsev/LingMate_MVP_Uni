# Eval 2026-11-09 — ollama / qwen2.5:7b-instruct

Cases: 34, answered: 34 (28 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 14% |
| Category recall | 7% |
| Category precision | 50% |
| Corrected text matches gold | 7% |
| False positives on correct input | 0% |
| Transfer source right | 9% |
| Transfer flagged (gold transfer, detected) | 33% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 14.536 / 13.258 / 29.512 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | — | 0% | 0 | 0 | 3 |
| article | — | 0% | 0 | 0 | 3 |
| clitic | — | 0% | 0 | 0 | 2 |
| gender | — | 0% | 0 | 0 | 3 |
| lexical | — | 0% | 0 | 0 | 5 |
| mood | — | 0% | 0 | 0 | 2 |
| preposition | — | 0% | 0 | 0 | 3 |
| register | — | 0% | 0 | 0 | 3 |
| ser_estar | 33% | 50% | 1 | 2 | 1 |
| spelling_accent | 100% | 33% | 1 | 0 | 2 |
| tense_aspect | — | 0% | 0 | 0 | 2 |
| word_order | — | 0% | 0 | 0 | 3 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: no correction
- `roman-2026-10-queue` gold ['lexical']: no correction
- `syn-article-1` gold ['article', 'gender']: no correction
- `syn-article-2` gold ['article']: no correction
- `syn-gender-1` gold ['gender']: no correction
- `syn-gender-2` gold ['gender']: no correction
- `syn-agreement-1` gold ['agreement']: no correction
- `syn-agreement-2` gold ['agreement', 'article']: no correction
- `syn-serestar-1` gold ['ser_estar']: Soy cansado después de clase. → Me siento cansado después de clase. [ser_estar]
- `syn-serestar-2` gold ['ser_estar']: no correction
- `syn-tense-1` gold ['tense_aspect']: no correction
- `syn-tense-2` gold ['tense_aspect']: no correction
- `syn-mood-1` gold ['mood']: no correction
- `syn-mood-2` gold ['mood']: te llamaré → me llamaré [ser_estar]
- `syn-prep-1` gold ['preposition']: no correction
- `syn-prep-2` gold ['preposition']: no correction
- `syn-clitic-1` gold ['clitic', 'word_order']: no correction
- `syn-clitic-2` gold ['clitic']: no correction
- `syn-order-1` gold ['word_order']: ¿Dónde la parada está? → ¿Dónde está la parada? [ser_estar]
- `syn-order-2` gold ['word_order', 'agreement']: no correction
- `syn-lexical-1` gold ['lexical', 'preposition']: no correction
- `syn-lexical-2` gold ['lexical']: no correction
- `syn-lexical-3` gold ['lexical']: no correction
- `syn-accent-1` gold ['spelling_accent']: no correction
- `syn-accent-2` gold ['spelling_accent']: no correction
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: no correction
