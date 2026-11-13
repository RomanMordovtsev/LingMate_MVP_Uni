# Reference learner: Roman (RU L1 → es-ES, A2 → B1)

Real situations where Roman lacked words or grammar, and real errors he made. Source of truth for his path.

**Live source:** Notion page «Испанский: ситуации, где не хватило слов»
(`40afd66e1d3481cd9571db1c4ea0a18d`, https://app.notion.com/p/40afd66e1d3481cd9571db1c4ea0a18d).
Roman adds new situations at the top. Each agent run: fetch the page with the Notion connector, add new entries here (newest first) and new cases to `eval/cases/es_roman.jsonl`. Never edit the Notion page.

## How to use this file
- **Transfer map (roadmap 1.5):** each error tagged below is a candidate rule for `core/pedagogy/l1_maps/ru_es.py`.
- **Eval harness (1.3a, `eval/`):** each "said → better" pair is a gold case; synthetic cases built from these situations live in `eval/cases/es_synthetic.jsonl`.
- **Scenarios (4.3):** each situation is a scenario seed for the relocation pack (bar, bus, queue…).
- **SRS (3.1):** listed chunks go into the review queue.

## Recurrent patterns (update as entries accumulate)
| Pattern | Category | Evidence |
|---|---|---|
| tú with strangers/older people instead of usted (pragmatics/register) | register | bus 31.10 |
| vague all-purpose verb (`¿puedo?`) instead of the situational chunk (`¿me deja pasar?`) | lexical / chunk | bus 31.10 |
| hesitation in service encounters: doesn't know the formula (`¿me pones…?`) | chunk | bar 31.10 |
| missing social routine formulas (`¡Que aproveche!`, que + subjuntivo wishes, `¿se puede?` / `con permiso`) | chunk / pragmatics | meal 02.11, adelante 03.11 |
| anglicism / calque: `la línea` for a queue (EN *line*) | lexical, transfer EN | queue 2026-10 |
| verb + preposition: `esforzarse` without `por/en` | preposition | compliment 2026-10 |
| spelling under EN influence: `possible` → `posible` | spelling_accent, transfer EN | compliment 2026-10 |
| everyday household / service vocabulary gaps (heating, postcards, meals, milk types) | lexical / chunk | 05.11, 06.11, 07.11 |
| gender of nouns not ending in -o/-a (`la postal`, `-ción`) | gender | 06.11 |
| confusing similar-sounding words (`abrigo / abogado / aguacate`; RU «авокадо» ≈ *abogado*) | lexical, interlingual false friend RU | 12.11 |
| RU verb doesn't map 1:1: «отдал в ремонт» ≠ *di* → **dejar**; traer/llevar by deixis | lexical / chunk | backpack 13.11 |
| "accidental" se-construction: **se me ha olvidado**, se me ha caído/roto | clitic / chunk | olvidar 13.11 |
| reading labels / written Spanish of everyday life (packaging, signs) | lexical, reading | Kinder 13.11, fíjate 13.11 |

Note: many of Roman's errors come from **English** (C1), not Russian — the transfer map must allow any language in the repertoire as `transfer_source` (multilingual-education §1, morphosyntax §7).

## Situations (newest first)

### 13.11.2026 — Storage phrases on packaging (Kinder)
- Reading situation (no utterance → no eval case). Label chunks: **Conservar en lugar fresco y seco** (*fresco* = cool, not "fresh"), **Consumir preferentemente antes del…** (best before) vs **Fecha de caducidad / Consumir antes del…** (use by), *caducado*; **Conservar en el frigorífico / la nevera**; **Una vez abierto, consumir en X días**; *a temperatura ambiente*; *Sin gluten*, *Valores nutricionales*, *Ingredientes*.
- Ingredients: leche entera / desnatada en polvo; manteca de cacao, pasta de cacao; mantequilla vs **manteca** (fat: de palma, de cerdo; in Argentina *manteca* = butter); relleno; azúcar.
- Uses: SRS (3.1); reading input for a supermarket / everyday-life unit (C.1); *fresco* = cool is a candidate lexical note (RU «свежий»).

### 13.11.2026 — "Yesterday I left you a backpack to repair"
- Service situation at a repair shop (no utterance recorded → no eval case). Chunks: **Ayer les dejé una mochila para arreglar.** / *Ayer traje una mochila a arreglar.* / **Vengo a recoger la mochila que dejé ayer.** / **¿Ya está lista?** / **¿Cuánto le debo?**
- Verb choice: **dejar** (leave for repair / dry cleaning / cloakroom); **traer** (bring here; irregular preterite *traje*) vs **llevar** (take there: *Ayer llevé la mochila a arreglar*); RU «отдал» as *di* (dar) sounds like a gift.
- Grammar: *les* (the shop, ustedes) / *le* (usted) / *te*; *para arreglar* ≈ *a arreglar* (a with motion verbs). Vocabulary: arreglar/reparar, coser, la cremallera, la correa / el asa, recoger, el resguardo.
- Uses: scenario seed for the relocation pack (4.3: repair shop / dry cleaner); transfer note candidate RU «отдать» → *dejar*.

### 13.11.2026 — «La percha» (hanger)
- Vocabulary (no eval case): **la percha** (clothes hanger), **el perchero** (coat stand / hooks), el gancho; LatAm *gancho / colgador*. Chunks: *Cuelga el abrigo en el perchero.* / *¿Tienes una percha?*; colgar (o→ue); el armario, el cajón; tender la ropa, el tendedero, la pinza.
- Mnemonic: **-ero** = place/holder for many X (percha → perchero, llave → llavero, azúcar → azucarero).

### 13.11.2026 — What does «fíjate» mean
- Comprehension question (no eval case). **fijarse (en)** = notice / pay attention: *Fíjate en el acento*; *¡Fíjate!* (surprise); **Fíjate que…** (discourse opener); *Fíjate si está abierto*; forms fíjate / fíjese / fijaos / fíjense; *no te fijes*; *me he fijado en que…*. Without -se: *fijar una fecha*.
- Accent appears when the pronoun is attached (fíjate, abrígate, siéntate) — a spelling_accent rule for imperatives + clitics.

### 13.11.2026 — «Я забыл» (I forgot)
- Production gap (no utterance → no eval case of his own). Three constructions: **Se me ha olvidado / Se me olvidó** (most natural, accidental), **Me he olvidado de algo**, **He olvidado algo**. *Se me han olvidado las llaves* (verb agrees with the thing). Same pattern: *se me ha caído / roto / perdido*.
- Typical error (from the page, not Roman's own utterance): *me olvidé el paraguas* → *me olvidé **del** paraguas* (preposition) — candidate synthetic eval case.
- In Spain recent events → pretérito perfecto (*se me ha olvidado*); *se me olvidó* for earlier / LatAm.
- Uses: chunk for SRS; grammar point "se accidental" for the A2→B1 curriculum (C.1).

### 12.11.2026 — Mixing up abrigo / abogado / aguacate
- Problem (vocabulary, no utterance recorded → no eval case): often confuses similar words.
- **el abrigo** = coat (← *abrigar* "to keep warm": *¡Abrígate!*, *Esta chaqueta abriga mucho.*); **el abogado / la abogada** = lawyer (← Lat. *advocatus*, same root as RU «адвокат»: v→b, c→g; *abogar por*); **el aguacate** = avocado (← Nahuatl *ahuacatl*; trap: RU «авокадо» sounds like *abogado*).
- Rule of thumb: food → *aguacate*, court → *abogado*. Linking sentence: *El abogado lleva un abrigo y come aguacate.*
- Other a- neighbours: abrir / abrigo / abril; abuelo / aburrido.
- Uses: SRS (3.1) with pictures, not translations (the Notion page suggests Anki cards with images); candidate RU→ES false-friend rule (*авокадо* ≠ *abogado*) for the transfer map.

### 07.11.2026 — Виды молока (kinds of milk)
- Question (vocabulary, no utterance → no eval case of his own; correct café orders added as clean cases in `es_synthetic.jsonl`). Directly feeds roadmap 4.1 café follow-up chunks (feedback 2026-11-05 §6).
- Cow's milk: **leche entera / semidesnatada / desnatada / sin lactosa**; leche fresca vs **UHT / de larga duración**, el brik; de cabra, de oveja. "Normal" milk: just **leche**; vs plant milk **leche normal** (colloquial) / **leche de vaca**. Barista may ask: *¿Leche normal o de avena?*
- Plant drinks: **de avena / soja / almendra(s) / arroz / coco / avellana**; labels *sin azúcares añadidos*, *barista*, *con calcio*. In EU shops the label says **bebida de avena** (not "leche"); in cafés people say *leche de avena*.
- Chunks: **Un café con leche de avena, por favor.** / **¿Tenéis leche vegetal / sin lactosa?** / *¿Con leche fría o caliente?* / **Un cortado con leche de soja.**

### 06.11.2026 — «Отопление» (heating)
- Question (vocabulary, no utterance → no eval case). Relevant to renting in Vitoria (4.3 landlord scenario).
- **la calefacción** (central / individual), el radiador, la caldera, el termostato, la estufa, el aire acondicionado; **encender / apagar**, **subir / bajar la calefacción**.
- Chunks: ¿Podemos encender la calefacción? / La calefacción no funciona. / El radiador de mi habitación está frío. / **¿La calefacción está incluida en el alquiler?** / Hace frío en casa.
- Form: -ción nouns are feminine, stress on the last syllable; plural loses the accent (calefacciones).

### 06.11.2026 — «Открытка» (postcard)
- Question (vocabulary, no eval case).
- **la postal / la tarjeta postal** (sent by post) vs **la tarjeta (de felicitación / de cumpleaños / de Navidad)**, colloquial *el christmas*.
- Chunks: Te he mandado una postal desde Vitoria. / ¿Dónde puedo comprar postales y sellos? / Quería enviar esta postal a Rusia. Related: el sello, Correos, el buzón, enviar / mandar.
- Form: **la postal** is feminine despite -l (gender trap → `gender` category, SRS); *tarjeta* also = bank card.

### 05.11.2026 — «Ужинать» (to have dinner)
- Question (vocabulary, no eval case).
- **cenar / la cena**; *cenar algo* without a preposition (Esta noche ceno pasta — not *ceno con*); salir a cenar; ¿Quedamos para cenar? ¿Qué hay para cenar?
- Other meals in Spain: desayunar, **comer** (= lunch, 14–15h), almorzar (late-morning snack in Spain), merendar. Culture: dinner 21:00–22:30 (intercultural note, 4.9).

### 03.11.2026 — What does «adelante» mean
- Question (comprehension, no utterance → no eval case): hears «adelante» often.
- Meanings: **¡Adelante!** = come in (after knocking) / go ahead (permission, encouragement); *sigue adelante* = keep going; **más adelante** = later / further on; **en adelante / de aquí en adelante** = from now on; **salir adelante** = get through hard times; **sacar adelante** algo = pull something off.
- Use: knocking → **Hola, ¿se puede?**; entering → **Con permiso**; letting someone pass → **Adelante, pasa / pase usted**; being let through → **Gracias**.
- Contrast: **adelante** (direction, "forward") vs **delante (de)** (location, "in front of": *Está delante de la puerta*). Synonym for "come in": ¡Pasa! / ¡Pase! Related: el adelanto, adelantar.

### 02.11.2026 — Wishing someone a good meal
- Problem: someone is eating (home, work, café): didn't know what to say. No utterance recorded, so no eval case.
- Better: **¡Que aproveche!** (most common in Spain) / **¡Buen provecho!** / **¡Que aproveches!** (tú) / **¡Que aprovechéis!** (vosotros) / **¡Aprovecha!** (colloquial) / Basque **On egin!** (appreciated in Vitoria).
- Replies: Gracias. / Gracias, igualmente. / ¿Quieres? (offering some)
- Grammar: **que + subjuntivo** for wishes (¡Que te mejores! ¡Que descanses! ¡Que te vaya bien!); aprovechar / el provecho.

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
