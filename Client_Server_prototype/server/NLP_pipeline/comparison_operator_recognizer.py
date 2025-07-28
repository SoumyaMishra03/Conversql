import json
import re

with open("NLP_pipeline/json/comparison_operators.json", "r") as f:
    OPERATOR_SYNONYMS = json.load(f)

_COMPILED = []
for op, phrases in OPERATOR_SYNONYMS.items():
    for phrase in phrases:
        p = re.escape(phrase.strip())
        if " " in phrase:
            regex = re.compile(r"\b" + p + r"\b", re.IGNORECASE)
        else:
            regex = re.compile(r"(?<!\w)" + p + r"(?!\w)", re.IGNORECASE)
        _COMPILED.append((op, regex))

_COMPILED.sort(key=lambda x: len(x[1].pattern), reverse=True)

def comparison_operator_recognizer(text):
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
