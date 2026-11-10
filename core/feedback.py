"""
Structured corrective feedback (roadmap 1.3).

The LLM returns `correction` as an object (or null). Models are not always
obedient, so `normalize_correction` accepts the legacy plain string, partial
objects and wrong-case enums, and always returns either None or a dict with
exactly the keys of the contract. Pure functions, no I/O.

Grounding: error categories follow the RU/EN→ES problem areas in
docs/research/morphosyntax.md §7 and the CF typology in §2 / sla.md §4.
"""

import difflib
import re
import unicodedata
from typing import Any, Dict, List, Optional

ERROR_CATEGORIES = (
    "article", "gender", "agreement", "ser_estar", "tense_aspect", "mood",
    "preposition", "clitic", "word_order", "lexical", "spelling_accent", "register",
)
CF_TYPES = ("recast", "explicit", "metalinguistic", "elicitation", "clarification")

# Tolerated synonyms that small models produce.
_CATEGORY_ALIASES = {
    "spelling": "spelling_accent", "accent": "spelling_accent", "accents": "spelling_accent",
    "orthography": "spelling_accent", "diacritics": "spelling_accent", "punctuation": "spelling_accent",
    "vocabulary": "lexical", "word_choice": "lexical", "lexis": "lexical", "anglicism": "lexical",
    "tense": "tense_aspect", "aspect": "tense_aspect", "subjunctive": "mood",
    "pronoun": "clitic", "pronouns": "clitic", "articles": "article",
    "pragmatics": "register", "politeness": "register", "formality": "register",
    "order": "word_order", "syntax": "word_order", "concord": "agreement",
}

# Contract text shared by both system prompts.
CORRECTION_CONTRACT = """CORRECTION (structured; feedback only about the learner's CURRENT "message"):
- Look ONLY at the field "message" (the learner's latest turn). Never repeat or re-correct errors from earlier turns in "history".
- If "message" is fully correct and natural for the situation, correction MUST be null.
- Otherwise correction is ONE object for the most important error:
  {{"original": "<the learner's words that are wrong>",
    "corrected": "<the same words, corrected, in {target_language}>",
    "error_category": one of {categories},
    "cf_type": one of {cf_types},
    "is_transfer": true if the error likely comes from another language the learner knows,
    "transfer_source": language code of that language (e.g. "en", "ru", "it") or null,
    "explanation": "<one short sentence in {native_language}>"}}
- If is_transfer is true, transfer_source is REQUIRED: the code of the learner's language the error comes from (e.g. "en" for an English calque, "ru" for a missing article).
- Missing accents (á é í ó ú ñ) and missing ¿ ¡ count as spelling_accent errors.
- Calques and false friends from ANY known language (e.g. English "line" → "línea" instead of "cola") are lexical errors with is_transfer true.
- Register must fit the situation and place: everyday colloquial forms (e.g. "porfa", tú with a barman in Spain) are fine in informal settings and are NOT errors. Flag register only when it is clearly wrong (e.g. tú with an older stranger or an official).
"""


def correction_contract(settings: Dict[str, Any]) -> str:
    """Prompt block with the JSON contract, filled with the learner's languages."""
    return CORRECTION_CONTRACT.format(
        target_language=settings.get("target_language", "en"),
        native_language=settings.get("native_language", "ru"),
        categories=", ".join(f'"{c}"' for c in ERROR_CATEGORIES),
        cf_types=", ".join(f'"{c}"' for c in CF_TYPES),
    )


def _clean(value: Any) -> str:
    return str(value).strip() if value not in (None, "") else ""


def _category(value: Any) -> Optional[str]:
    key = _clean(value).lower().replace("-", "_").replace(" ", "_")
    if key in ERROR_CATEGORIES:
        return key
    return _CATEGORY_ALIASES.get(key)


