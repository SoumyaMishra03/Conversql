import re
from typing import List, Tuple

OPERATOR_PATTERNS = {
    ">=": [
        r"greater\s+than\s+or\s+equal\s+to",
        r"at\s+least",
        r"no\s+less\s+than",
        r"minimum",
        r"≥",
        r">="
    ],
    "<=": [
        r"less\s+than\s+or\s+equal\s+to",
        r"at\s+most",
        r"no\s+more\s+than",
        r"maximum",
        r"≤",
        r"<="
    ],
    "!=": [
        r"not\s+equal\s+to",
        r"!=",
        r"<>"
    ],
    ">": [
        r"greater\s+than",
        r"more\s+than",
        r"above",
        r"over",
        r">"
    ],
    "<": [
        r"less\s+than",
        r"below",
        r"under",
        r"<"
    ],
    "=": [
        r"equal\s+to",
        r"equals?",
        r"=",
    ]
}

_COMPILED = []
for op, patterns in OPERATOR_PATTERNS.items():
    for pat in patterns:
        regex = re.compile(r"\b" + pat + r"\b", flags=re.IGNORECASE)
        _COMPILED.append((op, regex))
_COMPILED.sort(key=lambda x: len(x[1].pattern), reverse=True)

def comparison_operator_recognizer(text: str) -> List[Tuple[str, str, int, int]]:
    hits = []
    for op, regex in _COMPILED:
        for m in regex.finditer(text):
            raw = m.group(0)
            lo, hi = m.span()
            hits.append((op, raw, lo, hi))
    unique = {}
    for op, raw, lo, hi in hits:
        key = (lo, hi)
        if key not in unique or (hi - lo) > (unique[key][3] - unique[key][2]):
            unique[key] = (op, raw, lo, hi)
    sorted_hits = sorted(unique.values(), key=lambda x: x[2])
    return sorted_hits

