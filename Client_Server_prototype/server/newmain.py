import re
import json
from datetime import datetime, timedelta
import base64

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import subprocess
import time

from common.encryption_utils import (
    load_private_key,
    b64dec,
    decrypt_key_rsa,
    aes_decrypt,
    aes_encrypt
)

from NLP_pipeline.tokenizer_stanza import tokenize, SCHEMA_PHRASES
from NLP_pipeline.schema_entity_recognizer import schema_entity_recognizer
from NLP_pipeline.comparison_operator_recognizer import comparison_operator_recognizer
from NLP_pipeline.value_entity_recognizer import value_entity_recognizer
from NLP_pipeline.normalize_units import normalize_units
from NLP_pipeline.normalize_dates import normalize_dates
from NLP_pipeline.intent_recognizer import IntentRecognizer

from Query_Builder.query_builder_factory import build_query
from Query_Builder.query_verifier import verify_query
from Query_Builder.query_logger import log_query, log_access, fetch_access_logs
from Query_Builder.users_manager import get_user, user_exists, create_user
from Query_Builder.rbac import validate_query_access, explain_denial

app = FastAPI()

_priv_key = load_private_key("common/server_private_key.pem")
YEAR_PATTERN = re.compile(r"^\d{4}$")
intent_recognizer = IntentRecognizer()
_failed_logins = {}
_active_sessions = {}
_llm_process = None

