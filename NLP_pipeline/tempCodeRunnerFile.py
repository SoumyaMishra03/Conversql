import re
from tokenizer_stanza import tokenize, SCHEMA_PHRASES
from schema_entity_recognizer import schema_entity_recognizer
from comparison_operator_recognizer import comparison_operator_recognizer
from value_entity_recognizer import value_entity_recognizer
from normalize_units import normalize_units
from normalize_dates import normalize_dates
from intent_recognizer import IntentRecognizer

YEAR_PATTERN = re.compile(r"^\d{4}$")
intent_recognizer = IntentRecognizer()

queries = [
    "Show me asteroids with a perihelion distance less than 1 AU.",
    "List comets that came within 0.05 kilometers of Earth.",
    "Find all rockets with fairing diameter above 5 meters.",
    "Display stars with luminosity greater than 5000.",
    "Count the number of astronauts selected before 2000.",
    "Show missions launched between 2010 and 2020.",
    "List missions launched after January 5, 2015.",
    "Count space news articles published after 1/1/2021.",
    "Find stars discovered between 1990-06-01 and 2005-12-31.",
    "What is the average eccentricity in orbit_data?",
    "Give me the total sum of liftoff thrust in rockets_db.",
    "Which satellites were launched before 2020-01-01 by ISRO?",
    "List asteroid names with absolute magnitude more than 22.",
    "Find astronauts who are over the age of 50 in personal_info.",
    "List natural satellites with radius greater than 1000 km.",
    "Display news articles published on Feb 15, 2022.",
    "Show entries where miss_dist.(miles) is less than 0.1.",
    "List stars with mass less than 2 solar mass in stars_db.",
    "Find missions costing more than 100 million dollars.",
    "Display all incometaxreturn entries where eccentricity equals 0.2."
]



for q in queries:
    print("=" * 80)
    print("Original Query:\n ", q)

    t1, dates = normalize_dates(q)
    if dates:
        print("\nAfter date normalization:\n ", t1)
    else:
        t1 = q

    t2, units = normalize_units(t1)
    if units:
        print("\nAfter unit normalization:\n ", t2)
    else:
        t2 = t1

    tok = tokenize(t2)
    final_tokens = tok["Final Tokens"]
    print("\nFinal Tokens:\n ", final_tokens)

    intent = intent_recognizer.predict_from_tokens(final_tokens)
    print("\nIntent:\n ", intent)


    ents = schema_entity_recognizer(final_tokens, SCHEMA_PHRASES)
    print("\nSchema Entities:\n ", ents or "None")

    ops = comparison_operator_recognizer(t2)
    print("\nComparison Operators:\n ", ops or "None")

    raw_vals = value_entity_recognizer(t2)
    vals = []
    for typ, val, lo, hi in raw_vals:
        if typ == "STRING":
            continue
        if typ == "INTEGER" and YEAR_PATTERN.match(val):
            typ = "DATE"
        vals.append({"type": typ, "value": val, "span": (lo, hi)})
    print("\nValue Entities:\n ", vals or "None\n")
