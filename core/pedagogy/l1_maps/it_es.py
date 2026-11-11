"""Italian ↔ Spanish map. Italian is close to Spanish (psychotypology, sla.md §4), so it
is mostly a *bridge*: explain a Spanish form via the Italian one the learner knows
(multilingual-education.md §1). A few false friends are negative rules."""
from .base import TransferRule

_S, _T = "it", "es"

RULES = (
    TransferRule(
        "it_es.burro", _S, _T, "lexical", "Ложный друг: burro ≠ масло",
        "il burro", "la mantequilla",
        {"ru": "Итальянское burro (масло) по-испански la mantequilla; el burro — осёл.",
         "en": "Italian burro (butter) is mantequilla; Spanish burro is a donkey."},
        original_markers=(r"\bburro\b",), corrected_markers=(r"\bmantequilla\b",),
    ),
    TransferRule(
        "it_es.salir", _S, _T, "lexical", "Ложный друг: salire ≠ salir",
        "salire le scale", "subir las escaleras",
        {"ru": "Итальянское salire — подниматься (по-испански subir); испанское salir — выходить (= uscire).",
         "en": "Italian salire is subir; Spanish salir means 'go out' (uscire)."},
        original_markers=(r"\bsal\w*\b",), corrected_markers=(r"\bsub\w*\b",),
    ),
    # --- bridges (positive transfer) ---------------------------------------
    TransferRule(
        "it_es.stare", _S, _T, "ser_estar", "Как итальянское stare",
        "Sto bene. Come stai?", "Estoy bien. ¿Cómo estás?",
        {"ru": "Estar похож на stare (sto bene → estoy bien), но шире: "
               "в испанском estar ещё и для места (Estoy en casa — в итальянском Sono a casa).",
         "en": "Like Italian stare (sto bene → estoy bien), but Spanish estar also covers location."},
        "Italian bridge: estar ≈ stare (but also location).", kind="bridge",
    ),
    TransferRule(
        "it_es.articoli", _S, _T, "article", "Как артикли в итальянском",
        "Mi piace il caffè", "Me gusta el café",
        {"ru": "Артикли работают почти так же — il caffè → el café, "
               "un amico → un amigo.",
         "en": "Articles work almost like Italian: il caffè → el café."},
        kind="bridge",
    ),
    TransferRule(
        "it_es.congiuntivo", _S, _T, "mood", "Как congiuntivo",
        "Voglio che tu venga", "Quiero que vengas",
        {"ru": "Как congiuntivo — voglio che tu venga → quiero que vengas.",
         "en": "Like the Italian congiuntivo: voglio che tu venga → quiero que vengas."},
        kind="bridge",
    ),
    TransferRule(
        "it_es.imperfetto", _S, _T, "tense_aspect", "Как imperfetto / passato",
        "Leggevo un libro / Ho letto il libro", "Leía un libro / Leí el libro",
        {"ru": "Imperfecto ≈ imperfetto (фон, привычка), "
               "законченное событие — как passato prossimo/remoto.",
         "en": "imperfecto ≈ imperfetto; a completed event ≈ passato prossimo/remoto."},
        kind="bridge",
    ),
    TransferRule(
        "it_es.pronomi", _S, _T, "clitic", "Как местоимения в итальянском",
        "Dammelo. Lo vedo.", "Dámelo. Lo veo.",
        {"ru": "Местоимения ставятся так же — dammelo → dámelo, lo vedo → lo veo.",
         "en": "Clitics go like Italian: dammelo → dámelo."},
        kind="bridge",
    ),
)
