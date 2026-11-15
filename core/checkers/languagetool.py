"""
LanguageTool as a non-LLM pre-check (roadmap 5.7, Roman's answer to PR #15,
docs/feedback/2026-11-14-scouting-answers.md §2).

LanguageTool (LT) is a rule-based checker: no quota, no GPU, deterministic.
It is strong on spelling/accents and on local agreement (el/la + noun,
noun + adjective), weak on lexis, register and tense/aspect. Here it is used
only by the eval harness (alone and as a pre-check next to an LLM); whether
it goes into the app is decided after Roman's nightly numbers.

Server (env ``LANGUAGETOOL_URL``):
- default: the public API ``https://api.languagetool.org/v2`` (free, no key;
  limits ~20 requests/min, 20 KB/request — we wait ``min_interval_s`` between
  calls and send only the learner's sentence, nothing else);
- local: ``java -jar languagetool-server.jar --port 8081`` →
  ``LANGUAGETOOL_URL=http://localhost:8081/v2`` (no wait between calls).

``check()`` turns LT matches into ONE correction in the same contract as the
LLM (core/feedback.py), so the same scoring applies. Category mapping is a
heuristic over LT's rule ids / categories and the changed words.
"""

import os
import time
import unicodedata
from typing import Any, Callable, Dict, List, Optional, Tuple

import httpx

PUBLIC_URL = "https://api.languagetool.org/v2"
MAX_CHARS = 2000            # learner turns are short; never send long texts

# LT categories we never report: style advice and typography would flag
# colloquial but correct turns (*porfa*, docs/feedback/2026-11-05 §5).
_SKIP_CATEGORIES = {"STYLE", "REDUNDANCY", "WHITESPACE", "TYPOGRAPHY", "CASING", "COLLOQUIALISMS",
                    "REGIONALISMS", "SEMANTICS"}
_SKIP_ISSUES = {"style", "whitespace", "typographical", "register", "locale-violation"}

_ARTICLES = {"el", "la", "los", "las", "un", "una", "unos", "unas", "al", "del", "lo"}
_MASC = {"el", "los", "un", "unos", "al", "del"}
_FEM = {"la", "las", "una", "unas"}
_SER_ESTAR = {"soy", "eres", "es", "somos", "sois", "son", "era", "fue", "sea", "ser", "sido",
              "estoy", "estas", "esta", "estamos", "estais", "estan", "estaba", "estuve", "este", "estar", "estado"}
_PREPOSITIONS = {"a", "en", "de", "por", "para", "con", "sin", "sobre", "desde", "hasta", "entre", "hacia"}
_CLITICS = {"me", "te", "se", "le", "les", "lo", "la", "los", "las", "nos", "os"}

# Order = "most important error first" when LT finds several (contract: ONE correction).
_PRIORITY = ["ser_estar", "gender", "article", "agreement", "preposition", "clitic", "mood",
             "tense_aspect", "lexical", "spelling_accent"]

_RU_LABEL = {
    "spelling_accent": "Орфография / ударение", "gender": "Род существительного",
    "article": "Артикль", "agreement": "Согласование", "ser_estar": "ser / estar",
    "preposition": "Предлог", "clitic": "Местоимение", "lexical": "Слово",
    "mood": "Наклонение", "tense_aspect": "Время",
}


class CheckerError(RuntimeError):
    """Network error / 429 / bad answer from the LT server."""


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def _words(text: str) -> List[str]:
    return [w for w in "".join(c if c.isalnum() else " " for c in _fold(text)).split()]


def lt_language(target: str) -> str:
    """'es-ES' → 'es' (LT's generic Spanish); other variants LT knows are kept."""
    code = (target or "es").strip()
    return {"es-ES": "es", "es": "es"}.get(code, code)


def classify(match: Dict[str, Any], fragment: str, replacement: str,
             mother_tongue: Optional[str] = None) -> Tuple[Optional[str], bool]:
    """(error_category or None to drop the match, is_transfer)."""
    rule = match.get("rule") or {}
    rule_id = str(rule.get("id", "")).upper()
    cat_id = str((rule.get("category") or {}).get("id", "")).upper()
    issue = str(rule.get("issueType", "")).lower()

    if "FALSE_FRIEND" in rule_id or cat_id == "FALSE_FRIENDS":
        return "lexical", bool(mother_tongue)
    adds_marks = any(c in replacement for c in "¿¡") and not any(c in fragment for c in "¿¡")
    if adds_marks or (fragment and _fold(fragment) == _fold(replacement)):
        return "spelling_accent", False          # only accents / ¿ ¡ / case changed
    if cat_id in _SKIP_CATEGORIES or issue in _SKIP_ISSUES:
        return None, False
    if issue == "misspelling" or cat_id == "TYPOS" or rule_id.startswith(("MORFOLOGIK", "HUNSPELL")) \
            or "DIACRITIC" in rule_id or "TILDE" in rule_id:
        return "spelling_accent", False

    a, b = _words(fragment), _words(replacement)
    changed_a, changed_b = set(a) - set(b), set(b) - set(a)
    changed = changed_a | changed_b
    if changed and changed <= _SER_ESTAR:
        return "ser_estar", False
    art_a, art_b = [w for w in a if w in _ARTICLES], [w for w in b if w in _ARTICLES]
    if art_a and art_b and ((art_a[0] in _MASC and art_b[0] in _FEM) or (art_a[0] in _FEM and art_b[0] in _MASC)):
        return "gender", False                   # la problema → el problema, a la cero → al cero
    if changed and changed <= _ARTICLES:
        return "article", False
    if changed and changed <= _PREPOSITIONS:
        return "preposition", False
    if changed and changed <= _CLITICS:
        return "clitic", False
    if "CONCORD" in rule_id or "AGREEMENT" in rule_id or "CONCORD" in cat_id:
        return "agreement", False
    if len(a) == len(b) and any(x != y and x[:-1] == y[:-1] for x, y in zip(a, b)):
        return "agreement", False                # same stem, other ending (-o → -a, -s)
    if cat_id in {"GRAMMAR", "GRAMATICA"} or issue == "grammar":
        return "agreement", False
    return None, False


