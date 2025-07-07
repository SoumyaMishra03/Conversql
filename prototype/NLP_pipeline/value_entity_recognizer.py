import re
from typing import List, Tuple

FLOAT_PATTERN = r"\b-?\d+\.\d+\b"
INTEGER_PATTERN = r"\b-?\d+\b"
BOOLEAN_PATTERN = r"\b(?:true|false|yes|no)\b"
STRING_PATTERN = r"'([^']*)'|\"([^\"]*)\""
DATE_PATTERNS = [
    r"\b\d{4}-\d{2}-\d{2}\b",
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:,\s*\d{4})?\b"
]

VALUE_REGEX = re.compile(
    "(" + "|".join(
        [FLOAT_PATTERN, INTEGER_PATTERN, BOOLEAN_PATTERN, STRING_PATTERN] + DATE_PATTERNS
    ) + ")",
    flags=re.IGNORECASE
)

def value_entity_recognizer(text: str) -> List[Tuple[str, str, int, int]]:
    results: List[Tuple[str, str, int, int]] = []

    for m in VALUE_REGEX.finditer(text):
        raw = m.group(0)
        lo, hi = m.span()

        raw_clean = raw.strip()

        if re.fullmatch(FLOAT_PATTERN, raw_clean):
            typ = "FLOAT"
        elif re.fullmatch(INTEGER_PATTERN, raw_clean):
            typ = "INTEGER"
        elif re.fullmatch(BOOLEAN_PATTERN, raw_clean, flags=re.IGNORECASE):
            typ = "BOOLEAN"
        elif re.fullmatch(STRING_PATTERN, raw_clean):
            typ = "STRING"
            raw_clean = raw_clean[1:-1]
        elif any(re.fullmatch(pat, raw_clean, flags=re.IGNORECASE) for pat in DATE_PATTERNS):
            typ = "DATE"
        else:
            continue  

        results.append((typ, raw_clean, lo, hi))

    return results
