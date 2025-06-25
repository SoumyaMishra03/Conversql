#!/usr/bin/env python3
"""
main.py

End‐to‐end pipeline demo with diverse test queries covering:
  • Date normalization
  • Unit normalization
  • Tokenization & intent recognition
  • Schema, operator & value entity recognition
"""

import re

from tokenizer_stanza import tokenize, SCHEMA_PHRASES
from schema_entity_recognizer import schema_entity_recognizer
from comparison_operator_recognizer import comparison_operator_recognizer
from value_entity_recognizer import value_entity_recognizer
from normalize_units import normalize_units
from normalize_dates import normalize_dates

from intent_recognizer import IntentRecognizer

# treat 4-digit integers as dates
YEAR_PATTERN = re.compile(r"^\d{4}$")

# initialize intent recognizer
intent_recognizer = IntentRecognizer()

# Expanded list of queries to exercise every module
queries = [
    # Asteroids
    "How many asteroids have an absolute magnitude less than 5?",
    "Show me asteroid names and est dia in km(max) for those larger than 2 km.",
    "What is the average orbital period of asteroids in days?",

    # Stars
    "What is the average mass of stars in stars_db?",
    "List the top 5 most luminous stars.",
    "List star names within 100 light years of Earth.",

    # Astronauts
    "Give me the count of astronauts selected in 2005.",
    "Show mission_title and hours_mission for astronaut number 42.",
    "Show astronauts who have more than 10 total_eva_hrs.",

    # ISRO Satellites
    "Describe table basic_info in isro_satellites_db.",
    "What was the launch date of the Chandrayaan-2 satellite?",
    "Count satellites with perigee less than 500 km.",

    # Natural Satellites
    "Display all natural satellites with radius greater than 1000 km.",
    "What is the minimum gm value among natural satellites?",

    # Rockets
    "Find rockets with Payload_GTO above 2 tons.",
    "List rocket names with liftoff thrust above 5000 kN.",
    "Describe schema of rocket_technical_specs.",

    # Space News
    "List news headlines published after January 1, 2020.",
    "Count the number of news articles related to Mars.",

    # Space Missions
    "Which space missions cost more than 100 million dollars?",
    "List organizations in space_missions_db.",
    "Tell me which missions have been completed by SpaceX.",
    "Find missions launched between 2015 and 2020.",

    # Mixed / edge cases
    "Show me data for rockets_db and astronauts_db in one query.",
    "Display the schema of stars and space_news tables.",
    "What's the sum of total_hrs_sum for NASA astronauts?",
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
            unit = c.get('unit', 'm')
            print(f"    • '{c['raw']}' → {c['norm']:.3f} {unit} [{c['start']}–{c['end']}]")
    else:
        text_units = text_dates

    # 3. Tokenize & filter
    tok = tokenize(text_units)
    final_tokens = tok["Final Tokens"]
    print("\nFinal Tokens:")
    print(" ", final_tokens)

    # 4. Intent recognition on tokens
    intent = intent_recognizer.predict_from_tokens(final_tokens)
    print("\nIntent:")
    print(" ", intent)

    # 5. Schema entity recognition
    schema_entities = schema_entity_recognizer(final_tokens, SCHEMA_PHRASES)
    print("\nSchema Entities:")
    if schema_entities:
        for ent in schema_entities:
            print(f"   • {ent}")
    else:
        print("   None found")

    # 6. Comparison operator recognition
    raw_ops = comparison_operator_recognizer(text_units)
    print("\nComparison Operators:")
    if raw_ops:
        for op, raw, lo, hi in raw_ops:
            print(f"   • {{'operator': '{op}', 'raw': '{raw}', 'span': ({lo},{hi})}}")
    else:
        print("   None found")

    # 7. Value entity recognition
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
