#!/usr/bin/env python3
"""
normalize_units.py

Detects numeric+unit expressions (km, m, cm, mm, mi, ft) in text,
converts them into meters (m), and returns both the normalized text
and a list of conversion details.
"""

import re
import sys
import subprocess

# 1) Ensure nothing shadows our unit module
#    (no stanza.py or normalize_units.py conflict)

# 2) Unit conversion factors to meters
_UNIT_FACTORS = {
    'km':       1_000.0,
    'kilometer':1_000.0, 'kilometers':1_000.0,
    'm':        1.0,
    'meter':    1.0,     'meters':    1.0,
    'cm':       0.01,
    'centimeter':0.01,   'centimeters':0.01,
    'mm':       0.001,
    'millimeter':0.001,  'millimeters':0.001,
    'mi':       1609.34,
    'mile':     1609.34, 'miles':     1609.34,
    'ft':       0.3048,
    'foot':     0.3048,  'feet':      0.3048
}

# 3) Regex to find number+unit
_PATTERN = re.compile(
    r"\b(?P<val>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>km|kilometer[s]?|m|meter[s]?|cm|centimeter[s]?|"
    r"mm|millimeter[s]?|mi|mile[s]?|ft|foot|feet)\b",
    flags=re.IGNORECASE
)

def normalize_units(text: str):
    """
    Finds all <number><unit> occurrences and:
      - normalizes each to meters (value_in_meters)
      - returns (new_text, conversions)
    conversions: list of dicts {
      raw:    original text,
      start:  start idx,
      end:    end idx,
      value:  float(original number),
      unit:   normalized unit string,
      norm:   float(value_in_meters)
    }
    """
    conversions = []
    offset = 0
    new_text = text

    for m in _PATTERN.finditer(text):
        raw = m.group(0)
        lo, hi = m.span()
        val = float(m.group('val'))
        unit = m.group('unit').lower()
        fact = _UNIT_FACTORS[unit]
        norm = val * fact
        conversions.append({
            'raw': raw,
            'start': lo,
            'end': hi,
            'value': val,
            'unit': unit,
            'norm': norm
        })
        # replace in new_text, adjusting for prior replacements
        repl = f"{norm:.3f} m"
        adj_lo = lo + offset
        adj_hi = hi + offset
        new_text = new_text[:adj_lo] + repl + new_text[adj_hi:]
        offset += len(repl) - len(raw)

    return new_text, conversions

# Self-test
if __name__ == "__main__":
    samples = [
        "Distance traveled: 5 km and then 300 m.",
        "Tiny gap: 12.5 cm, also 250 mm.",
        "Walked 2 miles, then 10 ft down.",
        "Edge: 1000 millimeters in blueprint.",
        "Nothing to change here."
    ]

    for s in samples:
        print(f"\nInput:  {s}")
        nt, conv = normalize_units(s)
        print("Output: ", nt)
        for c in conv:
            print(f"  • {c['raw']} → {c['norm']:.3f} m [{c['start']}–{c['end']}]")
