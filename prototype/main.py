import re
import getpass
from datetime import datetime, timedelta
from NLP_pipeline.tokenizer_stanza import tokenize, SCHEMA_PHRASES
from NLP_pipeline.schema_entity_recognizer import schema_entity_recognizer
from NLP_pipeline.comparison_operator_recognizer import comparison_operator_recognizer
from NLP_pipeline.value_entity_recognizer import value_entity_recognizer
from NLP_pipeline.normalize_units import normalize_units
from NLP_pipeline.normalize_dates import normalize_dates
from NLP_pipeline.intent_recognizer import IntentRecognizer
from Query_Builder.template_query_builder import build_query
from Query_Builder.query_verifier import verify_query
from Query_Builder.query_logger import log_query, log_access, fetch_access_logs
from Query_Builder.users_manager import get_user
from Query_Builder.rbac import validate_query_access, explain_denial

YEAR_PATTERN = re.compile(r"^\d{4}$")
intent_recognizer = IntentRecognizer()
_failed_logins = {}

def login_prompt():
    while True:
        username = input("Username: ").strip()
        if username.lower() in {"exit", "quit"}:
            exit(0)
        info = _failed_logins.get(username, {"count": 0, "lock_until": None})
        if info["lock_until"] and datetime.now() < info["lock_until"]:
            wait = (info["lock_until"] - datetime.now()).seconds
            print(f"{username} is locked. Try again in {wait//60}m{wait%60}s.")
            continue
        password = getpass.getpass("Password: ")
        user = get_user(username, password)
        if user:
            _failed_logins.pop(username, None)
            log_access(username, "LOGIN_SUCCESS")
            return user
        info["count"] += 1
        log_access(username, "LOGIN_FAILURE")
        if info["count"] >= 3:
            info["lock_until"] = datetime.now() + timedelta(minutes=5)
            print("Too many invalid attempts. Locked for 5 minutes.")
            log_access(username, "LOCKOUT")
        else:
            print("Invalid credentials. Try again.")
        _failed_logins[username] = info

def handle_query(user):
    q = input("\n> ")
    if not q.strip() or q.lower() == "exit":
        print("Goodbye.")
        exit()

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

    query_str, resolved_db = build_query(
        intent, ents, ops, vals,
        db_host='localhost', db_user='root', db_pass='root'
    )
    print("\nGenerated SQL Query:\n", query_str)

    if not validate_query_access(user["role"], resolved_db):
        reason = explain_denial(user["role"], resolved_db)
        print("\nACCESS DENIED:", reason)
        log_query(user["username"], user["role"], q, resolved_db, "denied", sql=query_str)
        return

    success, result = verify_query(
        query_str,
        host='localhost',
        user='root',
        password='root',
        database=resolved_db
    )

    if success:
        print("\nQuery executed successfully. Sample rows:\n", result[:3])
        log_query(user["username"], user["role"], q, resolved_db, "read", sql=query_str)
    else:
        print("\nQuery failed to execute:\n", result)
        log_query(user["username"], user["role"], q, resolved_db, "fail", sql=query_str)

def repl(user):
    role = user["role"]
    while True:
        print("\nSelect an action:")
        print("1) Enter a natural-language query")
        print("2) Switch user")
        print("3) Exit")
        if role == "admin":
            print("4) Show recent access logs")
            print("5) Lock out a user")
        choice = input("> ").strip()
        if choice == "1":
            handle_query(user)
        elif choice == "2":
            return
        elif choice == "3":
            exit(0)
        elif role == "admin" and choice == "4":
            logs = fetch_access_logs(20)
            print("Recent Access Log:")
            print("ID | Username | Event Time | Status")
            for row in logs:
                print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")
        elif role == "admin" and choice == "5":
            target = input("Username to lock out: ").strip()
            dur_str = input("Lockout duration (minutes): ").strip()
            try:
                minutes = int(dur_str)
                until = datetime.now() + timedelta(minutes=minutes)
                _failed_logins[target] = {"count": 999, "lock_until": until}
                log_access(target, f"ADMIN_LOCKOUT_{minutes}m")
                print(f"User '{target}' locked until {until:%Y-%m-%d %H:%M:%S}")
            except ValueError:
                print("Invalid duration.")
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    while True:
        user = login_prompt()
        print(f"\nWelcome, {user['username']}! Role: {user['role']}")
        repl(user)
