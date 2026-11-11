"""English → Spanish transfer map. Many of Roman's real errors come from English (C1),
not Russian (docs/learner/roman-spanish.md: línea for a queue, possible, esforzarse
without por). Calques and false friends are word-level rules; markers run on folded text."""
from .base import TransferRule

_S, _T = "en", "es"


def _ff(word_id, en, en_phrase, es_wrong, es_right, ru_note, markers, corrected=()):
    """False friend / calque rule (lexical)."""
    return TransferRule(
        f"en_es.{word_id}", _S, _T, "lexical", f"Ложный друг: {en} ≠ {es_wrong}",
        en_phrase, es_right, {"ru": ru_note, "en": f"'{es_wrong}' does not mean '{en}': say {es_right}."},
        original_markers=markers, corrected_markers=corrected,
    )


RULES = (
    _ff("linea_cola", "line", "stand in line", "línea", "la cola / hacer cola",
        "Очередь — la cola (hacer cola, ¿quién es el último?). La línea — линия (автобуса, телефона), "
        "это калька с английского line.",
        (r"\blinea\b",), (r"\b(cola|fila)\b",)),
    _ff("embarazada", "embarrassed", "I'm embarrassed", "embarazada", "me da vergüenza / avergonzado",
        "Embarazada — «беременная»! «Мне неловко» — me da vergüenza, estoy avergonzado/a.",
        (r"\bembarazad[oa]s?\b",)),
    _ff("actualmente", "actually", "Actually, I…", "actualmente", "en realidad / de hecho",
        "Actualmente — «в настоящее время», а не «на самом деле». «На самом деле» — en realidad, de hecho.",
        (r"\bactualmente\b",), (r"\b(en realidad|de hecho|la verdad)\b",)),
    _ff("realizar", "realize", "I realized that…", "realizar", "darse cuenta (de)",
        "Realizar — «осуществить, провести». «Понять, осознать» — darse cuenta (de): Me di cuenta de que…",
        (r"\breali[zc]\w*\b",), (r"\bcuenta\b",)),
    _ff("libreria", "library", "the library", "librería", "la biblioteca",
        "Librería — книжный магазин. Библиотека — la biblioteca.",
        (r"\blibreria\b",), (r"\bbiblioteca\b",)),
    TransferRule(
        "en_es.double_consonant", _S, _T, "spelling_accent", "Двойные согласные из английского",
        "possible, professor, communicate", "posible, profesor, comunicar",
        {"ru": "В испанском не бывает ss, mm, ff, pp, tt: posible, profesor, comunicar. "
               "Двойными бывают только rr, ll и cc (acción).",
         "en": "Spanish has no ss/mm/ff/pp/tt: posible, profesor, comunicar (only rr, ll, cc)."},
        "English spelling leaks in: no double ss/mm/ff/pp/tt in Spanish (posible, profesor).",
        original_markers=(r"(ss|mm|ff|pp|tt)",),
    ),
    TransferRule(
        "en_es.esforzarse", _S, _T, "preposition", "make an effort to → esforzarse por/en",
        "I make an effort to practise", "Me esfuerzo por practicar",
        {"ru": "Esforzarse требует предлога: me esfuerzo por / en practicar. "
               "Без предлога: intento / procuro practicar.",
         "en": "esforzarse needs por/en before an infinitive; intentar/procurar take none."},
        corrected_markers=(r"\besf(ue|o)r[cz]\w*\s+(por|en)\b",),
    ),
    TransferRule(
        "en_es.depend_on", _S, _T, "preposition", "depend on → depender de",
        "It depends on the weather", "Depende del tiempo",
        {"ru": "Depender de (не en, хотя по-английски on): Depende del tiempo.",
         "en": "depender de, not en."},
        original_markers=(r"\bdepend\w*\s+(en|sobre)\b",),
    ),
    TransferRule(
        "en_es.think_of", _S, _T, "preposition", "think of/about → pensar en",
        "I'm thinking of moving", "Pienso en mudarme / Pienso mudarme",
        {"ru": "«Думать о» — pensar en (не de/sobre, как think of/about); «собираться» — pensar + инфинитив.",
         "en": "think of/about → pensar en; 'plan to' → pensar + infinitive."},
        original_markers=(r"\b(pens|piens)\w*\s+(de|sobre)\b",),
    ),
    TransferRule(
        "en_es.to_be", _S, _T, "ser_estar", "Одно to be → ser и estar",
        "I am tired. I am a student.", "Estoy cansado. Soy estudiante.",
        {"ru": "В английском одно to be. ser — кто/что это по сути; estar — где и в каком состоянии сейчас.",
         "en": "English has one 'to be'. ser: identity, essence; estar: location and current state."},
    ),
    TransferRule(
        "en_es.calque", _S, _T, "lexical", "Калька с английского",
        "make a decision, take a photo", "tomar una decisión, hacer una foto",
        {"ru": "Похоже на дословный перевод с английского. Испанский часто берёт другой глагол или "
               "готовую фразу: tomar una decisión, hacer una foto, hacer cola.",
         "en": "Looks like a word-for-word English calque; Spanish uses its own chunk."},
        "English calques and false friends (línea for a queue, embarazada, actualmente, realizar).",
    ),
)