def normalize_correction(raw: Any) -> Optional[Dict[str, Any]]:
    """Coerce whatever the model sent into the contract, or None for "no correction".
    Unknown categories become None; we never invent a transfer source."""
    if raw is None or raw is False:
        return None
    if isinstance(raw, str):
        text = raw.strip()
        if not text or text.lower() in {"null", "none", "n/a", "-"}:
            return None
        # Legacy plain-string correction: keep the text, category unknown.
        return {"original": "", "corrected": "", "error_category": None, "cf_type": "explicit",
                "is_transfer": False, "transfer_source": None, "explanation": text}
    if isinstance(raw, list):
        raw = next((r for r in raw if isinstance(r, (dict, str)) and r), None)
        return normalize_correction(raw)
    if not isinstance(raw, dict):
        return None

    original = _clean(raw.get("original"))
    corrected = _clean(raw.get("corrected") or raw.get("correction") or raw.get("text"))
    explanation = _clean(raw.get("explanation") or raw.get("note"))
    if not (corrected or explanation):
        return None
    if original and corrected and original == corrected and not explanation:
        return None  # model "corrected" a correct sentence to itself

    cf_type = _clean(raw.get("cf_type")).lower()
    source = _clean(raw.get("transfer_source")).lower() or None
    is_transfer = bool(raw.get("is_transfer")) or source is not None
    return {
        "original": original,
        "corrected": corrected,
        "error_category": _category(raw.get("error_category") or raw.get("category")),
        "cf_type": cf_type if cf_type in CF_TYPES else "recast",
        "is_transfer": is_transfer,
        "transfer_source": source if is_transfer else None,
        "explanation": explanation,
    }


def correction_to_text(correction: Optional[Dict[str, Any]]) -> str:
    """One readable line for the progress log and old clients."""
    if not correction:
        return ""
    head = ""
    if correction.get("original") and correction.get("corrected"):
        head = f"{correction['original']} → {correction['corrected']}"
    elif correction.get("corrected"):
        head = correction["corrected"]
    parts = [p for p in (head, correction.get("explanation")) if p]
    tag = f" [{correction['error_category']}]" if correction.get("error_category") else ""
    return " — ".join(parts) + tag


# ----------------------------------------------------------------------
# Diff view (roadmap 1.4): make the recast *noticeable*.
# Learners miss morphosyntactic recasts unless the changed morpheme is
# visibly marked (docs/research/morphosyntax.md §2; textual enhancement §6).
# ----------------------------------------------------------------------

_TOKEN_RE = re.compile(r"\w+|\s+|[^\w\s]", re.UNICODE)


def _fold(token: str) -> str:
    """Case- and accent-insensitive key: "Dónde" and "donde" align."""
    decomposed = unicodedata.normalize("NFD", token.lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def _push(segments: List[Dict[str, str]], op: str, text: str) -> None:
    if not text:
        return
    if segments and segments[-1]["op"] == op:
        segments[-1]["text"] += text
    else:
        segments.append({"op": op, "text": text})


def _same_stem(x: str, y: str) -> bool:
    """True when only an ending/accent changed ("cansado" → "cansada",
    "fuí" → "fui"), so marking letters is clearer than swapping the word.
    "la" → "el" or "soy" → "estoy" are different words: whole-word swap."""
    if not (re.match(r"\w", x) and re.match(r"\w", y)):
        return False
    fx, fy = _fold(x), _fold(y)
    if fx == fy:
        return True
    prefix = 0
    for cx, cy in zip(fx, fy):
        if cx != cy:
            break
        prefix += 1
    return prefix >= 2 and prefix * 2 >= min(len(fx), len(fy))


def _char_diff(segments: List[Dict[str, str]], a: str, b: str) -> None:
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            _push(segments, "equal", a[i1:i2])
        else:
            _push(segments, "del", a[i1:i2])
            _push(segments, "ins", b[j1:j2])


def _pair(segments: List[Dict[str, str]], x: str, y: str) -> None:
    if x == y:
        _push(segments, "equal", x)
    elif _same_stem(x, y):
        _char_diff(segments, x, y)
    else:
        _push(segments, "del", x)
        _push(segments, "ins", y)


def correction_diff(original: str, corrected: str) -> List[Dict[str, str]]:
    """Segments [{"op": "equal"|"del"|"ins", "text": ...}] turning `original`
    into `corrected`. Words are aligned ignoring case and accents; a word that
    only changed an ending or an accent is refined to letters. Empty list when
    there is nothing to compare.
    Concatenating equal+del gives `original`; equal+ins gives `corrected`."""
    original, corrected = (original or "").strip(), (corrected or "").strip()
    if not original or not corrected or original == corrected:
        return []
    a, b = _TOKEN_RE.findall(original), _TOKEN_RE.findall(corrected)
    segments: List[Dict[str, str]] = []
    sm = difflib.SequenceMatcher(None, [_fold(t) for t in a], [_fold(t) for t in b], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        left, right = a[i1:i2], b[j1:j2]
        if tag == "equal" or (tag == "replace" and len(left) == len(right)):
            for x, y in zip(left, right):
                _pair(segments, x, y)
        else:
            _push(segments, "del", "".join(left))
            _push(segments, "ins", "".join(right))
    return segments
