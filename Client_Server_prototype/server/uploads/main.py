import re
import json
from datetime import datetime, timedelta
import base64
import os
import subprocess
import time
import httpx

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector

from common.encryption_utils import (
    load_private_key,
    b64dec,
    decrypt_key_rsa,
    aes_decrypt,
    aes_encrypt
)

from NLP_pipeline.tokenizer_stanza import tokenize, SCHEMA_MAP
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_priv_key = load_private_key("common/server_private_key.pem")
YEAR_PATTERN = re.compile(r"^\d{4}$")
intent_recognizer = IntentRecognizer()
_failed_logins = {}
_active_sessions = {}
_llm_process = None

_ollama_client = None

# Define intents that require admin privileges for modification
MODIFICATION_INTENTS = {
    "CREATE_TABLE", "ALTER_TABLE", "DROP_TABLE", "TRUNCATE_TABLE", "RENAME_TABLE",
    "CREATE_DATABASE", "DROP_DATABASE", "RENAME_DATABASE",
    "CREATE_INDEX", "DROP_INDEX",
    "INSERT_ROWS", "UPDATE_ROWS", "DELETE_ROWS",
    "GRANT_PRIVILEGE", "REVOKE_PRIVILEGE",
    "COMMIT_TRANSACTION", "ROLLBACK_TRANSACTION", "SAVEPOINT_TRANSACTION"
}

