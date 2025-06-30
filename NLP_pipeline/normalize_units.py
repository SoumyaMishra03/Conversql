import re

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

_PATTERN = re.compile(
    r"\b(?P<val>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>km|kilometer[s]?|m|meter[s]?|cm|centimeter[s]?|"
    r"mm|millimeter[s]?|mi|mile[s]?|ft|foot|feet)\b",
    flags=re.IGNORECASE
)

def normalize_units(text: str):
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
        repl = f"{norm:.3f} m"
        adj_lo = lo + offset
        adj_hi = hi + offset
        new_text = new_text[:adj_lo] + repl + new_text[adj_hi:]
        offset += len(repl) - len(raw)

    return new_text, conversions