@app.on_event("startup")
def startup_event():
    global _llm_process
    _llm_process = subprocess.Popen(
        [r"C:\Users\hbhan\AppData\Local\Programs\Ollama\ollama.exe", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)

@app.on_event("shutdown")
def shutdown_event():
    global _llm_process
    if _llm_process:
        _llm_process.terminate()

class SecureLoginRequest(BaseModel):
    encrypted_key: str
    nonce:         str
    ciphertext:    str

class EncryptedQueryRequest(BaseModel):
    encrypted_key: str
    nonce:         str
    ciphertext:    str

class LockUserRequest(BaseModel):
    admin_user:       str
    admin_pass:       str
    target_user:      str
    duration_minutes: int

class MessageRequest(BaseModel):
    username: str
    password: str
    message:  str

class AdminMessageRequest(BaseModel):
    admin_user:   str
    admin_pass:   str
    target_user:  str
    message:      str

class AddUserRequest(BaseModel):
    admin_user:   str
    admin_pass:   str
    target_user:  str
    department:   str
    position:     str

class LogoutRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(req: SecureLoginRequest):
    try:
        wrapped_key = b64dec(req.encrypted_key)
        sym_key = decrypt_key_rsa(wrapped_key, _priv_key)
    except Exception:
        raise HTTPException(400, "Invalid key wrap")
    try:
        nonce = b64dec(req.nonce)
        ct = b64dec(req.ciphertext)
        raw = aes_decrypt(nonce, ct, sym_key)
        creds = json.loads(raw)
        username = creds.get("u")
        password = creds.get("p")
    except Exception:
        raise HTTPException(400, "Invalid encrypted payload")

    info = _failed_logins.get(username, {"count": 0, "lock_until": None})
    if info["lock_until"] and datetime.now() < info["lock_until"]:
        wait = (info["lock_until"] - datetime.now()).seconds
        raise HTTPException(403, f"Locked. Try after {wait//60}m{wait%60}s.")
    if username in _active_sessions:
        raise HTTPException(403, "User already logged in elsewhere.")
    user = get_user(username, password)
    if user:
        _failed_logins.pop(username, None)
        _active_sessions[username] = True
        log_access(username, "LOGIN_SUCCESS")
        return {"message": "Login successful", "role": user["role"]}
    info["count"] += 1
    log_access(username, "LOGIN_FAILURE")
    if info["count"] >= 3:
        info["lock_until"] = datetime.now() + timedelta(minutes=5)
        log_access(username, "LOCKOUT")
    _failed_logins[username] = info
    raise HTTPException(401, "Invalid credentials.")

@app.post("/logout")
def logout(data: LogoutRequest):
    user = get_user(data.username, data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials.")
    _active_sessions.pop(data.username, None)
    return {"message": "Logged out successfully."}

@app.post("/query")
def encrypted_query(req: EncryptedQueryRequest):
    wrapped = b64dec(req.encrypted_key)
    sym_key = decrypt_key_rsa(wrapped, _priv_key)
    nonce = b64dec(req.nonce)
    ct = b64dec(req.ciphertext)
    raw = aes_decrypt(nonce, ct, sym_key)
    data = json.loads(raw)

    user = get_user(data["username"], data["password"])
    if not user:
        raise HTTPException(401, "Invalid credentials.")
    if data["username"] not in _active_sessions:
        raise HTTPException(403, "User not actively logged in.")
    q = data["query"].strip()
    if not q:
        raise HTTPException(400, "Empty query.")

    t1, dates = normalize_dates(q)
    t2, units = normalize_units(t1 if dates else q)
    tok = tokenize(t2 if units else t1)
    final_tokens = tok["Final Tokens"]
    intent = intent_recognizer.predict_from_tokens(final_tokens)
    ents = schema_entity_recognizer(final_tokens, SCHEMA_PHRASES)
    ops_raw = comparison_operator_recognizer(t2)
    ops = [(i["matched_phrase"], i["operator"]) for i in ops_raw]
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
    if not resolved_db:
        raise HTTPException(400, "Cannot determine target database.")
    if not validate_query_access(user["role"], resolved_db):
        reason = explain_denial(user["role"], resolved_db)
        log_query(user["username"], user["role"], q, resolved_db, "denied", sql=query_str)
        raise HTTPException(403, reason)
    success, result = verify_query(
        query_str,
        host='localhost', user='root', password='root',
        database=resolved_db
    )
    if success:
        log_query(user["username"], user["role"], q, resolved_db, "read", sql=query_str)
        rows = result[:5]
    else:
        log_query(user["username"], user["role"], q, resolved_db, "fail", sql=query_str)
        raise HTTPException(400, f"SQL Failed: {result}")

    resp_plain = json.dumps({"sample_rows": rows}, default=str).encode()
    out = aes_encrypt(resp_plain, sym_key)
    return {
        "nonce": base64.b64encode(out["nonce"]).decode(),
        "ciphertext": base64.b64encode(out["ciphertext"]).decode()
    }

@app.get("/logs/access")
def access_logs(admin_user: str, admin_pass: str):
    user = get_user(admin_user, admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(403, "Only admin can view logs.")
    logs = fetch_access_logs(20)
    return {"logs": logs}

@app.post("/admin/lock")
def lock_user(data: LockUserRequest):
    user = get_user(data.admin_user, data.admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(403, "Only admin can lock users.")
    if not user_exists(data.target_user):
        raise HTTPException(404, f"User '{data.target_user}' not found.")
    until = datetime.now() + timedelta(minutes=data.duration_minutes)
    _failed_logins[data.target_user] = {"count": 999, "lock_until": until}
    _active_sessions.pop(data.target_user, None)
    log_access(data.target_user, f"ADMIN_LOCKOUT_{data.duration_minutes}m")
    return {"locked_user": data.target_user, "until": until.strftime("%Y-%m-%d %H:%M:%S")}

@app.post("/message")
def send_message(data: MessageRequest):
    user = get_user(data.username, data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials.")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
    cur = conn.cursor()
    cur.execute("INSERT INTO messages(from_user,to_user,message) VALUES(%s,%s,%s)", (data.username, "admin", data.message))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Message sent to admin."}

@app.post("/admin/message")
def admin_send_message(data: AdminMessageRequest):
    user = get_user(data.admin_user, data.admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(403, "Only admin can send messages.")
    if not user_exists(data.target_user):
        raise HTTPException(404, f"User '{data.target_user}' not found.")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
    cur = conn.cursor()
    cur.execute("INSERT INTO messages(from_user,to_user,message) VALUES(%s,%s,%s)", ("admin", data.target_user, data.message))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": f"Message sent to {data.target_user}."}

@app.get("/messages")
def user_inbox(username: str, password: str):
    user = get_user(username, password)
    if not user:
        raise HTTPException(401, "Invalid credentials.")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
    cur = conn.cursor()
    cur.execute("""
        SELECT id, from_user, message, created_at
          FROM messages
         WHERE to_user = %s
         ORDER BY created_at DESC
         LIMIT 20
    """, (username,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"messages": [{"id": r[0], "from": r[1], "message": r[2], "time": r[3].strftime("%Y-%m-%d %H:%M:%S")} for r in rows]}

@app.get("/admin/messages")
def view_all_messages(admin_user: str, admin_pass: str):
    user = get_user(admin_user, admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(403, "Only admin can view messages.")
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
    return {"messages": [{"id": r[0], "from": r[1], "to": r[2], "message": r[3], "time": r[4].strftime("%Y-%m-%d %H:%M:%S")} for r in rows]}

@app.post("/admin/add_user")
def add_user(data: AddUserRequest):
    user = get_user(data.admin_user, data.admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(403, "Only admin can add users.")
    if user_exists(data.target_user):
        raise HTTPException(400, "Username already exists.")
    pwd = create_user(data.target_user, data.department, data.position)
    return {"username": data.target_user, "password": pwd}