@app.on_event("startup")
async def startup_event():
    global _llm_process, _ollama_client
    
    print("\n===== Running schema_automation.py =====")
    try:
        result = subprocess.run(
            ["python", "NLP_pipeline/schema_automation.py"],
            capture_output=True,
            text=True,
            check=True
        )
        print("schema_automation.py output:\n", result.stdout)
        if result.stderr:
            print("automate_schema.py errors:\n", result.stderr)
        print("===== schema_automation.py finished =====")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: schema_automation.py failed with exit code {e.returncode}")
        print("Stdout:", e.stdout)
        print("Stderr:", e.stderr)
    except FileNotFoundError:
        print("ERROR: python command or NLP_pipeline/schema_automation.py not found. Ensure Python is in PATH and script path is correct.")
    except Exception as e:
        print(f"An unexpected error occurred while running schema_automation.py: {e}")

    _llm_process = subprocess.Popen(
        [r"C:\Users\hbhan\AppData\Local\Programs\Ollama\ollama.exe", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)
    _ollama_client = httpx.AsyncClient(timeout=30.0)

@app.on_event("shutdown")
async def shutdown_event():
    global _llm_process, _ollama_client
    if _llm_process:
        _llm_process.terminate()
    if _ollama_client:
        await _ollama_client.aclose()

class SecureLoginRequest(BaseModel):
    encrypted_key: str
    nonce: str
    ciphertext: str

class SimpleLoginRequest(BaseModel):
    username: str
    password: str

class EncryptedQueryRequest(BaseModel):
    encrypted_key: str
    nonce: str
    ciphertext: str

class SimpleQueryRequest(BaseModel):
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

class AddUserRequest(BaseModel):
    admin_user: str
    admin_pass: str
    target_user: str
    department: str
    position: str

class LogoutRequest(BaseModel):
    username: str
    password: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Server is running"}

@app.get("/public-key")
async def get_public_key():
    public_key_path = "common/server_public_key.pem"
    if not os.path.exists(public_key_path):
        raise HTTPException(500, "Server public key file not found. Please ensure 'common/server_public_key.pem' exists.")
    try:
        with open(public_key_path, "r") as f:
            public_key_content = f.read()
        return {"public_key": public_key_content}
    except Exception as e:
        print(f"Error reading public key file: {e}")
        raise HTTPException(500, "Failed to read server public key.")

async def get_ollama_commentary(input_data):
    """
    Generates conversational commentary using Ollama, acting as a medium
    between the user and the query pipeline, without exposing internal details.
    """
    try:
        original_query = input_data.get('original_query', 'N/A')
        query_status = input_data.get('query_status', 'N/A')
        denial_reason = input_data.get('denial_reason', '')
        sql_error = input_data.get('sql_error', '')
        sample_rows_count = input_data.get('sample_rows_count', 0)
        
        base_instruction = "You are ConversQL, a friendly and helpful AI assistant. Your primary role is to communicate clearly and conversationally with the user. Never mention internal processes like SQL, intents, or tokenization. Focus solely on the user's input and the outcome in natural language."
        
        if query_status == "success":
            prompt = f"""{base_instruction}User asked: "{original_query}"I successfully found {sample_rows_count} relevant entries for your request.Please provide a brief, friendly response summarizing what was found. Focus on the user's original question and the data you retrieved."""
        elif query_status == "denied":
            prompt = f"""{base_instruction}User asked: "{original_query}"I'm sorry, but I don't have the necessary permissions to access that information for you. The system indicated: {denial_reason}.Please provide a brief, empathetic response explaining why access was denied and suggest how the user might rephrase their question or what kind of information they *can* access based on their permissions."""
        elif query_status == "fail":
            prompt = f"""{base_instruction}User asked: "{original_query}"I tried to get that information for you, but I ran into a technical issue while processing the request. The problem was: {sql_error}.Please provide a brief, helpful response explaining the issue in simple terms and suggest how the user might rephrase their question or what might be causing the problem (e.g., data not existing, a typo in their request). Avoid technical jargon where possible."""
        elif query_status == "general_chat":
            prompt = f"""{base_instruction}User said: "{original_query}"This input does not seem to be a database query. Please respond as a general-purpose AI assistant, engaging in a friendly conversation or answering general knowledge questions. If the user asks for data, gently guide them to phrase it as a query."""
        else:
            prompt = f"""{base_instruction}User asked: "{original_query}"I couldn't quite understand how to find the information you're looking for.Please provide a brief, polite response explaining that you couldn't fulfill the request and suggest how the user could rephrase their question or provide more specific details. Give an example of a clearer way to ask if possible."""
            
        print(f"\n--- Ollama Conversational Prompt ---\n{prompt}\n---------------------")
        try:
            response = await _ollama_client.post(
                "http://localhost:11434/api/generate",
                json={
                    "prompt": prompt,
                    "model": "gemma:2b",
                    "stream": False,
                    "options": {
                        "temperature": 0.5,
                        "top_p": 0.7,
                        "num_predict": 150,
                        "stop": ["\n\n", "User:", "ConversQL:"]
                    }
                }
            )
            response.raise_for_status()
        except httpx.RequestError as req_err:
            print(f"HTTPX Request Error: {req_err}")
            return f"I'm having trouble connecting to my AI brain right now. Please try again in a moment."
        except httpx.HTTPStatusError as http_err:
            print(f"HTTP error with Ollama: {http_err}")
            return f"I'm experiencing some technical difficulties. Please try again."
        try:
            json_response = response.json()
            ollama_text = json_response.get("response", "").strip()
            
            if ollama_text:
                return ollama_text
            else:
                return "I processed your request but couldn't generate a proper response. Please try rephrasing your question."
                
        except json.JSONDecodeError as json_err:
            print(f"JSON Decode Error from Ollama: {json_err}")
            return "I'm having trouble processing the response. Please try again."
    except Exception as e:
        print(f"Unexpected error with Ollama: {e}")
        return "I encountered an unexpected error. Please try your query again."

@app.post("/login")
def login(req: SecureLoginRequest):
    print("\n===== ENCRYPTED LOGIN PAYLOAD RECEIVED =====")
    print(f"Encrypted Key: {req.encrypted_key[:30]}...")
    print(f"Nonce: {req.nonce[:30]}...")
    print(f"Ciphertext: {req.ciphertext[:30]}...")

    try:
        wrapped_key = b64dec(req.encrypted_key)
        sym_key = decrypt_key_rsa(wrapped_key, _priv_key)
    except Exception as e:
        print(f"ERROR: Invalid key wrap - {e}")
        raise HTTPException(400, "Invalid key wrap")
    try:
        nonce = b64dec(req.nonce)
        ct = b64dec(req.ciphertext)
        raw = aes_decrypt(nonce, ct, sym_key)
        creds = json.loads(raw)
        username = creds.get("u")
        password = creds.get("p")
        print(f"Decrypted Login Credentials: Username={username}, Password={'*' * len(password)}")
    except Exception as e:
        print(f"ERROR: Invalid encrypted payload - {e}")
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

@app.post("/login/simple")
def simple_login(req: SimpleLoginRequest):
    """Simple login endpoint for testing without encryption"""
    username = req.username
    password = req.password
    
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
async def encrypted_query(req: EncryptedQueryRequest):
    print("\n===== ENCRYPTED QUERY PAYLOAD RECEIVED =====")
    print(f"Encrypted Key: {req.encrypted_key[:30]}...")
    print(f"Nonce: {req.nonce[:30]}...")
    print(f"Ciphertext: {req.ciphertext[:30]}...")

    try:
        wrapped = b64dec(req.encrypted_key)
        sym_key = decrypt_key_rsa(wrapped, _priv_key)
        nonce = b64dec(req.nonce)
        ct = b64dec(req.ciphertext)
        raw = aes_decrypt(nonce, ct, sym_key)
        data = json.loads(raw)
        print(f"Decrypted Query Data: {data}")
    except Exception as e:
        print(f"ERROR: Failed to decrypt query payload - {e}")
        raise HTTPException(400, "Invalid encrypted payload for query")

    user = get_user(data["username"], data["password"])
    if not user:
        raise HTTPException(401, "Invalid credentials.")
    if data["username"] not in _active_sessions:
        raise HTTPException(403, "User not actively logged in.")
    q = data["query"].strip().lower()
    if not q:
        raise HTTPException(400, "Empty query.")

    print("\n===== RAW INPUT =====")
    print(q)

    t1, dates = normalize_dates(q)
    print("\n===== AFTER NORMALIZE DATES =====")
    print(t1)

    t2, units = normalize_units(t1 if dates else q)
    print("\n===== AFTER NORMALIZE UNITS =====")
    print(t2)

    tok = tokenize(t2 if units else t1)
    final_tokens = tok["Final Tokens"]
    print("\n===== FINAL TOKENS =====")
    print(final_tokens)

    intent = intent_recognizer.predict_from_tokens(final_tokens)
    print("\n===== DETECTED INTENT =====")
    print(intent)

    # Admin check for modificational tasks
    if user["role"] != "admin" and any(i in MODIFICATION_INTENTS for i in intent):
        raise HTTPException(403, "Permission denied: Only admin users can perform this action.")

    ents = schema_entity_recognizer(final_tokens, SCHEMA_MAP)
    print("\n===== INITIAL SCHEMA ENTITIES =====")
    print(ents)

    ops_raw = comparison_operator_recognizer(t2)
    print("\n===== RAW OPERATORS FROM RECOGNIZER =====")
    print(ops_raw)

    raw_vals = value_entity_recognizer(t2)
    vals = []
    for typ, val, lo, hi in raw_vals:
        if typ == "STRING":
            continue
        if typ == "INTEGER" and YEAR_PATTERN.match(val):
            typ = "DATE"
        vals.append({"type": typ, "value": val, "span": (lo, hi)})
    print("\n===== VALUES =====")
    print(vals)

    all_identified_columns = [e['value'] for e in ents if e['type'] == 'column']
    agg_column = None
    if "AGGREGATE_AVG" in intent or "AGGREGATE_SUM" in intent or \
       "AGGREGATE_MIN" in intent or "AGGREGATE_MAX" in intent:
        if all_identified_columns:
            agg_column = all_identified_columns[0]
    
    structured_ops = []
    if ops_raw and all_identified_columns:
        filter_col = None
        if len(all_identified_columns) == 1:
            filter_col = all_identified_columns[0]
        elif len(all_identified_columns) > 1 and agg_column:
            for col_name in all_identified_columns:
                if col_name != agg_column:
                    filter_col = col_name
                    break
            if not filter_col:
                filter_col = all_identified_columns[0]
        elif all_identified_columns:
            filter_col = all_identified_columns[0]

        if filter_col:
            for op_symbol, op_text in ops_raw:
                structured_ops.append((filter_col, op_symbol, op_text))
    elif ops_raw:
        for op_symbol, op_text in ops_raw:
            structured_ops.append((None, op_symbol, op_text))

    print("\n===== FINAL OPERATORS FOR BUILD_QUERY =====")
    print(structured_ops)

    query_str, resolved_db = build_query(
        intent, ents, structured_ops, vals, q, # Pass original_query
        db_host='localhost', db_user='root', db_pass='root'
    )
    print("\n===== GENERATED QUERY =====")
    print(query_str)

    rows = []
    commentary = ""
    text_response = ""
    error_message = None
    query_status = "no_sql"
    log_action_type = "read" # Default log action type

    # Determine log action type based on intent
    if any(i in MODIFICATION_INTENTS for i in intent):
        log_action_type = "write" # For DML, DDL, DCL, TCL
    elif "SELECT_ROWS" in intent or "SHOW_DATABASES" in intent or "SHOW_TABLES" in intent or "DESCRIPTION" in intent:
        log_action_type = "read"
    else:
        log_action_type = "unknown" # Fallback for other intents

    ollama_input_data = {
        "original_query": q,
        "final_tokens": final_tokens,
        "intent": intent,
        "ents": ents,
        "ops": structured_ops,
        "vals": vals,
        "query_str": "N/A (No SQL generated)",
        "query_status": query_status,
        "denial_reason": "",
        "sql_error": "",
        "sample_rows_count": 0
    }

    if not resolved_db and not any(i in ["SHOW_DATABASES", "CREATE_DATABASE", "DROP_DATABASE", "RENAME_DATABASE", "GRANT_PRIVILEGE", "REVOKE_PRIVILEGE", "COMMIT_TRANSACTION", "ROLLBACK_TRANSACTION", "SAVEPOINT_TRANSACTION"] for i in intent):
        query_status = "no_sql"
        ollama_input_data["query_status"] = query_status
        commentary = await get_ollama_commentary(ollama_input_data)
        text_response = commentary
        error_message = "Could not resolve database or table from your query."
    elif not validate_query_access(user["role"], resolved_db):
        query_status = "denied"
        reason = explain_denial(user["role"], resolved_db)
        log_query(user["username"], user["role"], q, resolved_action_type=log_action_type, status="denied", sql=query_str)
        ollama_input_data.update({
            "query_str": query_str,
            "query_status": query_status,
            "denial_reason": reason
        })
        commentary = await get_ollama_commentary(ollama_input_data)
        text_response = commentary
        error_message = reason
    else:
        success, result = verify_query(
            query_str,
            host='localhost', user='root', password='root',
            database=resolved_db
        )
        if success:
            query_status = "success"
            log_query(user["username"], user["role"], q, resolved_action_type=log_action_type, status="success", sql=query_str)
            rows = result[:5]
            ollama_input_data.update({
                "query_str": query_str,
                "query_status": query_status,
                "sample_rows_count": len(rows)
            })
            commentary = await get_ollama_commentary(ollama_input_data)
            text_response = commentary
        else:
            query_status = "fail"
            log_query(user["username"], user["role"], q, resolved_action_type=log_action_type, status="fail", sql=query_str)
            ollama_input_data.update({
                "query_str": query_str,
                "query_status": query_status,
                "sql_error": result
            })
            commentary = await get_ollama_commentary(ollama_input_data)
            text_response = commentary
            error_message = result

    print("\n===== OLLAMA COMMENTARY =====")
    print(commentary)
    if error_message:
        print("\n===== OLLAMA ERROR SUGGESTION =====")
        print(error_message)

    response_payload = {
        "sample_rows": rows,
        "commentary": commentary,
        "text_response": text_response,
    }
    if error_message:
        response_payload["error"] = error_message

    resp_plain = json.dumps(response_payload, default=str).encode()
    out = aes_encrypt(resp_plain, sym_key)
    return {
        "nonce": base64.b64encode(out["nonce"]).decode(),
        "ciphertext": base64.b64encode(out["ciphertext"]).decode()
    }

@app.post("/query/simple")
async def simple_query(req: SimpleQueryRequest):
    """Optimized simple query endpoint"""
    user = get_user(req.username, req.password)
    if not user:
        raise HTTPException(401, "Invalid credentials.")
    if req.username not in _active_sessions:
        raise HTTPException(403, "User not actively logged in.")
    
    q = req.query.strip().lower()
    if not q:
        raise HTTPException(400, "Empty query.")

    print("\n===== RAW INPUT =====")
    print(q)
    
    t1, dates = normalize_dates(q)
    t2, units = normalize_units(t1 if dates else t1)
    tok = tokenize(t2 if units else t1)
    final_tokens = tok["Final Tokens"]
    
    intent = intent_recognizer.predict_from_tokens(final_tokens)
    print("\n===== DETECTED INTENT =====")
    print(intent)

    # Admin check for modificational tasks
    if user["role"] != "admin" and any(i in MODIFICATION_INTENTS for i in intent):
        raise HTTPException(403, "Permission denied: Only admin users can perform this action.")

    ents = schema_entity_recognizer(final_tokens, SCHEMA_MAP)
    print("\n===== INITIAL SCHEMA ENTITIES =====")
    print(ents)

    ops_raw = comparison_operator_recognizer(t2)
    
    raw_vals = value_entity_recognizer(t2)
    vals = []
    for typ, val, lo, hi in raw_vals:
        if typ == "STRING":
            continue
        if typ == "INTEGER" and YEAR_PATTERN.match(val):
            typ = "DATE"
        vals.append({"type": typ, "value": val, "span": (lo, hi)})

    all_identified_columns = [e['value'] for e in ents if e['type'] == 'column']
    agg_column = None
    if "AGGREGATE_AVG" in intent or "AGGREGATE_SUM" in intent or \
       "AGGREGATE_MIN" in intent or "AGGREGATE_MAX" in intent:
        if all_identified_columns:
            agg_column = all_identified_columns[0]
    
    structured_ops = []
    if ops_raw and all_identified_columns:
        filter_col = None
        if len(all_identified_columns) == 1:
            filter_col = all_identified_columns[0]
        elif len(all_identified_columns) > 1 and agg_column:
            for col_name in all_identified_columns:
                if col_name != agg_column:
                    filter_col = col_name
                    break
            if not filter_col:
                filter_col = all_identified_columns[0]
        elif all_identified_columns:
            filter_col = all_identified_columns[0]

        if filter_col:
            for op_symbol, op_text in ops_raw:
                structured_ops.append((filter_col, op_symbol, op_text))
    elif ops_raw:
        for op_symbol, op_text in ops_raw:
            structured_ops.append((None, op_symbol, op_text))

    query_str, resolved_db = build_query(
        intent, ents, structured_ops, vals, q, # Pass original_query
        db_host='localhost', db_user='root', db_pass='root'
    )
    print(f"\n===== GENERATED QUERY =====\n{query_str}")

    rows = []
    commentary = ""
    error_message = None
    query_status = "no_sql"
    log_action_type = "read" # Default log action type

    is_general_chat = False
    if not resolved_db and not query_str and any(i in intent for i in ['greeting', 'general_question', 'unknown']):
        is_general_chat = True

    # Determine log action type based on intent
    if any(i in MODIFICATION_INTENTS for i in intent):
        log_action_type = "write" # For DML, DDL, DCL, TCL
    elif "SELECT_ROWS" in intent or "SHOW_DATABASES" in intent or "SHOW_TABLES" in intent or "DESCRIPTION" in intent:
        log_action_type = "read"
    else:
        log_action_type = "unknown" # Fallback for other intents

    ollama_input_data = {
        "original_query": q,
        "intent": intent,
        "query_str": query_str if query_str else "N/A (No SQL generated)",
        "query_status": query_status,
        "denial_reason": "",
        "sql_error": "",
        "sample_rows_count": 0
    }

    if is_general_chat:
        query_status = "general_chat"
        ollama_input_data["query_status"] = query_status
        commentary = await get_ollama_commentary(ollama_input_data)
        
    elif not resolved_db and not any(i in ["SHOW_DATABASES", "CREATE_DATABASE", "DROP_DATABASE", "RENAME_DATABASE", "GRANT_PRIVILEGE", "REVOKE_PRIVILEGE", "COMMIT_TRANSACTION", "ROLLBACK_TRANSACTION", "SAVEPOINT_TRANSACTION"] for i in intent):
        query_status = "no_sql"
        ollama_input_data["query_status"] = query_status
        commentary = await get_ollama_commentary(ollama_input_data)
        error_message = "Could not resolve database or table from your query."
        
    elif not validate_query_access(user["role"], resolved_db):
        query_status = "denied"
        reason = explain_denial(user["role"], resolved_db)
        log_query(user["username"], user["role"], q, resolved_db, log_action_type, status="denied", sql=query_str)
        ollama_input_data.update({
            "query_status": query_status,
            "denial_reason": reason
        })
        commentary = await get_ollama_commentary(ollama_input_data)
        error_message = reason
        
    else:
        success, result = verify_query(
            query_str,
            host='localhost', user='root', password='root',
            database=resolved_db
        )
        
        if success:
            query_status = "success"
            log_query(user["username"], user["role"], q, resolved_db, log_action_type, status="success", sql=query_str)
            rows = result[:5]
            ollama_input_data.update({
                "query_status": query_status,
                "sample_rows_count": len(rows)
            })
            commentary = await get_ollama_commentary(ollama_input_data)
            
        else:
            query_status = "fail"
            log_query(user["username"], user["role"], q, resolved_db, log_action_type, status="fail", sql=query_str)
            ollama_input_data.update({
                "query_status": query_status,
                "sql_error": result
            })
            commentary = await get_ollama_commentary(ollama_input_data)
            error_message = result

    print(f"\n===== OLLAMA COMMENTARY =====\n{commentary}")
    if error_message:
        print("\n===== OLLAMA ERROR SUGGESTION =====\n", error_message)

    response_payload = {
        "sample_rows": rows,
        "commentary": commentary,
        "text_response": commentary,
        "query_status": query_status,
        "generated_sql": query_str if query_str else None
    }
    
    if error_message:
        response_payload["error"] = error_message
    return response_payload

@app.get("/logs/access")
def access_logs(admin_user: str, admin_pass: str):
    user = get_user(admin_user, admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(403, "Only admin can view logs.")
    
    raw_logs = fetch_access_logs(20)
    
    # Convert tuples to dictionaries for frontend consumption
    formatted_logs = []
    for log_entry in raw_logs:
        # log_entry is (idx, usernm, ts, status)
        # We need: username, action, timestamp
        if len(log_entry) >= 4: # Ensure it has enough parts
            # The order in the tuple is (idx, username, timestamp, status)
            # So, log_entry[1] is username, log_entry[3] is status (action), log_entry[2] is timestamp
            formatted_logs.append({
                "username": log_entry[1],
                "action": log_entry[3],
                "timestamp": log_entry[2]
            })
    
    return {"logs": formatted_logs}

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
