#!/usr/bin/env python3
"""
main.py

Orchestrates the pipeline (sans link_entities and synonym_mapping):
  1. normalize_dates
  2. normalize_units
  3. tokenize (Stanza)
  4. schema_entity_recognizer
  5. comparison_operator_recognizer
  6. value_entity_recognizer
"""

import re

from tokenizer_stanza import tokenize, SCHEMA_PHRASES
from schema_entity_recognizer import schema_entity_recognizer
from comparison_operator_recognizer import comparison_operator_recognizer
from value_entity_recognizer import value_entity_recognizer
from normalize_units import normalize_units
from normalize_dates import normalize_dates

# treat 4-digit integers as dates
YEAR_PATTERN = re.compile(r"^\d{4}$")

queries = [
    "List all astronauts who participated in missions and logged eva_hrs_missions above 10.",
    "Show me the satellites launched after 2010 that orbit around Mars.",
    "Which rockets were flying and carrying payloads heavier than 5000 kg?",
    "Find the rocket with the highest payload_leo from rockets_db.",
    "What are the most luminous stars in the stars_db?",
    "Display star names, distances and luminosities of stars closer than 50 light years.",
    "Give details about organizations operating missions in the space_missions_db.",
    "Which astronauts were selected in 2005 and went on missions later?",
    "What satellites were operated by ISRO and launched in 2019?",
    "Give me the albedo values for satellites that were orbiting Jupiter.",
    "Tell me which missions have been completed by NASA astronauts.",
    "I'm curious about the perihelion times and orbit id from orbit_data in asteroids."
]

for query in queries:
    print("=" * 80)
    print("Original Query:")
    print(" ", query)

    # 1. Normalize dates
    text_dates, date_conversions = normalize_dates(query)
    if date_conversions:
        print("\nAfter date normalization:")
        print(" ", text_dates)
        print("  Date conversions:")
        for c in date_conversions:
            print(f"    • '{c['raw']}' → {c['normalized']} [{c['start']}–{c['end']}]")
    else:
        text_dates = query

    # 2. Normalize units
    text_units, unit_conversions = normalize_units(text_dates)
    if unit_conversions:
        print("\nAfter unit normalization:")
        print(" ", text_units)
        print("  Unit conversions:")
        for c in unit_conversions:
            print(f"    • '{c['raw']}' → {c['norm']:.3f} m [{c['start']}–{c['end']}]")
    else:
        text_units = text_dates

    # 3. Tokenize & filter
    tok = tokenize(text_units)
    final_tokens = tok["Final Tokens"]
    print("\nFinal Tokens:")
    print(" ", final_tokens)

    # 4. Schema entity recognition
    schema_entities = schema_entity_recognizer(final_tokens, SCHEMA_PHRASES)
    print("\nSchema Entities:")
    if schema_entities:
        for ent in schema_entities:
            print(f"   • {ent}")
    else:
        print("   None found")

    # 5. Comparison operator recognition
    raw_ops = comparison_operator_recognizer(text_units)
    print("\nComparison Operators:")
    if raw_ops:
        for op, raw, lo, hi in raw_ops:
            print(f"   • {{'operator': '{op}', 'raw': '{raw}', 'span': ({lo},{hi})}}")
    else:
        print("   None found")

    # 6. Value entity recognition
    raw_vals = value_entity_recognizer(text_units)
    val_entities = []
    for typ, val, lo, hi in raw_vals:
        if typ == "STRING":
            continue
        if typ == "INTEGER" and YEAR_PATTERN.match(val):
            typ = "DATE"
        val_entities.append({
            "type": typ,
            "value": val,
            "span": (lo, hi)
        })

    print("\nValue Entities:")
    if val_entities:
        for v in val_entities:
            print(f"   • {v}")
    else:
        print("   None found")

    print("\n")
