import re
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
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
from Query_Builder.users_manager import get_user, user_exists
from Query_Builder.rbac import validate_query_access, explain_denial

app = FastAPI()
YEAR_PATTERN = re.compile(r"^\d{4}$")
intent_recognizer = IntentRecognizer()
_failed_logins = {}
_active_sessions = {}

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

class MessageRequest(BaseModel):
    username: str
    password: str
    message: str

class AdminMessageRequest(BaseModel):
    admin_user: str
    admin_pass: str
    target_user: str
    message: str

class LogoutRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(data: LoginRequest):
    username = data.username
    password = data.password
    info = _failed_logins.get(username, {"count": 0, "lock_until": None})
    if info["lock_until"] and datetime.now() < info["lock_until"]:
        wait = (info["lock_until"] - datetime.now()).seconds
        raise HTTPException(status_code=403, detail=f"Locked. Try after {wait//60}m{wait%60}s.")
    if username in _active_sessions:
        raise HTTPException(status_code=403, detail="User already logged in elsewhere.")
    user = get_user(username, password)
    if user:
        _failed_logins.pop(username, None)
        _active_sessions[username] = True
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

@app.post("/logout")
def logout(data: LogoutRequest):
    user = get_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    if data.username in _active_sessions:
        _active_sessions.pop(data.username)
    return {"message": "Logged out successfully."}

@app.post("/query")
def handle_query(data: QueryRequest):
    user = get_user(data.username, data.password)
    if not user:
        log_access(data.username, "LOGIN_FAILURE_QUERY")
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    if data.username not in _active_sessions:
        raise HTTPException(status_code=403, detail="User not actively logged in.")
    q = data.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Empty query.")
    t1, dates = normalize_dates(q)
    t2, units = normalize_units(t1 if dates else q)
    tok = tokenize(t2 if units else t1)
    final_tokens = tok["Final Tokens"]
    intent = intent_recognizer.predict_from_tokens(final_tokens)
    ents = schema_entity_recognizer(final_tokens, SCHEMA_PHRASES)
    ops_raw = comparison_operator_recognizer(t2)
    ops = [(raw, op) for op, raw, _, _ in ops_raw]
    raw_vals = value_entity_recognizer(t2)
    vals = []
    for typ, val, lo, hi in raw_vals:
        if typ == "STRING":
            continue
        if typ == "INTEGER" and YEAR_PATTERN.match(val):
            typ = "DATE"
        vals.append({"type": typ, "value": val, "span": (lo, hi)})
    query_str, resolved_db = build_query(
        intent, ents, ops, vals,
        db_host='localhost', db_user='root', db_pass='root'
    )
    if not validate_query_access(user["role"], resolved_db):
        reason = explain_denial(user["role"], resolved_db)
        log_query(user["username"], user["role"], q, resolved_db, "denied", sql=query_str)
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
        return {"sample_rows": result[:5]}
    else:
        log_query(user["username"], user["role"], q, resolved_db, "fail", sql=query_str)
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
    if not user_exists(data.target_user):
        raise HTTPException(status_code=404, detail=f"User '{data.target_user}' does not exist.")
    until = datetime.now() + timedelta(minutes=data.duration_minutes)
    _failed_logins[data.target_user] = {"count": 999, "lock_until": until}
    if data.target_user in _active_sessions:
        _active_sessions.pop(data.target_user)
    log_access(data.target_user, f"ADMIN_LOCKOUT_{data.duration_minutes}m")
    return {"locked_user": data.target_user, "until": until.strftime("%Y-%m-%d %H:%M:%S")}

@app.post("/message")
def send_message(data: MessageRequest):
    user = get_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (from_user, to_user, message) VALUES (%s, %s, %s)", (data.username, "admin", data.message))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Message sent to admin."}

@app.post("/admin/message")
def admin_send_message(data: AdminMessageRequest):
    user = get_user(data.admin_user, data.admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can send messages.")
    if not user_exists(data.target_user):
        raise HTTPException(status_code=404, detail=f"User '{data.target_user}' does not exist.")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (from_user, to_user, message) VALUES (%s, %s, %s)", ("admin", data.target_user, data.message))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": f"Message sent to {data.target_user}."}

@app.get("/messages")
def user_inbox(username: str, password: str):
    user = get_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
    cur = conn.cursor()
    cur.execute("""
        SELECT id, from_user, message, created_at
        FROM messages
        WHERE to_user=%s
        ORDER BY created_at DESC
        LIMIT 20
    """, (username,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"messages": [
        {"id": r[0], "from": r[1], "message": r[2], "time": r[3].strftime("%Y-%m-%d %H:%M:%S")}
        for r in rows
    ]}

@app.get("/admin/messages")
def view_all_messages(admin_user: str, admin_pass: str):
    user = get_user(admin_user, admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view messages.")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
    cur = conn.cursor()
    cur.execute("""
        SELECT id, from_user, to_user, message, created_at
        FROM messages
        ORDER BY created_at DESC
        LIMIT 20
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"messages": [
        {"id": r[0], "from": r[1], "to": r[2], "message": r[3], "time": r[4].strftime("%Y-%m-%d %H:%M:%S")}
        for r in rows
    ]}
