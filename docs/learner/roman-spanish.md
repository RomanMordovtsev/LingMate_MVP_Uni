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
| gender with numbers / implied nouns (*a la cero* → *al cero* / *a la baja*) | gender / lexical | lift 14.11 |
| RU-style verb choice where Spain prefers *poner/quitar* (heating, lights) | lexical / chunk | heating 06.11 (+14.11) |
| concessive "even if": *aunque* + subjuntivo vs indicativo; never *si* + present subjunctive | mood | even if 15.11 |
| academic / presentation vocabulary from EN (*engage* ≠ *comprometer*; *público* vs *audiencia*) | lexical, transfer EN | engage 15.11 |
| hoping / wishing: *espero que* + subjuntivo (*salga, vaya*), *ojalá*, *eso espero* | mood / chunk | espero 19.11 |
| personal data in forms: *dirección / domicilio*, Spanish address format; spelling *dirección* (cc, EN *direction*) | lexical / spelling_accent, transfer EN | address 23.11 |
| EN/RU "overhaul / капитальный ремонт" → *reforma integral* (flat, system), *revisión a fondo* (car); *la reforma* = flat renovation in Spain | lexical, transfer EN/RU | overhaul 22.11 |
| EN news/academic adverbs (*allegedly*) → *presuntamente / supuestamente / al parecer*; *presumir* = to boast, not *to presume* | lexical, transfer EN | allegedly 19.11 |

Note: many of Roman's errors come from **English** (C1), not Russian — the transfer map must allow any language in the repertoire as `transfer_source` (multilingual-education §1, morphosyntax §7).

## Situations (newest first)

### 23.11.2026 — «Адрес» (address)
- Question (no utterance → synthetic eval case `syn-spelling-en-direccion`: *direción* under EN *direction* → **dirección**).
- **la dirección** = address (also "direction", "management"); **el domicilio** = address of residence in forms, banks, documents (*domicilio habitual, domicilio fiscal*); **la dirección de correo (electrónico) / el correo / el email**; **la dirección de envío** = delivery address.
- Chunks: *¿Cuál es tu dirección? / ¿Me das tu dirección?*, *Vivo en la calle… número…*, *¿Me lo puedes enviar a esta dirección?*, *He cambiado de domicilio.*
- Spanish address format: **C/ Mayor 12, 3º izda., 01001 Vitoria-Gasteiz** (street, number, floor + side/letter, then *código postal* (5 digits) + city); abbreviations *C/, Avda., Pza., Pº, nº, s/n*; flat by side *izda. / dcha.* or letter *A, B*; read aloud *calle Mayor, doce, tercero izquierda*.
- Spelling / gender: dire**cc**ión (two c, tilde), **la** dirección, plural *direcciones* (no tilde). No Spanish word resembles RU «адрес».
- Uses: curriculum unit «Mis datos, por favor» (C.1, `es-a2-tramites`), relocation pack 4.3 (empadronamiento, bank, deliveries), SRS chunks.

### 22.11.2026 — «Overhaul» → reforma integral / revisión a fondo
- Question from English (no utterance → synthetic eval case `syn-lexical-ru-overhaul`: RU calque *reparación capital* «капитальный ремонт» → *reforma integral*).
- By context: system / laws → **una reforma integral / a fondo**, *reformar a fondo*, *reestructurar*; car / engine → **una revisión general / a fondo** (*rectificar / reconstruir el motor*); website / product → *renovar por completo, rehacer, remodelar*; CV / text → *rehacer, darle un buen repaso*. Colloquial *un lavado de cara* = a cosmetic revamp, not an overhaul.
- Spain: **la reforma** = also renovating a flat: *Estamos de reformas.*, *una reforma integral del piso*; rental ads *reformado* / *a reformar*. **revisar** = check / service a car (*llevar el coche a revisar*) — without *a fondo / general* it is not an overhaul. *rehacer* conjugates like *hacer* (rehago, rehice, rehecho).
- Uses: relocation pack 4.3 (renting, landlord), EN→ES / RU→ES lexical transfer, SRS chunks.

### 19.11.2026 — «Allegedly» → presuntamente / supuestamente
- Question from English (no utterance → synthetic eval case `syn-lexical-en-4`: *presume que* → *supone que* / *al parecer*).
- **presuntamente** (news, legal; exact *allegedly*): *El hombre presuntamente robó 5.000 euros.*; **supuestamente** (colloquial, doubtful *supposedly*); **al parecer / según parece** (*apparently*); **según fuentes / según informan** (*reportedly*).
- Word family: *presunto/-a* (*el presunto autor, la presunta víctima*), *la presunción de inocencia*; *supuesto/-a*, **por supuesto** = of course.
- False friend: **presumir** in everyday Spanish = **to boast** (*presumir de coche*, *presumido* = show-off), not EN *presume* → new rule `en_es.presumir`.
- Stress: presuntaMENte, supuestaMENte (main stress on *-men-* + secondary on the adjective).
- Uses: news / reading (content mode 4.6), EN→ES transfer map (1.5), SRS chunks.

