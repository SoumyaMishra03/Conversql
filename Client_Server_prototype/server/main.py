import re
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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

app = FastAPI()
YEAR_PATTERN = re.compile(r"^\d{4}$")
intent_recognizer = IntentRecognizer()
_failed_logins = {}

class LoginRequest(BaseModel):
    username: str
    password: str

class QueryRequest(BaseModel):
    username: str
    password: str
    query: str

class LockUserRequest(BaseModel):
    admin_user: str
    admin_pass: str
    target_user: str
    duration_minutes: int

@app.post("/login")
def login(data: LoginRequest):
    username = data.username
    password = data.password
    info = _failed_logins.get(username, {"count": 0, "lock_until": None})
    if info["lock_until"] and datetime.now() < info["lock_until"]:
        wait = (info["lock_until"] - datetime.now()).seconds
        raise HTTPException(status_code=403, detail=f"Locked. Try after {wait//60}m{wait%60}s.")
    user = get_user(username, password)
    if user:
        _failed_logins.pop(username, None)
        log_access(username, "LOGIN_SUCCESS")
        return {"message": f"Login successful", "role": user["role"]}
    info["count"] += 1
    log_access(username, "LOGIN_FAILURE")
    if info["count"] >= 3:
        info["lock_until"] = datetime.now() + timedelta(minutes=5)
        log_access(username, "LOCKOUT")
        _failed_logins[username] = info
        raise HTTPException(status_code=403, detail="Too many failed attempts. Locked 5 minutes.")
    _failed_logins[username] = info
    raise HTTPException(status_code=401, detail="Invalid credentials.")

@app.post("/query")
def handle_query(data: QueryRequest):
    user = get_user(data.username, data.password)
    if not user:
        log_access(data.username, "LOGIN_FAILURE_QUERY")
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    q = data.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Empty query.")

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
        log_query(user["username"], user["role"], q, resolved_db, "denied", sql=query_str)
        print("\nACCESS DENIED:", reason)
        raise HTTPException(status_code=403, detail=reason)

    success, result = verify_query(
        query_str,
        host='localhost',
        user='root',
        password='root',
        database=resolved_db
    )

    if success:
        log_query(user["username"], user["role"], q, resolved_db, "read", sql=query_str)
        print("\nQuery executed successfully. Sample rows:\n", result[:5])
        return {"sample_rows": result[:5]}
    else:
        log_query(user["username"], user["role"], q, resolved_db, "fail", sql=query_str)
        print("\nQuery failed to execute:\n", result)
        raise HTTPException(status_code=400, detail=f"SQL Failed: {result}")

@app.get("/logs/access")
def access_logs(admin_user: str, admin_pass: str):
    user = get_user(admin_user, admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view logs.")
    logs = fetch_access_logs(20)
    return {"logs": logs}

@app.post("/admin/lock")
def lock_user(data: LockUserRequest):
    user = get_user(data.admin_user, data.admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can lock users.")
    until = datetime.now() + timedelta(minutes=data.duration_minutes)
    _failed_logins[data.target_user] = {"count": 999, "lock_until": until}
    log_access(data.target_user, f"ADMIN_LOCKOUT_{data.duration_minutes}m")
    return {"message": f"User '{data.target_user}' locked until {until}"}