def matches_to_correction(text: str, matches: List[Dict[str, Any]],
                          mother_tongue: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Kept LT matches → one correction (contract of core/feedback.py) or None."""
    kept = []
    for m in matches:
        reps = m.get("replacements") or []
        if not reps or not isinstance(reps[0], dict) or reps[0].get("value") is None:
            continue
        off, length = int(m.get("offset", 0)), int(m.get("length", 0))
        fragment, repl = text[off:off + length], str(reps[0]["value"])
        if fragment == repl:
            continue
        category, transfer = classify(m, fragment, repl, mother_tongue)
        if category:
            kept.append((off, length, repl, category, transfer, str(m.get("message", "")).strip()))
    if not kept:
        return None
    corrected, last = text, None
    for off, length, repl, *_ in sorted(kept, key=lambda k: k[0], reverse=True):
        if last is not None and off + length > last:
            continue                             # overlapping match: keep the later one only
        corrected, last = corrected[:off] + repl + corrected[off + length:], off
    main = min(kept, key=lambda k: _PRIORITY.index(k[3]))
    _, _, _, category, transfer, message = main
    explanation = _RU_LABEL.get(category, "Ошибка") + (f" (LanguageTool: «{message}»)" if message else "")
    return {"original": text, "corrected": corrected, "error_category": category,
            "cf_type": "explicit", "is_transfer": transfer,
            "transfer_source": mother_tongue if transfer else None, "explanation": explanation}


class LanguageToolChecker:
    name = "languagetool"

    def __init__(self, url: Optional[str] = None, *, timeout: float = 10.0,
                 min_interval_s: Optional[float] = None, client: Optional[httpx.Client] = None,
                 clock: Callable[[], float] = time.monotonic, sleeper: Callable[[float], None] = time.sleep):
        self.url = (url or os.getenv("LANGUAGETOOL_URL") or PUBLIC_URL).rstrip("/")
        self.is_public = "api.languagetool.org" in self.url
        # Public API: ~20 requests/min per IP → one call every 3.5 s at most.
        self.min_interval_s = (3.5 if self.is_public else 0.0) if min_interval_s is None else min_interval_s
        self.model_name = "public" if self.is_public else "local"
        self._client = client or httpx.Client(timeout=timeout)
        self._clock, self._sleeper, self._last = clock, sleeper, None

    def is_configured(self) -> bool:
        try:
            return self._client.get(f"{self.url}/languages").status_code == 200
        except Exception:
            return False

    def _wait(self) -> None:
        if self._last is not None and self.min_interval_s > 0:
            left = self.min_interval_s - (self._clock() - self._last)
            if left > 0:
                self._sleeper(left)
        self._last = self._clock()

    def check(self, text: str, target: str = "es", mother_tongue: Optional[str] = None) -> Optional[Dict[str, Any]]:
        text = (text or "").strip()
        if not text or len(text) > MAX_CHARS:
            return None
        data = {"text": text, "language": lt_language(target)}
        if mother_tongue:
            data["motherTongue"] = mother_tongue     # enables LT's false-friend rules
        self._wait()
        try:
            resp = self._client.post(f"{self.url}/check", data=data)
        except httpx.HTTPError as e:
            raise CheckerError(f"languagetool: {type(e).__name__}: {e}") from e
        if resp.status_code != 200:
            raise CheckerError(f"languagetool HTTP {resp.status_code}: {resp.text[:200]}")
        try:
            matches = resp.json().get("matches") or []
        except ValueError as e:
            raise CheckerError("languagetool: answer is not JSON") from e
        return matches_to_correction(text, matches, mother_tongue)


def combine(llm_correction: Optional[Dict[str, Any]],
            lt_correction: Optional[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], bool]:
    """Pre-check policy "fill": the LLM's correction wins; LanguageTool only fills
    turns where the LLM gave none. Returns (correction, filled_by_lt)."""
    if llm_correction:
        return llm_correction, False
    return (lt_correction, True) if lt_correction else (None, False)
