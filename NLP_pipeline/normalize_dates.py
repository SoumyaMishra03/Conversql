#!/usr/bin/env python3
"""
normalize_dates.py

Detects fuzzy date expressions in text and converts them
to ISO 'YYYY-MM-DD'. Returns (new_text, conversions).
Relies on python-dateutil for parsing.
"""

import re
import sys
import subprocess

# 1) Ensure dateutil is available
try:
    from dateutil import parser as _p
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dateutil"])
    from dateutil import parser as _p

# 2) Patterns to locate candidate date substrings
_DATE_PATTERNS = [
    r"\b\d{4}-\d{2}-\d{2}\b",                 # 2025-06-23
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",           # 6/23/2025 or 06/23/25
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
      r"[a-z]*\s+\d{1,2}(?:,\s*\d{4})?\b"      # Jan 5, 2020 or january 5
]
_DATE_REGEX = re.compile("|".join(_DATE_PATTERNS), flags=re.IGNORECASE)

def normalize_dates(text: str):
    """
    Finds all date substrings, parses them, and converts to ISO format.
    Returns (new_text, conversions).
    conversions: list of dicts {
      raw:          original date text,
      start:        start idx,
      end:          end idx,
      normalized:   'YYYY-MM-DD'
    }
    """
    conversions = []
    offset = 0
    new_text = text

    for m in _DATE_REGEX.finditer(text):
        raw = m.group(0)
        lo, hi = m.span()
        try:
            dt = _p.parse(raw, dayfirst=False, fuzzy=True)
            iso = dt.date().isoformat()
        except Exception:
            continue
        conversions.append({
            'raw': raw,
            'start': lo,
            'end': hi,
            'normalized': iso
        })
        # replace in new_text
        repl = iso
        adj_lo = lo + offset
        adj_hi = hi + offset
        new_text = new_text[:adj_lo] + repl + new_text[adj_hi:]
        offset += len(repl) - len(raw)

    return new_text, conversions

# Self-test
if __name__ == "__main__":
    samples = [
        "Event on 2025-06-23 should be logged.",
        "Deadline: 6/23/2025 or 06/23/25 variant.",
        "Meeting Jan 5, 2020 was moved.",
        "Backup date feb 12 without year.",
        "Nothing here."
    ]

    for s in samples:
        print(f"\nInput:  {s}")
        nt, conv = normalize_dates(s)
        print("Output: ", nt)
        for c in conv:
            print(f"  • {c['raw']} → {c['normalized']} [{c['start']}–{c['end']}]")