### 19.11.2026 — «Надеюсь, всё будет хорошо»
- Question (no utterance → synthetic eval case `syn-mood-4`: *Espero que todo sale bien* → *salga*).
- **Espero que todo salga bien.** (a concrete event: exam, interview), **Espero que todo vaya bien.** (general), **¡Ojalá (que todo salga bien)!**, **Eso espero.** (*I hope so*), **Espero que no.**
- Grammar: **esperar que + subjuntivo** (other subject: *Espero que tengas un buen día.*); **esperar + infinitivo** (same subject: *Espero aprobar el examen.*); **ojalá (que) + subjuntivo** always; irregular *salir → salga, ir → vaya*.
- Note: *esperar* = to hope and to wait (*Te espero en la puerta.*); after *que + subjuntivo* it almost always means "hope".
- Uses: curriculum unit «Buenos deseos» (C.1, `es-a2-buenos-deseos` → B1 *que + subjuntivo*), SRS chunks.

### 15.11.2026 — «Even» / «even if it's 0 degrees outside»
- Question (no utterance of Roman's → synthetic eval case `syn-mood-3`: *incluso si haga* → *incluso si hace* / *aunque haga*).
- **aunque + subjuntivo** = "even if" (hypothesis / doesn't matter): *Abro la ventana todos los días, aunque haga cero grados fuera.*; **aunque + indicativo** = "although" (fact): *Aunque hace frío, salgo.*; **incluso si + indicativo** (closer to EN); after *si* never present subjunctive.
- Plain "even": **incluso / hasta**, negative **ni siquiera** (*Ni siquiera me saludó.*), "even more" **aún / todavía más**.
- Temperature: **hace cero grados / estamos a cero grados**, **bajo cero** (*dos grados bajo cero*), **fuera** (Spain) / *afuera* (LatAm).
- Uses: mood unit B1 (concessive clauses, C.1), SRS chunks, weather small talk.

### 15.11.2026 — «Engage the audience» (presentations)
- Question for class presentations (no utterance → synthetic eval case `syn-lexical-en-3`: *comprometer a la audiencia* → *implicar al público*).
- By nuance: **captar la atención del público** (at the start), **mantener el interés**, **implicar / involucrar al público** (closest to *engage*), **hacer participar al público**, **conectar con el público**, colloquial **enganchar**.
- **el público** = live audience; **la audiencia** = TV/radio/social-media viewers (also "audience" with a judge); in class *los oyentes / los compañeros*.
- False friend: **comprometer** ≠ engage (= to commit / compromise) → candidate EN rule for `en_es`. Noun: *la implicación / la participación* (marketing: *el engagement*). *implicar → implique* (c→qu).
- Uses: study/work scenario (university presentation, 4.3), EN→ES transfer map (1.5).

### 14.11.2026 — In the lift: «¿Abajo?»
- Said: **Sí, a la cero.** (understood, but odd: *cero* is masculine; the ground floor is *la (planta) baja*) → eval case `roman-2026-11-14-lift`.
- Better: **Sí, a la baja.** (most natural) / **Sí, al cero.** (the button) / **Sí, gracias.** (just going down).
- Gender of floors: ordinals imply *planta* → feminine (*a la primera, a la segunda*); with *piso* → masculine (*al tercero*); cardinals for the button → masculine (*al cero, al tres*).
- Lift chunks: **¿Subes? / ¿Bajas?**, **¿A qué piso vas?**, *Al tercero, por favor.*, **¿Me aguantas la puerta?**
- Culture: Spanish floor numbering ≠ Russian: planta baja (0) = RU 1st floor, primera = RU 2nd; *entresuelo*, *sótano / garaje (-1)*; *piso* = floor and flat, *planta* = floor only.
- Uses: scenario seed (4.3: building / neighbours), intercultural note (4.9), gender note for numbers (morphosyntax §7).

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
- Added 14.11: in Spain everyday speech uses **poner / quitar la calefacción** (*¿Pones la calefacción?*, *¿Has puesto la calefacción?*, *¿Te importa si pongo la calefacción?*, *¿Está puesta?*); *encender* (e→ie: enciendo).
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
