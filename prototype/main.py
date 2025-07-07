#!/usr/bin/env python3

import re
import getpass
from datetime import datetime, timedelta

from NLP_pipeline.tokenizer_stanza             import tokenize, SCHEMA_PHRASES
from NLP_pipeline.normalize_dates              import normalize_dates
from NLP_pipeline.normalize_units              import normalize_units
from NLP_pipeline.intent_recognizer            import IntentRecognizer
from NLP_pipeline.schema_entity_recognizer     import schema_entity_recognizer
from NLP_pipeline.comparison_operator_recognizer import comparison_operator_recognizer
from NLP_pipeline.value_entity_recognizer      import value_entity_recognizer

from Query_Builder.users_manager import get_user
from Query_Builder.query_logger   import log_query, log_access, fetch_access_logs
from Query_Builder.rbac           import validate_query_access, explain_denial
from Query_Builder.template_query_builder import build_query
from Query_Builder.query_verifier    import verify_query

YEAR_PATTERN      = re.compile(r"^\d{4}$")
intent_recognizer = IntentRecognizer()
_failed_logins    = {}  # username -> {count, lock_until}

def login_prompt():
    """
    Prompt for username/password. Lock out after 3 failures for 5 minutes.
    """
    while True:
        username = input("👤 Username: ").strip()
        if username.lower() in {"exit", "quit"}:
            print("🔚 Goodbye!")
            exit(0)

        info = _failed_logins.get(username, {"count": 0, "lock_until": None})
        if info["lock_until"] and datetime.now() < info["lock_until"]:
            wait = (info["lock_until"] - datetime.now()).seconds
            print(f"🚫 {username} locked. Try again in {wait//60}m{wait%60}s.")
            continue

        password = getpass.getpass("🔒 Password: ")
        user = get_user(username, password)
        if user:
            _failed_logins.pop(username, None)
            print(f"\n✅ Welcome {user['username']} (role: {user['role']})")
            log_access(username, "LOGIN_SUCCESS")
            return user

        # failed login
        info["count"] += 1
        log_access(username, "LOGIN_FAILURE")
        if info["count"] >= 3:
            info["lock_until"] = datetime.now() + timedelta(minutes=5)
            print("🚨 3 invalid attempts. Locked for 5 minutes.")
            log_access(username, "LOCKOUT")
        else:
            print("🚫 Invalid credentials. Try again.")
        _failed_logins[username] = info

def handle_query(user):
    """
    Normalize input, build SQL, run RBAC, execute, and log.
    """
    raw = input("\n🗣️ Enter your query: ").strip()
    if not raw:
        print("🚫 Empty query.")
        return

    # Normalize dates & units
    t1, dates = normalize_dates(raw)
    t2, units = normalize_units(t1 if dates else raw)

    # Tokenize
    final_tokens = tokenize(t2 if units or dates else raw)["Final Tokens"]
    print("🧾 Final Tokens:", final_tokens)

    # Intent
    intent = intent_recognizer.predict_from_tokens(final_tokens)
    print("🎯 Intent:", intent)

    # Schema entities
    ents = schema_entity_recognizer(final_tokens, SCHEMA_PHRASES) or []
    print("📦 Schema Entities:", ents or "None")

    # Comparison operators
    ops_raw = comparison_operator_recognizer(t2) or []
    ops = [(rawop, op) for op, rawop, _, _ in ops_raw]
    print("⚙️ Comparison Operators:", ops or "None")

    # Value entities
    raw_vals = value_entity_recognizer(t2) or []
    vals = []
    for typ, val, lo, hi in raw_vals:
        if typ == "STRING":
            continue
        if typ == "INTEGER" and YEAR_PATTERN.match(val):
            typ = "DATE"
        vals.append({"type": typ, "value": val, "span": (lo, hi)})
    print("🔢 Value Entities:", vals or "None")

    # Build SQL
    sql = build_query(intent, ents, ops, vals)
    print("📝 Generated SQL:\n", sql)
    if sql.startswith("ERROR:"):
        print("🚫", sql)
        log_query(user["username"], user["role"], raw, "unknown", "fail", sql)
        return

    # Extract target DB
    m1 = re.search(r'FROM\s+`([^`]+)`\.`([^`]+)`', sql, re.IGNORECASE)
    if m1:
        db = m1.group(1)
    else:
        m2 = re.search(r'SHOW\s+TABLES\s+FROM\s+`([^`]+)`', sql, re.IGNORECASE)
        if m2:
            db = m2.group(1)
        else:
            part = sql.split("FROM", 1)[1].strip().split()[0]
            db = part.replace("`", "").rstrip(";").split(".")[0]
    print("📂 Inferred DB:", db)

    # RBAC
    if not validate_query_access(user["role"], db):
        reason = explain_denial(user["role"], db)
        print("🚫 ACCESS DENIED:", reason)
        log_query(user["username"], user["role"], raw, db, "denied", sql)
        return

    # Execute
    success, result = verify_query(
        sql,
        host='localhost',
        user='root',
        password='Helloworld@2025',  # update as needed
        database=db
    )
    if success:
        print("\n✅ Executed OK. Sample rows:\n", result[:3])
        log_query(user["username"], user["role"], raw, db, "read", sql)
    else:
        print("\n❌ Execution error:\n", result)
        log_query(user["username"], user["role"], raw, db, "fail", sql)

def repl(user):
    """
    Numeric menu: query, switch, exit, and admin-only options.
    """
    role = user["role"]
    while True:
        print("\nSelect an action:")
        print("  1) Enter a natural-language query")
        print("  2) Switch user")
        print("  3) Exit")
        if role == "admin":
            print("  4) Show recent access logs")
            print("  5) Lock out a user")
        choice = input("> ").strip()

        if choice == "1":
            handle_query(user)
        elif choice == "2":
            print("🔄 Switching user…")
            return
        elif choice == "3":
            print("🔚 Goodbye!")
            exit(0)
        elif role == "admin" and choice == "4":
            logs = fetch_access_logs(20)
            print("\n📋 Recent Access Log:")
            print("ID | Username | Event Time          | Status")
            print("---+----------+----------------------+----------------")
            for row in logs:
                print(f"{row[0]:<2} | {row[1]:<8} | {row[2]} | {row[3]}")
        elif role == "admin" and choice == "5":
            target = input("Enter username to lock out: ").strip()
            dur_str = input("Enter lockout duration (minutes): ").strip()
            try:
                minutes = int(dur_str)
                until = datetime.now() + timedelta(minutes=minutes)
                _failed_logins[target] = {"count": 999, "lock_until": until}
                log_access(target, f"ADMIN_LOCKOUT_{minutes}m")
                print(f"🔒 User '{target}' locked out until {until:%Y-%m-%d %H:%M:%S}")
            except ValueError:
                print("🚫 Invalid duration; must be an integer.")
        else:
            print("🚫 Invalid choice. Pick a number from the menu.")

if __name__ == "__main__":
    while True:
        user = login_prompt()
        repl(user)
