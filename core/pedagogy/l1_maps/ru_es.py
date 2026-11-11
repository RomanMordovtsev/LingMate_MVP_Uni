"""Russian → Spanish transfer map (morphosyntax.md §7: articles, ser/estar, gender
mismatches, preterite vs imperfect, subjunctive, clitic order).
Markers run on folded text (lower case, no accents)."""
from .base import TransferRule

_S, _T = "ru", "es"

RULES = (
    # --- specific (word-level) rules first --------------------------------
    TransferRule(
        "ru_es.gender_ma", _S, _T, "gender", "Род: слова на -ma мужского рода",
        "эта проблема, новая система", "el problema, el sistema nuevo",
        {"ru": "Большинство слов на -ma греческого происхождения в испанском мужского рода, "
               "хотя в русском они женского: el problema, el tema, el sistema, el idioma, el clima.",
         "en": "Most Greek-origin nouns in -ma are masculine in Spanish: el problema, el tema, el sistema."},
        "Gender of nouns differs from Russian: el problema/tema/sistema/idioma/clima, la leche, la postal.",
        corrected_markers=(r"\b(el|un|este|ese|aquel|del|al)\s+(problema|tema|sistema|programa|idioma|clima|mapa|dia|planeta)\b",),
    ),
    TransferRule(
        "ru_es.gender_mismatch", _S, _T, "gender", "Род не совпадает с русским",
        "молоко (ср. р.), открытка", "la leche, la postal",
        {"ru": "Род в испанском не всегда совпадает с русским: la leche (молоко — ср. р.), "
               "la postal, la calle, el coche. Слова на -ción всегда женского рода.",
         "en": "Gender often differs from Russian: la leche, la postal, la calle; -ción nouns are feminine."},
        corrected_markers=(r"\b(la|una|esta|esa)\s+(leche|postal|calle|sal|miel|nariz|sangre|carne|\w+cion)\b",
                           r"\b(el|un|este|ese)\s+(coche|arbol|dolor|viaje|garaje)\b"),
    ),
    TransferRule(
        "ru_es.pensar_en", _S, _T, "preposition", "думать о → pensar en",
        "Я думаю о тебе", "Pienso en ti",
        {"ru": "«Думать о ком-то» — pensar en (не de/sobre): Pienso en ti. "
               "Pensar de = иметь мнение: ¿Qué piensas de esto?",
         "en": "'Think about someone' is pensar en, not de/sobre."},
        original_markers=(r"\b(pens|piens)\w*\s+(de|sobre)\b",), corrected_markers=(r"\b(pens|piens)\w*\s+en\b",),
    ),
    TransferRule(
        "ru_es.meal_verbs", _S, _T, "preposition", "ужинать чем → cenar algo",
        "Сегодня ужинаю пастой", "Esta noche ceno pasta",
        {"ru": "Cenar, comer, desayunar берут еду без предлога: ceno pasta (не «ceno con pasta»). "
               "Con — только «с кем»: ceno con amigos.",
         "en": "Meal verbs take the food directly: ceno pasta (con is for people)."},
        original_markers=(r"\b(cen|desayun|com|almuer[cz]|almorz|merend)\w*\s+con\b",),
    ),
    # --- category-level rules ----------------------------------------------
    TransferRule(
        "ru_es.article", _S, _T, "article", "Артикли: в русском их нет",
        "Мне нравится кофе. Я купил машину.", "Me gusta el café. Compré un coche.",
        {"ru": "В русском нет артиклей, поэтому их легко пропустить. el/la — «тот самый» или вещь "
               "вообще (me gusta el café), un/una — «какой-то, один» (compré un coche).",
         "en": "Russian has no articles. el/la: known or generic (me gusta el café); un/una: new, one of many."},
        "Russian has no articles: watch for missing or wrong el/la/un/una (me gusta el café).",
    ),
    TransferRule(
        "ru_es.ser_estar", _S, _T, "ser_estar", "Один глагол «быть» → ser и estar",
        "Я устал. Он врач. Я в Витории.", "Estoy cansado. Es médico. Estoy en Vitoria.",
        {"ru": "В русском одно «быть» (часто пропускается). ser — что это, кто это, какое по сути; "
               "estar — где и в каком состоянии сейчас.",
         "en": "Russian has one 'to be'. ser: identity, essence; estar: location and current state."},
        "Russian has one (often omitted) 'to be': watch ser vs estar.",
    ),
    TransferRule(
        "ru_es.aspect", _S, _T, "tense_aspect", "Вид глагола ≠ pretérito / imperfecto",
        "Я читал книгу (долго) / Я прочитал книгу", "Leía un libro / Leí el libro",
        {"ru": "Похоже на совершенный/несовершенный вид, но не 1:1: imperfecto — фон, привычка, описание "
               "в прошлом; indefinido — законченное событие, даже долгое (Viví dos años en Madrid).",
         "en": "Like Russian aspect but not 1:1: imperfecto = background/habit; indefinido = completed event."},
        "Russian aspect does not map 1:1 onto pretérito indefinido vs imperfecto.",
    ),
    TransferRule(
        "ru_es.subjunctive", _S, _T, "mood", "«чтобы + прошедшее» → que + subjuntivo",
        "Хочу, чтобы ты пришёл. Надеюсь, что ты придёшь.", "Quiero que vengas. Espero que vengas.",
        {"ru": "Где в русском «чтобы» или пожелание, в испанском que + subjuntivo: Quiero que vengas, "
               "¡Que aproveche! После esperar que, para que, cuando (о будущем) — тоже subjuntivo.",
         "en": "Where Russian uses 'chtoby' or a wish, Spanish uses que + subjunctive."},
        "Russian has no subjunctive forms: watch que + subjuntivo after querer/esperar/para que/cuando.",
    ),
    TransferRule(
        "ru_es.clitic", _S, _T, "clitic", "Местоимения-клитики стоят у глагола",
        "Я его видел. Дай мне его.", "Lo vi. Dámelo.",
        {"ru": "В русском местоимение может стоять где угодно; в испанском lo/la/le/me/te — прямо перед "
               "спрягаемым глаголом (lo vi) или слитно после инфинитива/императива (dámelo, quiero verlo).",
         "en": "Clitics go right before the finite verb (lo vi) or attached to infinitive/imperative (dámelo)."},
        "Clitic placement and lo/la/le differ from Russian free pronoun order.",
    ),
    # Positive transfer: Russian ты/вы matches tú/usted (bridge for register errors).
    TransferRule(
        "ru_es.tu_usted", _S, _T, "register", "ты / вы → tú / usted",
        "Простите, вы не пропустите?", "Perdone, ¿me deja pasar?",
        {"ru": "Как в русском «ты/вы»: с пожилыми незнакомыми и официально — usted (perdone, ¿me deja…?), "
               "с барменом и сверстниками в Испании — tú.",
         "en": "Like Russian ty/vy: usted with older strangers and officials, tú with peers."},
        kind="bridge",
    ),
)
