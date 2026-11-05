# Roman's manual test, 05.11.2026 (PR #2, learner profile)

Setup: Windows, fresh clone of `agent/learner-profile`, `.env` with `GEMINI_MODEL=gemini-flash-lite-latest`; Gemini returned **503 UNAVAILABLE (high demand)**, the chain fell back to the next provider. Profile: es-ES A2, RU native, EN C1, relocated, Vitoria-Gasteiz, interests: anime, music, series, food.

## Works (Roman: "выглядит круто")
- Onboarding card, validation, saving; F5 keeps the profile; «Мой профиль» reopens it filled. Scenario list switches to Spanish.
- Profile reaches the prompt: replies mention Vitoria and Basque food.

## Problems → turn into fixes / roadmap work (cite this file)
1. **Gemini unreliable (Roman wants to change it).** Frequent 503 on `gemini-flash-lite-latest`. Do: retry once with short backoff on 503/429 before falling back; log and show which provider/model answered (small label under the reply, dev/debug setting) so Roman knows what he is testing; prioritise 1.3a + 5.6 to choose a better default. Don't hard-code a new model without the comparison.
2. **Missed transfer error.** «No estoy en la línea.» was not corrected (should be *cola*, EN *line* transfer). The reply went off-topic («¿algo relacionado con la culinaria?»). → 1.3 structured CF + eval case already exists (`roman-2026-10-queue`).
3. **Weak coherence in free talk.** Replies ignore what the learner said and repeat themselves («Estudiar en Vitoria es…» twice). Factual error: «el pintxo, es un bocadillo tradicional» (a pintxo is a small snack, often on bread; not a bocadillo). Vocab list had a typo «eforzar» (should be *esforzarse (por/en)*). Correction of *esforzarse por / posible* was right.
4. **Lesson feedback attached to the wrong turn.** In «Cafetería en Madrid», the feedback about *aquí* was repeated on the next learner turn («De normal»), and «está» (no accent in «esta bien») was missed. Feedback must refer only to the current learner message. → 1.3.
5. **Over-prescriptive register.** It told him to say *por favor* instead of *porfa* "en un contexto formal" — in a Spanish café *porfa* is fine. Register advice should match the scenario (sla / syllabus-design §8; learner profile: relocated, everyday use).
6. **Role-play logic.** Learner ordered «un café»; bot asked what milk for «el café con leche». Missed a natural chance to teach *entera / semidesnatada / desnatada / de avena*. → 4.1 task cycle (key chunks).
7. **Scenarios should use the learner's place.** «Cafetería en Madrid» for someone in Vitoria (and the bot offered a pintxo, which is Basque). → 4.2 templates with `{city}`; Roman explicitly asked for this.
