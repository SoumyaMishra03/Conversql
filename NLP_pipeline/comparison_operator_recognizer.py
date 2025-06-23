#!/usr/bin/env python3
"""
comparison_operator_recognizer.py

Scans input text for natural‐language and symbolic comparison phrases,
returning (operator_symbol, raw_phrase, start_idx, end_idx) for each match.
"""

import re
from typing import List, Tuple

# 1) Define mapping from phrases → normalized SQL operators
OPERATOR_PATTERNS = {
    # Order matters: longer phrases first
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

# 2) Precompile regex list, sorted by phrase‐length desc to catch longer first
_COMPILED = []
for op, patterns in OPERATOR_PATTERNS.items():
    for pat in patterns:
        regex = re.compile(r"\b" + pat + r"\b", flags=re.IGNORECASE)
        _COMPILED.append((op, regex))
# Sort by pattern length (longest first) to avoid partial matches
_COMPILED.sort(key=lambda x: len(x[1].pattern), reverse=True)

def comparison_operator_recognizer(text: str) -> List[Tuple[str, str, int, int]]:
    """
    Finds comparison operators in text.
    Returns list of (op_symbol, raw_phrase, start_idx, end_idx).
    """
    hits = []
    for op, regex in _COMPILED:
        for m in regex.finditer(text):
            raw = m.group(0)
            lo, hi = m.span()
            hits.append((op, raw, lo, hi))
    # remove overlaps and duplicates, prefer earlier start and longer raw matches
    unique = {}
    for op, raw, lo, hi in hits:
        key = (lo, hi)
        # keep only the longest match at this span
        if key not in unique or (hi - lo) > (unique[key][3] - unique[key][2]):
            unique[key] = (op, raw, lo, hi)
    # sort by occurrence
    sorted_hits = sorted(unique.values(), key=lambda x: x[2])
    return sorted_hits

# 3) Self-test with diverse samples
if __name__ == "__main__":
    samples = [
        "Show records where mass > 5.2 and height less than 10 meters.",
        "Find entries with age greater than or equal to 21 and score not equal to 100.",
        "Filter results at least 50 items or at most 200 items.",
        "Select rows where temperature ≥ 100 or pressure ≤ 20.",
        "Retrieve data where status equals 'active' and count <> 0.",
        "Get all values over 1000 and below 5000.",
        "Return items with amount more than 100 or amount under 10.",
        "Pick records where price minimum 50 and maximum 150.",
        "Check if flag = true or flag != false."
    ]

    for sample in samples:
        print(f"\nInput: {sample}")
        ops = comparison_operator_recognizer(sample)
        if not ops:
            print("  → No comparison operators found.")
        else:
            print("  → Found comparison operators:")
            for op, raw, lo, hi in ops:
                snippet = sample[lo:hi]
                print(f"     • {op:2s}  '{raw}' at [{lo}:{hi}] → snippet: '{snippet}'")
