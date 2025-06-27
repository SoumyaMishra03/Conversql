#!/usr/bin/env python3
"""
main.py

Demo pipeline with:
 • Spell-correction via LanguageTool
 • Date & unit normalization
 • Tokenize, intent, schema/operator/value recognition
"""

import re
from spell_corrector import correct_query
from tokenizer_stanza import tokenize, SCHEMA_PHRASES
from schema_entity_recognizer import schema_entity_recognizer
from comparison_operator_recognizer import comparison_operator_recognizer
from value_entity_recognizer import value_entity_recognizer
from normalize_units import normalize_units
from normalize_dates import normalize_dates
from intent_recognizer import IntentRecognizer

YEAR_PATTERN = re.compile(r"^\d{4}$")
intent_recognizer = IntentRecognizer()

# A broader set of typo-rich queries to validate spell correction
queries = [
    # Asteroids
    "How many astroids have an absolute magnitude less then 5?",
    "Show me astroid names and est dia in km(max) for those larger than 2 km.",

    # Stars
    "What is teh average mass of stars in stars_db?",
    "List the topfive most luminous stars.",

    # Astronauts
    "Give me the count of astronots selected in 2005.",
    "Show mission_title and hours_mission for astronot number 42.",

    # ISRO Satellites
    "Descrbe table basic_info in isro_satellites_db.",
    "What was the launch date of the Chandrayaan2 sattelite?",

    # Natural Satellites
    "Display all natural satellits with radius > 1000 km.",
    "What is the minimun gm value among natural satellites?",

    # Rockets
    "Find rockets with payload_GTO above two tons.",
    "List rocket names with liftoff thrst above 5000 kN.",

    # Space News
    "List news headlines publshed after Jan 1 2020.",
    "Count the number of news articels related to Marss.",

    # Space Missions
    "Which space missions cost more than 100 millon dollars?",
    "List organisations in space_missins_db.",

    # Mixed
    "Whats the sum of total_hrs_sum for NASA astronuts?",
    "Show me data for rockets_db and astronauts_db in one query.",
    "Describe the schema of stars and space_news tables please.",
    "Find missions launchd between 2015 and twenty twenty.",

    "Count asteroids discovered aftr 2015.",
    "Show nead earth obects with miss_dist.(kilometers) less than 0.05.",
    "List asteroids with orbiting bodi equal Mars.",
    "Find all near earth object entres where hazardous is true.",
    "How many astroids have a perihelion dist less then 1 AU?",
    "Display est dia in miles(max) for asteroids_db.",
    "List the brightest stras within 50 light years.",
    "What is the callibrated lumiosity of Vega?",
    "Count stars in stars_db with mass under 2 solar mass.",
    "How many astronots over the age of fifty are in personal_info?",
    "Show me persnol_info for astronaut number seven.",
    "Give me the average year_of_selection for astronots.",
    "List satelites operators in isro_satellites_db.",
    "Count isro satellits launched befor 2000.",
    "What is the mean motion of natural satellits_db entries?",
    "Display radiuss of all moons of Saturn in natural_satellites_db.",
    "Slect rocket_general_info from rockets_db where stages > 2.",
    "List ricket names with strap_ons count greater then 3.",
    "Find rockets with fairing_diameter_m above five.",
    "Get me lastest news atlesst from 2021 in space_news_db.",
    "Count the news articels releated to Mars in spacenews_db.",
    "Which space misssions cost under 50 million dollars?",
    "List missons launced between 2010 and 2020 by SpaceX.",
    "Find missions out of space_missions_db with mission_status = completed.",
    "Show me data for stars_db and rockets_db in sinlge query.",
    "Descrbe both stars and astronuts tables.",
    "Whats the averge orbit period of asteroids_db?",
    "How many orbit_data entres have eccentricity > 0.1?",
    "List neo_reference enrties with hazardous flagged as true.",
    "Show news about SpeceX launches in 2020.",
    "List Chandrayaan-3 launch detials.",
    "Find information on Neel Armstrong's missions.",
    "Count articles mentioning Barack Obma in news_articles_table.",
    "Display data on Chang'e 5 sattelite in isro_satellites_db.",
    "Show me data for NASA and ISRO collaborations.",
    "Mention articles about the Persevarance rover landing.",
    "List asteroids discovered by Jpl.",
    "Give me details of the James Webb Space Teliscope mission.",
    "How many observations of Betelgeuse evidences in stars_db?",
    "List exoplanets discovered by Nasa in 2021.",
    "Find entries where orbital mechanics professor Neil deGrasse Tyson is mentioned.",
    "Show me articles by Marie Curie in space_news_db.",
    "List missions funded by European Space Agency.",
    "Display all entries for the International Space Station.",
    "Fetch data about the Hubble Space Telescop imaging results.",
    "Count articles on Curiosity rover in space_news_db.",
    "List all rovers Curiosity, Perseverance, and Spirit.",
    "Give me info on Space Shuttle Challenger accident.",
    "Show me data about Apollo 11 mission crew.",
    "Find articles about the Sputnik 1 mission.",
    "Slect all entries where country of operator = Russia.",
    "List rusian satellite launches in the 1960s.",
    "Count comets in close_approach with miss_dist.(astronomical) < 0.1.",
    "Display news about the Persephone probe (if it existed).",
]
for q in queries:
    print("=" * 80)
    print("Original Query:\n ", q)

    # 0) Spell-correction
    corrected = correct_query(q)
    if corrected != q:
        print("\nAfter spell-correction:\n ", corrected)
    else:
        corrected = q

    # 1) Date normalization
    t1, dates = normalize_dates(corrected)
    if dates:
        print("\nAfter date normalization:\n ", t1)

    # 2) Unit normalization
    t2, units = normalize_units(t1)
    if units:
        print("\nAfter unit normalization:\n ", t2)

    # 3) Tokenize
    tok = tokenize(t2)
    final_tokens = tok["Final Tokens"]
    print("\nFinal Tokens:\n ", final_tokens)

    # 4) Intent recognition
    intent = intent_recognizer.predict_from_tokens(final_tokens)
    print("\nIntent:\n ", intent)

    # 5) Schema entity recognition
    ents = schema_entity_recognizer(final_tokens, SCHEMA_PHRASES)
    print("\nSchema Entities:\n ", ents or "None")

    # 6) Operator recognition
    ops = comparison_operator_recognizer(t2)
    print("\nComparison Operators:\n ", ops or "None")

    # 7) Value recognition
    raw_vals = value_entity_recognizer(t2)
    vals = []
    for typ, val, lo, hi in raw_vals:
        if typ == "STRING": continue
        if typ == "INTEGER" and YEAR_PATTERN.match(val):
            typ = "DATE"
        vals.append({"type": typ, "value": val, "span": (lo, hi)})
    print("\nValue Entities:\n ", vals or "None\n")