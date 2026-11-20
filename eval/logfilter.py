"""Strip `ollama pull` progress bars from the nightly log (docs/feedback/2026-11-16 §3).

    python -m eval.logfilter pull-out.txt [pull-err.txt ...]   # prints the cleaned text

`ollama pull` redraws its progress line many times per second (carriage returns, ANSI
cursor codes, spinner glyphs). Written to a file, one 5 GB model became megabytes of
log (15.11: 19 MB). We keep each distinct status line once and a progress line only
when a layer reaches 100 %, so the log still shows what was pulled and any error.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional

_ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
_SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
_BAR = re.compile(r"[▕▏█▉▊▋▌▍▎ ]{3,}")
_PROGRESS = re.compile(r"^pulling ([0-9a-f]{6,})\.*:?\s.*?(\d{1,3})%")


def clean_pull_output(text: str) -> str:
    out: List[str] = []
    finished = set()
    # ANSI cursor moves separate redraws just like \r does.
    for raw in re.split(r"[\r\n]+", _ANSI.sub("\n", text)):
        line = raw.strip().strip(_SPINNER).strip()
        if not line:
            continue
        m = _PROGRESS.match(line)
        if m:
            digest, pct = m.group(1), int(m.group(2))
            if pct < 100 or digest in finished:
                continue
            finished.add(digest)
            line = re.sub(r"\s+", " ", _BAR.sub(" ", line)).strip()
        if out and out[-1] == line:
            continue
        out.append(line)
    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    paths = argv if argv is not None else sys.argv[1:]
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for p in paths:
        path = Path(p)
        if path.exists():
            cleaned = clean_pull_output(path.read_text(encoding="utf-8", errors="replace"))
            if cleaned:
                print(cleaned)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
