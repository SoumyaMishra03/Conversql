import re
from typing import List, Tuple

DATE_PATTERNS = [
    r"\b\d{4}-\d{2}-\d{2}\b",
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:,\s*\d{4})?\b"
]
FLOAT_PATTERN = r"\b-?\d+\.\d+\b"
INTEGER_PATTERN = r"\b-?\d+\b"
BOOLEAN_PATTERN = r"\b(?:true|false|yes|no)\b"
STRING_PATTERN = r"'([^']*)'|\"([^\"]*)\""

VALUE_REGEX = re.compile(
    "(" + "|".join(DATE_PATTERNS + [FLOAT_PATTERN, INTEGER_PATTERN, BOOLEAN_PATTERN, STRING_PATTERN]) + ")",
    flags=re.IGNORECASE
)

def value_entity_recognizer(text: str) -> List[Tuple[str, str, int, int]]:
    results: List[Tuple[str, str, int, int]] = []
    for m in VALUE_REGEX.finditer(text):
        raw = m.group(0)
        lo, hi = m.span()
        if re.fullmatch(FLOAT_PATTERN, raw):
            typ = "FLOAT"
        elif re.fullmatch(INTEGER_PATTERN, raw):
            typ = "INTEGER"
        elif re.fullmatch(BOOLEAN_PATTERN, raw, flags=re.IGNORECASE):
            typ = "BOOLEAN"
        elif re.fullmatch(STRING_PATTERN, raw):
            typ = "STRING"
            raw = raw[1:-1]
        else:
            typ = "DATE"
        results.append((typ, raw, lo, hi))
    return results
