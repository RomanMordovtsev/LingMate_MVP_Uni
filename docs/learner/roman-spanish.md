# Reference learner: Roman (RU L1 → es-ES, A2 → B1)

Real situations where Roman lacked words or grammar, and real errors he made. Source of truth for his path.

**Live source:** Notion page «Испанский: ситуации, где не хватило слов»
(`40afd66e1d3481cd9571db1c4ea0a18d`, https://app.notion.com/p/40afd66e1d3481cd9571db1c4ea0a18d).
Roman adds new situations at the top. Each agent run: fetch the page with the Notion connector, add new entries here (newest first) and new cases to `eval/cases/es_roman.jsonl`. Never edit the Notion page.

## How to use this file
- **Transfer map (roadmap 1.5):** each error tagged below is a candidate rule for `core/pedagogy/l1_maps/ru_es.py`.
- **Eval harness (5.3):** each "said → better" pair is a gold case.
- **Scenarios (4.3):** each situation is a scenario seed for the relocation pack (bar, bus, queue…).
- **SRS (3.1):** listed chunks go into the review queue.

## Recurrent patterns (update as entries accumulate)
| Pattern | Category | Evidence |
|---|---|---|
| tú with strangers/older people instead of usted (pragmatics/register) | register | bus 31.10 |
| vague all-purpose verb (`¿puedo?`) instead of the situational chunk (`¿me deja pasar?`) | lexical / chunk | bus 31.10 |
| hesitation in service encounters: doesn't know the formula (`¿me pones…?`) | chunk | bar 31.10 |
| anglicism / calque: `la línea` for a queue (EN *line*) | lexical, transfer EN | queue 2026-10 |
| verb + preposition: `esforzarse` without `por/en` | preposition | compliment 2026-10 |
| spelling under EN influence: `possible` → `posible` | spelling_accent, transfer EN | compliment 2026-10 |

Note: many of Roman's errors come from **English** (C1), not Russian — the transfer map must allow any language in the repertoire as `transfer_source` (multilingual-education §1, morphosyntax §7).

## Situations (newest first)

### 31.10.2026 — Ordering a Coke in a bar
- Problem: always hesitates how to ask.
- Better: **Una Coca-Cola, por favor.** / **¿Me pones una Coca-Cola?** (tú with the barman is normal) / **Póngame…** (usted) / **Para mí, una Coca-Cola.**
- Chunks: con/sin hielo, con limón, Zero, de lata / de botella. `poner` in a bar = to serve.
- Note: `Quiero una Coca-Cola` is not wrong but sounds blunt in Spain.

### 31.10.2026 — Getting to the window seat on the bus
- Said: **Perdona, ¿puedo?** (understood, but vague and tú to an older stranger)
- Better: **Perdone, ¿me deja pasar?** / **Disculpe, es que mi asiento es el de la ventanilla.** / **Con permiso.**
- Grammar: usted imperatives (perdone/disculpe); **dejar + infinitivo**; **es que…** to soften a reason.
- Vocabulary: el asiento, la ventanilla (not la ventana), el pasillo, dejar pasar, apartarse.
- Likely replies: Sí, claro. / Pasa, pasa. / Perdón, no me había dado cuenta.

### 2026-10 — Responding to a compliment on his Spanish
- Said (mixed): *me esfuerzo practicar lo más possible*
- Better: **Gracias, me esfuerzo por practicar lo más posible.** More natural: **Intento practicar todo lo que puedo.** / **Procuro practicar mucho.**
- Points: esforzarse **por/en** + inf; *posible* with one s; procurar + inf (no preposition); *todo lo que puedo* ≠ *todo el tiempo que puedo*.

### 2026-10 — Standing near a queue
- Said: **No estoy en la línea.**
- Better: **No estoy en la cola.** / **No estoy haciendo cola.** (fila is understood; línea is an anglicism here)
- Chunks: ¿Quién es el último? — Yo. / Pase, pase.
