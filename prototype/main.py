import re
import getpass
from NLP_pipeline.tokenizer_stanza import tokenize, SCHEMA_PHRASES
from NLP_pipeline.schema_entity_recognizer import schema_entity_recognizer
from NLP_pipeline.comparison_operator_recognizer import comparison_operator_recognizer
from NLP_pipeline.value_entity_recognizer import value_entity_recognizer
from NLP_pipeline.normalize_units import normalize_units
from NLP_pipeline.normalize_dates import normalize_dates
from NLP_pipeline.intent_recognizer import IntentRecognizer
from Query_Builder.template_query_builder import build_query
from Query_Builder.query_verifier import verify_query
from Query_Builder.query_logger import log_query
from Query_Builder.users_manager import get_user
from Query_Builder.rbac import validate_query_access, explain_denial

YEAR_PATTERN = re.compile(r"^\d{4}$")
intent_recognizer = IntentRecognizer()

username = input("Username: ")
password = getpass.getpass("Password: ")
user = get_user(username, password)

if not user:
    print("Invalid credentials. Exiting.")
    exit()

print(f"\nWelcome, {user['username']}! Role: {user['role']}")
print("Type your queries (or 'exit' to quit).")

# Batch mode - uncomment to run all at once
"""
queries = [
    "List all neo_reference data.",
    "Show close_approach information.",
    "Display everything in orbit_data.",
    "Count records in orbit_data.",
    "What is the average eccentricity in orbit_data.",
    "Show all personal_info records.",
    "Give me the total number of astronauts in personal_info.",
    "List names and year_of_birth from personal_info.",
    "Display satellite_identity details.",
    "List data in satellite_physical.",
    "Show the average launch mass in satellite_physical.",
    "List all entries in basic_info.",
    "Show orbital_info data.",
    "Give me rocket_general_info records.",
    "Display rocket_technical_specs.",
    "What is the total sum of liftoff_thrust in rocket_general_info.",
    "List organizations.",
    "Show all rockets data.",
    "Display missions.",
    "Count missions.",
    "List news_articles_table entries.",
    "Show publishing_info.",
    "List all stars.",
    "Show the maximum luminosity in stars.",
    "What is the average mass in stars.",
    "Show orbit_data where eccentricity is greater than 0.5.",
    "Find close_approach records where miss dist.(kilometers) is less than 100000.",
    "List neo_reference entries where absolute magnitude is more than 22.",
    "Find personal_info where year_of_birth is before 1970.",
    "Show astronauts in personal_info where total_number_of_missions is above 3.",
    "List satellite_physical data where launch mass (kg.) exceeds 2000.",
    "Show satellite_identity where purpose is 'communication'.",
    "Display rocket_general_info where price is over 50.",
    "Find rocket_technical_specs where payload_leo is greater than 10000.",
    "Show missions where mission_status is 'completed'.",
    "List news_articles_table where date is after '2020-01-01'.",
    "Show stars where mass is below 2.",
    "Find stars where luminosity exceeds 5000."
]
for q in queries:
"""
while True:
    q = input("\n> ")
    if not q.strip() or q.lower() == "exit":
        print("Goodbye.")
        break

    print("=" * 100)
    print("Original Query:\n ", q)

    t1, dates = normalize_dates(q)
    t2, units = normalize_units(t1 if dates else q)
    tok = tokenize(t2 if units else t1)
    final_tokens = tok["Final Tokens"]
    print("\nFinal Tokens:\n ", final_tokens)

    intent = intent_recognizer.predict_from_tokens(final_tokens)
    print("\nIntent:\n ", intent)

    ents = schema_entity_recognizer(final_tokens, SCHEMA_PHRASES)
    print("\nSchema Entities:\n ", ents or "None")

    ops_raw = comparison_operator_recognizer(t2)
    ops = [(raw, op) for op, raw, _, _ in ops_raw]
    print("\nComparison Operators:\n ", ops or "None")

    raw_vals = value_entity_recognizer(t2)
    vals = []
    for typ, val, lo, hi in raw_vals:
        if typ == "STRING":
            continue
        if typ == "INTEGER" and YEAR_PATTERN.match(val):
            typ = "DATE"
        vals.append({"type": typ, "value": val, "span": (lo, hi)})
    print("\nValue Entities:\n ", vals or "None")

    query_str = build_query(
        intent, ents, ops, vals,
        db_host='localhost', db_user='root', db_pass='root'
    )
    print("\nGenerated SQL Query:\n", query_str)

    if query_str.startswith("ERROR"):
        db = "unknown"
        print("\nCould not build SQL query:", query_str)
        log_query(user["username"], user["role"], q, db, "read", sql=query_str)
        continue

    if "FROM" in query_str:
        db = query_str.split("FROM")[1].split()[0].split(".")[0].strip("`")
    else:
        db = "unknown"

    if not validate_query_access(user["role"], db):
        reason = explain_denial(user["role"], db)
        print("\nACCESS DENIED:", reason)
        log_query(user["username"], user["role"], q, db, "denied", sql=query_str)
        continue

    success, result = verify_query(
        query_str,
        host='localhost',
        user='root',
        password='root'
    )

    if success:
        print("\nQuery executed successfully. Sample rows:\n", result[:3])
        log_query(user["username"], user["role"], q, db, "read", sql=query_str)
    else:
        print("\nQuery failed to execute:\n", result)
        log_query(user["username"], user["role"], q, db, "read", sql=query_str)
