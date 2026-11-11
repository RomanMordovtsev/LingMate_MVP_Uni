"""Rule type shared by all transfer maps (roadmap 1.5)."""
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class TransferRule:
    id: str
    source: str                 # language the learner knows ("ru", "en", "it")
    target: str                 # target language ("es")
    category: str               # one of core.feedback.ERROR_CATEGORIES
    title: str                  # short label in Russian (UI language)
    source_example: str         # in the source language
    target_example: str         # in the target language
    note: Dict[str, str]        # explanation by learner L1 code ("ru", "en")
    prompt_hint: str = ""       # short English line for the system prompt
    kind: str = "negative"      # "negative" | "bridge"
    original_markers: Tuple[str, ...] = ()   # regex on the folded learner text
    corrected_markers: Tuple[str, ...] = ()  # regex on the folded corrected text

    @property
    def specific(self) -> bool:
        return bool(self.original_markers or self.corrected_markers)
