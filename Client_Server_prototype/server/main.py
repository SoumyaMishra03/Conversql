import re
import json
from datetime import datetime, timedelta
import base64
import os
import subprocess
import time
import httpx
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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
from Query_Builder.query_builder_factory import build_query, is_destructive_operation
from Query_Builder.query_verifier import verify_query
from Query_Builder.query_logger import log_query, log_access
from Query_Builder.users_manager import get_user, user_exists, create_user
from Query_Builder.rbac import validate_query_access, explain_denial, is_admin_only_operation

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIRECTORY = "./uploads"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

_priv_key = load_private_key("common/server_private_key.pem")
YEAR_PATTERN = re.compile(r"^\d{4}$")

intent_recognizer = IntentRecognizer("NLP_pipeline/json/intent.json", use_ai_fallback=True)

_failed_logins = {}
_active_sessions = {}
_llm_process = None
_ollama_client = None

def enhanced_operator_column_linking(entities, operators, intent):
    all_identified_columns = [e['value'] for e in entities if e['type'] == 'column']
    
    agg_column = None
    if any(agg_intent in intent for agg_intent in ["AGGREGATE_AVG", "AGGREGATE_SUM", "AGGREGATE_MIN", "AGGREGATE_MAX"]):
        if all_identified_columns:
            agg_column = all_identified_columns[0]
            
    structured_ops = []
    if operators and all_identified_columns:
        filter_columns = []
        
        if agg_column:
            filter_columns = [col for col in all_identified_columns if col != agg_column]
            if not filter_columns:
                filter_columns = [all_identified_columns[0]]
        else:
            filter_columns = all_identified_columns
            
        for i, operator_item in enumerate(operators):
            if isinstance(operator_item, tuple) and len(operator_item) >= 2:
                op_symbol = operator_item[0]
                op_text = operator_item[1]
            else:
                op_symbol = str(operator_item)
                op_text = str(operator_item)
                
            if i < len(filter_columns):
                target_column = filter_columns[i]
            else:
                target_column = filter_columns[-1] if filter_columns else all_identified_columns[0]
                
            structured_ops.append((target_column, op_symbol, op_text))
    elif operators:
        for operator_item in operators:
            if isinstance(operator_item, tuple) and len(operator_item) >= 2:
                op_symbol = operator_item[0]
                op_text = operator_item[1]
            else:
                op_symbol = str(operator_item)
                op_text = str(operator_item)
                
            structured_ops.append((None, op_symbol, op_text))
            
    return structured_ops, agg_column

async def generate_sql_with_query_builder(original_query: str, intent: list, entities: list, operators: list, values: list, user_role: str):
    try:
        print(f"\n--- Query Builder SQL Generation ---")
        print(f"Original Query: {original_query}")
        print(f"Intent: {intent}")
        print(f"Entities: {entities}")
        print(f"Operators: {operators}")
        print(f"Values: {values}")
        print(f"User Role: {user_role}")
        
        structured_ops, agg_column = enhanced_operator_column_linking(entities, operators, intent)
        
        print(f"Structured Operators: {structured_ops}")
        print(f"Aggregate Column: {agg_column}")
        
        query_str, resolved_db = build_query(intent, entities, structured_ops, values)
        
        print(f"\n--- Query Builder Generated SQL ---\n{query_str}\nDB: {resolved_db}\n---------------------")
        
        if query_str and not query_str.startswith("ERROR:"):
            if not resolved_db:
                db_entities = [e for e in entities if e.get('type') == 'database' and e.get('value')]
                if db_entities:
                    resolved_db = db_entities[0]['value']
                
                if not resolved_db:
                    table_entities = [e for e in entities if e.get('type') == 'table' and e.get('value')]
                    if table_entities:
                        table_name = table_entities[0]['value']
                        if table_name in SCHEMA_MAP.get("table_to_db", {}):
                            resolved_db = SCHEMA_MAP["table_to_db"][table_name]
                
                if not resolved_db:
                    column_entities = [e for e in entities if e.get('type') == 'column' and e.get('value')]
                    if column_entities:
                        column_name = column_entities[0]['value']
                        col_info = SCHEMA_MAP.get("column_to_table_db", {}).get(column_name)
                        if col_info:
                            if isinstance(col_info, dict) and col_info.get('db'):
                                resolved_db = col_info['db']
                            elif isinstance(col_info, tuple) and len(col_info) > 0:
                                resolved_db = col_info[0]
                
                if not resolved_db and SCHEMA_MAP.get("db_to_tables"):
                    resolved_db = list(SCHEMA_MAP["db_to_tables"].keys())[0]
            
            return query_str, resolved_db
        
        return None, None
        
    except Exception as e:
        print(f"Query Builder SQL Generation Error: {e}")
        return None, None

def has_meaningful_schema_entities(entities: list) -> bool:
    meaningful_entities = [
        e for e in entities 
        if e.get('type') in ['database', 'table', 'column'] 
        and e.get('value') 
        and e.get('type') != 'unmatched'
        and len(e.get('value', '').strip()) > 0
    ]
    return len(meaningful_entities) > 0

async def get_optimized_commentary(input_data, ai_already_used: bool = False):
    original_query = input_data.get('original_query', 'N/A')
    query_status = input_data.get('query_status', 'N/A')
    denial_reason = input_data.get('denial_reason', '')
    sql_error = input_data.get('sql', '')
    sample_rows_count = input_data.get('sample_rows_count', 0)
    intent = input_data.get('intent', [])
    is_aggregate_query = input_data.get('is_aggregate_query', False)
    has_schema_entities = input_data.get('has_schema_entities', True)
    
    use_ai_commentary = (
        not has_schema_entities and 
        not ai_already_used and 
        query_status in ["general_chat", "no_sql"]
    )
    
    if use_ai_commentary:
        print(f"[DEBUG] Using AI commentary for general chat query")
        return await get_ai_commentary(input_data)
    else:
        print(f"[DEBUG] Using template-based commentary (AI already used: {ai_already_used}, Has schema: {has_schema_entities})")
        return get_template_commentary(input_data)

async def get_ai_commentary(input_data):
    try:
        original_query = input_data.get('original_query', 'N/A')
        query_status = input_data.get('query_status', 'N/A')
        
        base_instruction = "You are ConversQL, a friendly database assistant. The user's input doesn't seem to be a database query."
        
        if query_status == "general_chat":
            prompt = f"""{base_instruction}

User said: "{original_query}"

Please respond as a helpful AI assistant. If they're trying to ask about data, gently guide them to be more specific about what database information they need.

Response:"""
        else:
            prompt = f"""{base_instruction}

User requested: "{original_query}"

I couldn't understand this as a database query. Please provide a brief, helpful response explaining that I need more specific database-related questions, and give an example of how they could rephrase their request.

Response:"""
        
        print(f"\n--- AI Commentary Prompt ---\n{prompt}\n---------------------")
        
        response = await _ollama_client.post(
            "http://localhost:11434/api/generate",
            json={
                "prompt": prompt,
                "model": "gemma:2b",
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "top_p": 0.7,
                    "num_predict": 100,
                    "stop": ["\n\n", "User:", "ConversQL:"]
                }
            }
        )
        response.raise_for_status()
        
        json_response = response.json()
        ollama_text = json_response.get("response", "").strip()
        
        if ollama_text:
            return ollama_text
        else:
            return get_template_commentary(input_data)
            
    except Exception as e:
        print(f"AI commentary error: {e}")
        return get_template_commentary(input_data)

def get_template_commentary(input_data):
    original_query = input_data.get('original_query', 'N/A')
    query_status = input_data.get('query_status', 'N/A')
    denial_reason = input_data.get('denial_reason', '')
    sql_error = input_data.get('sql', '')
    sample_rows_count = input_data.get('sample_rows_count', 0)
    intent = input_data.get('intent', [])
    is_aggregate_query = input_data.get('is_aggregate_query', False)
    
    is_destructive = any(destructive_intent in intent for destructive_intent in [
        "INSERT_ROWS", "UPDATE_ROWS", "DELETE_ROWS", 
        "DROP_TABLE", "DROP_DATABASE", "TRUNCATE_TABLE"
    ])
    
    if query_status == "success":
        if is_destructive:
            return f"✅ Successfully executed your data modification request. The operation has been completed and logged for security purposes."
        elif is_aggregate_query:
            return f"✅ Successfully calculated the result for your query. The aggregate value has been retrieved from the database."
        else:
            return f"✅ Found {sample_rows_count} relevant entries matching your query criteria."
    
    elif query_status == "denied":
        if is_destructive:
            return f"❌ Access denied: Data modification operations require administrator privileges. Please contact your administrator if you need to make changes to the data."
        else:
            return f"❌ Access denied: {denial_reason}. Please check your permissions or contact your administrator."
    
    elif query_status == "fail":
        return f"❌ Query execution failed: {sql_error}. Please check your query syntax and try again."
    
    else:
        return f"❓ I couldn't process your request. Please try rephrasing your query with more specific database terms."

def get_admin_conversations(admin_user: str):
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT T.username, M.message as lastMessage, M.created_at as lastMessageTimestamp
            FROM (
                SELECT IF(from_user = %s, to_user, from_user) AS username, MAX(id) as max_id
                FROM messages
                WHERE (from_user = %s OR to_user = %s) AND (IF(from_user = %s, to_user, from_user) != 'admin')
                GROUP BY username
            ) AS T
            JOIN messages M ON T.max_id = M.id
            ORDER BY M.created_at DESC;
        """
        cursor.execute(query, (admin_user, admin_user, admin_user, admin_user))
        conversations = cursor.fetchall()
        for conv in conversations:
            if 'lastMessageTimestamp' in conv and hasattr(conv['lastMessageTimestamp'], 'strftime'):
                conv['lastMessageTimestamp'] = conv['lastMessageTimestamp'].strftime('%Y-%m-%d %H:%M:%S')
        return conversations
    except Exception as e:
        print(f"Error fetching admin conversations: {e}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def log_access_to_db(username: str, status: str):
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
        cur = conn.cursor()
        cur.execute("INSERT INTO access_log (username, status) VALUES (%s, %s)", (username, status))
        conn.commit()
        print(f"[DEBUG] Logged to database: {username} - {status}")
    except Exception as e:
        print(f"[ERROR] Could not write to database access_log: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cur.close()
            conn.close()

@app.on_event("startup")
async def startup_event():
    global _llm_process, _ollama_client
        
    print("\n===== Running schema_automation.py =====")
    try:
        result = subprocess.run(
            ["python", "NLP_pipeline/automate_schema.py"],
            capture_output=True,
            text=True,
            check=True         
        )
        print("schema_automation.py output:\n", result.stdout)
        if result.stderr:
            print("schema_automation.py errors:\n", result.stderr)
        print("===== schema_automation.py finished =====")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: schema_automation.py failed with exit code {e.returncode}")
        print("Stdout:", e.stdout)
        print("Stderr:", e.stderr)
    except FileNotFoundError:
        print("ERROR: python command or NLP_pipeline/schema_automation.py not found.")
    except Exception as e:
        print(f"An unexpected error occurred while running schema_automation.py: {e}")

    _llm_process = subprocess.Popen(
        [r"C:\Users\hbhan\AppData\Local\Programs\Ollama\ollama.exe", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)
        
    _ollama_client = httpx.AsyncClient(timeout=30.0)
    
    print("✅ Optimized AI system initialized - Max 1 AI call per query")

@app.on_event("shutdown")
async def shutdown_event():
    global _llm_process, _ollama_client, intent_recognizer
    if _llm_process:
        _llm_process.terminate()
    if _ollama_client:
        await _ollama_client.aclose()
    if intent_recognizer:
        await intent_recognizer.close()

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
        raise HTTPException(500, "Server public key file not found.")
    try:
        with open(public_key_path, "r") as f:
            public_key_content = f.read()
        return {"public_key": public_key_content}
    except Exception as e:
        print(f"Error reading public key file: {e}")
        raise HTTPException(500, "Failed to read server public key.")

@app.post("/login")
def login(req: SecureLoginRequest):
    print("\n===== ENCRYPTED LOGIN PAYLOAD RECEIVED =====")
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
        log_access_to_db(username, "LOGIN_SUCCESS")
        return {"message": "Login successful", "role": user["role"]}
    
    info["count"] += 1
    log_access(username, "LOGIN_FAILURE")
    log_access_to_db(username, "LOGIN_FAILURE")
    if info["count"] >= 3:
        info["lock_until"] = datetime.now() + timedelta(minutes=5)
        log_access(username, "LOCKOUT")
        log_access_to_db(username, "LOCKOUT")
    _failed_logins[username] = info
    raise HTTPException(401, "Invalid credentials.")

@app.post("/login/simple")
def simple_login(req: SimpleLoginRequest):
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
        log_access_to_db(username, "LOGIN_SUCCESS")
        return {"message": "Login successful", "role": user["role"]}
        
    info["count"] += 1
    log_access(username, "LOGIN_FAILURE")
    log_access_to_db(username, "LOGIN_FAILURE")
    if info["count"] >= 3:
        info["lock_until"] = datetime.now() + timedelta(minutes=5)
        log_access(username, "LOCKOUT")
        log_access_to_db(username, "LOCKOUT")
    _failed_logins[username] = info
    raise HTTPException(401, "Invalid credentials.")

@app.post("/logout")
def logout(data: LogoutRequest):
    user = get_user(data.username, data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials.")
    _active_sessions.pop(data.username, None)
    log_access_to_db(data.username, "LOGOUT")
    return {"message": "Logged out successfully."}

@app.post("/query")
async def encrypted_query(req: EncryptedQueryRequest):
    print("\n===== ENCRYPTED QUERY PAYLOAD RECEIVED =====")
    try:
        wrapped = b64dec(req.encrypted_key)
        sym_key = decrypt_key_rsa(wrapped, _priv_key)
        nonce = b64dec(req.nonce)
        ct = b64dec(req.ciphertext)
        raw = aes_decrypt(nonce, ct, sym_key)
        data = json.loads(raw)
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
    t2, units = normalize_units(t1 if dates else q)
    tok = tokenize(t2 if units else t1)
    final_tokens = tok["Final Tokens"]
    
    ents = schema_entity_recognizer(final_tokens)
    has_schema_entities = has_meaningful_schema_entities(ents)
    
    intent, ai_used_for_intent = intent_recognizer.predict_from_tokens(final_tokens, ents)
    print(f"\n===== DETECTED INTENT =====\n{intent} (AI used: {ai_used_for_intent})")

    is_aggregate_intent = any(agg_intent in intent for agg_intent in ["AGGREGATE_AVG", "AGGREGATE_SUM", "AGGREGATE_MIN", "AGGREGATE_MAX"])

    if is_admin_only_operation(intent) and user["role"] != "admin":
        query_status = "denied"
        reason = f"Access denied: Only administrators can perform {', '.join([i for i in intent if 'INSERT' in i or 'UPDATE' in i or 'DELETE' in i or 'DROP' in i or 'TRUNCATE' in i])} operations."
                
        ollama_input_data = {
            "original_query": q,
            "intent": intent,
            "query_str": "N/A (Access denied)",
            "query_status": query_status,
            "denial_reason": reason,
            "sql": "",
            "sample_rows_count": 0,
            "is_aggregate_query": is_aggregate_intent,
            "has_schema_entities": has_schema_entities
        }
                
        commentary = await get_optimized_commentary(ollama_input_data, ai_used_for_intent)
        log_query(user["username"], user["role"], q, "N/A", "denied", sql="N/A (Admin-only operation)")
                
        response_payload = {
            "sample_rows": [],
            "commentary": commentary,
            "text_response": commentary,
            "error": reason
        }
                
        resp_plain = json.dumps(response_payload, default=str).encode()
        out = aes_encrypt(resp_plain, sym_key)
        return {
            "nonce": base64.b64encode(out["nonce"]).decode(),
            "ciphertext": base64.b64encode(out["ciphertext"]).decode()
        }

    ops_raw = comparison_operator_recognizer(t2)
        
    raw_vals = value_entity_recognizer(t2)
    vals = []
    for typ, val, lo, hi in raw_vals:
        if typ == "STRING":
            continue
        if typ == "INTEGER" and YEAR_PATTERN.match(val):
            typ = "DATE"
        vals.append({"type": typ, "value": val, "span": (lo, hi)})

    query_str = None
    resolved_db = None
    rows = []
    commentary = ""
    error_message = None
    query_status = "no_sql"
    
    is_general_chat = not has_schema_entities and any(i in intent for i in ['greeting', 'general_question', 'unknown'])

    ollama_input_data = {
        "original_query": q,
        "intent": intent,
        "query_str": "N/A (No SQL generated yet)",
        "query_status": query_status,
        "denial_reason": "",
        "sql": "",
        "sample_rows_count": 0,
        "is_aggregate_query": is_aggregate_intent,
        "has_schema_entities": has_schema_entities
    }

    if is_general_chat:
        query_status = "general_chat"
        ollama_input_data["query_status"] = query_status
        commentary = await get_optimized_commentary(ollama_input_data, ai_used_for_intent)
    else:
        query_str, resolved_db = await generate_sql_with_query_builder(q, intent, ents, ops_raw, vals, user["role"])
        
        if query_str and resolved_db:
            print(f"\n===== Query Builder Generated SQL =====\nSQL: {query_str}\nDB: {resolved_db}")
            
            if not validate_query_access(user["role"], resolved_db, intent):
                query_status = "denied"
                reason = explain_denial(user["role"], resolved_db, intent)
                log_query(user["username"], user["role"], q, resolved_db, "denied", sql=query_str)
                ollama_input_data.update({
                    "query_str": query_str,
                    "query_status": query_status,
                    "denial_reason": reason,
                })
                commentary = await get_optimized_commentary(ollama_input_data, ai_used_for_intent)
                error_message = reason
            else:
                action_type = "read"
                if is_destructive_operation(intent):
                    if "INSERT_ROWS" in intent:
                        action_type = "insert"
                    elif "UPDATE_ROWS" in intent:
                        action_type = "update"
                    elif "DELETE_ROWS" in intent:
                        action_type = "delete"
                    elif any(drop_intent in intent for drop_intent in ["DROP_TABLE", "DROP_DATABASE", "TRUNCATE_TABLE"]):
                        action_type = "drop"
                                
                success, result = verify_query(
                    query_str,
                    host='localhost', user='root', password='root',
                    database=resolved_db
                )
                                
                if success:
                    query_status = "success"
                    log_query(user["username"], user["role"], q, resolved_db, action_type, sql=f"[QUERY_BUILDER] {query_str}")
                                            
                    if is_destructive_operation(intent):
                        rows = []
                        ollama_input_data.update({
                            "query_str": query_str,
                            "query_status": query_status,
                            "sample_rows_count": 0,
                        })
                    elif is_aggregate_intent:
                        rows = result
                        ollama_input_data.update({
                            "query_str": query_str,
                            "query_status": query_status,
                            "sample_rows_count": 1,
                        })
                    else:
                        rows = result[:5]
                        ollama_input_data.update({
                            "query_str": query_str,
                            "query_status": query_status,
                            "sample_rows_count": len(rows),
                        })
                                            
                    commentary = await get_optimized_commentary(ollama_input_data, ai_used_for_intent)
                else:
                    query_status = "fail"
                    log_query(user["username"], user["role"], q, resolved_db, "fail", sql=f"[QUERY_BUILDER_FAILED] {query_str}")
                    error_message = f"SQL Failed: {result}"
                    ollama_input_data.update({
                        "query_str": query_str,
                        "query_status": query_status,
                        "sql": result,
                    })
                    commentary = await get_optimized_commentary(ollama_input_data, ai_used_for_intent)
        else:
            query_status = "no_sql"
            ollama_input_data.update({
                "query_status": query_status,
                "query_str": "N/A (Query builder failed to generate SQL)"
            })
            commentary = await get_optimized_commentary(ollama_input_data, ai_used_for_intent)

    print(f"\n===== OPTIMIZED COMMENTARY =====\n{commentary}")
    print(f"[DEBUG] Total AI calls for this query: {1 if (ai_used_for_intent or (not has_schema_entities and query_status in ['general_chat', 'no_sql'])) else 0}")

    response_payload = {
        "sample_rows": rows,
        "commentary": commentary,
        "text_response": commentary,
        "query_status": query_status,
        "generated_sql": query_str if query_str else None,
        "operation_type": "destructive" if is_destructive_operation(intent) else "read",
        "used_query_builder": True if query_str else False,
        "ai_calls_used": 1 if (ai_used_for_intent or (not has_schema_entities and query_status in ['general_chat', 'no_sql'])) else 0
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
    
    ents = schema_entity_recognizer(final_tokens)
    has_schema_entities = has_meaningful_schema_entities(ents)
    
    intent, ai_used_for_intent = intent_recognizer.predict_from_tokens(final_tokens, ents)
    print(f"\n===== DETECTED INTENT =====\n{intent} (AI used: {ai_used_for_intent})")
        
    is_aggregate_intent = any(agg_intent in intent for agg_intent in ["AGGREGATE_AVG", "AGGREGATE_SUM", "AGGREGATE_MIN", "AGGREGATE_MAX"])

    if is_admin_only_operation(intent) and user["role"] != "admin":
        query_status = "denied"
        reason = f"Access denied: Only administrators can perform {', '.join([i for i in intent if 'INSERT' in i or 'UPDATE' in i or 'DELETE' in i or 'DROP' in i or 'TRUNCATE' in i])} operations."
            
        ollama_input_data = {
            "original_query": q,
            "intent": intent,
            "query_str": "N/A (Access denied)",
            "query_status": query_status,
            "denial_reason": reason,
            "sql": "",
            "sample_rows_count": 0,
            "is_aggregate_query": is_aggregate_intent,
            "has_schema_entities": has_schema_entities
        }
                
        commentary = await get_optimized_commentary(ollama_input_data, ai_used_for_intent)
        log_query(user["username"], user["role"], q, "N/A", "denied", sql="N/A (Admin-only operation)")
                
        return {
            "sample_rows": [],
            "commentary": commentary,
            "text_response": commentary,
            "query_status": query_status,
            "generated_sql": None,
            "error": reason,
            "ai_calls_used": 1 if (ai_used_for_intent or (not has_schema_entities and query_status in ['general_chat', 'no_sql'])) else 0
        }
        
    ops_raw = comparison_operator_recognizer(t2)
        
    raw_vals = value_entity_recognizer(t2)
    vals = []
    for typ, val, lo, hi in raw_vals:
        if typ == "STRING":
            continue
        if typ == "INTEGER" and YEAR_PATTERN.match(val):
            typ = "DATE"
        vals.append({"type": typ, "value": val, "span": (lo, hi)})

    query_str = None
    resolved_db = None
    rows = []
    commentary = ""
    error_message = None
    query_status = "no_sql"
    
    is_general_chat = not has_schema_entities and any(i in intent for i in ['greeting', 'general_question', 'unknown'])

    ollama_input_data = {
        "original_query": q,
        "intent": intent,
        "query_str": "N/A (No SQL generated yet)",
        "query_status": query_status,
        "denial_reason": "",
        "sql": "",
        "sample_rows_count": 0,
        "is_aggregate_query": is_aggregate_intent,
        "has_schema_entities": has_schema_entities
    }

    if is_general_chat:
        query_status = "general_chat"
        ollama_input_data["query_status"] = query_status
        commentary = await get_optimized_commentary(ollama_input_data, ai_used_for_intent)
        
    else:
        query_str, resolved_db = await generate_sql_with_query_builder(q, intent, ents, ops_raw, vals, user["role"])
        
        if query_str and resolved_db:
            print(f"\n===== Query Builder Generated SQL =====\nSQL: {query_str}\nDB: {resolved_db}")
            
            if not validate_query_access(user["role"], resolved_db, intent):
                query_status = "denied"
                reason = explain_denial(user["role"], resolved_db, intent)
                log_query(user["username"], user["role"], q, resolved_db, "denied", sql=query_str)
                ollama_input_data.update({
                    "query_str": query_str,
                    "query_status": query_status,
                    "denial_reason": reason,
                })
                commentary = await get_optimized_commentary(ollama_input_data, ai_used_for_intent)
                error_message = reason
            else:
                action_type = "read"
                if is_destructive_operation(intent):
                    if "INSERT_ROWS" in intent:
                        action_type = "insert"
                    elif "UPDATE_ROWS" in intent:
                        action_type = "update"
                    elif "DELETE_ROWS" in intent:
                        action_type = "delete"
                    elif any(drop_intent in intent for drop_intent in ["DROP_TABLE", "DROP_DATABASE", "TRUNCATE_TABLE"]):
                        action_type = "drop"
                                
                success, result = verify_query(
                    query_str,
                    host='localhost', user='root', password='root',
                    database=resolved_db
                )
                                
                if success:
                    query_status = "success"
                    log_query(user["username"], user["role"], q, resolved_db, action_type, sql=f"[QUERY_BUILDER] {query_str}")
                                            
                    if is_destructive_operation(intent):
                        rows = []
                        ollama_input_data.update({
                            "query_str": query_str,
                            "query_status": query_status,
                            "sample_rows_count": 0,
                        })
                    elif is_aggregate_intent:
                        rows = result
                        ollama_input_data.update({
                            "query_str": query_str,
                            "query_status": query_status,
                            "sample_rows_count": 1,
                        })
                    else:
                        rows = result[:5]
                        ollama_input_data.update({
                            "query_str": query_str,
                            "query_status": query_status,
                            "sample_rows_count": len(rows),
                        })
                                            
                    commentary = await get_optimized_commentary(ollama_input_data, ai_used_for_intent)
                else:
                    query_status = "fail"
                    log_query(user["username"], user["role"], q, resolved_db, "fail", sql=f"[QUERY_BUILDER_FAILED] {query_str}")
                    error_message = f"SQL Failed: {result}"
                    ollama_input_data.update({
                        "query_str": query_str,
                        "query_status": query_status,
                        "sql": result,
                    })
                    commentary = await get_optimized_commentary(ollama_input_data, ai_used_for_intent)
        else:
            query_status = "no_sql"
            ollama_input_data.update({
                "query_status": query_status,
                "query_str": "N/A (Query builder failed to generate SQL)"
            })
            commentary = await get_optimized_commentary(ollama_input_data, ai_used_for_intent)

    print(f"\n===== OPTIMIZED COMMENTARY =====\n{commentary}")
    
    ai_calls_used = 0
    if ai_used_for_intent:
        ai_calls_used += 1
    if not has_schema_entities and query_status in ['general_chat', 'no_sql'] and not ai_used_for_intent:
        ai_calls_used += 1
    
    print(f"[DEBUG] Total AI calls for this query: {ai_calls_used}")

    response_payload = {
        "sample_rows": rows,
        "commentary": commentary,
        "text_response": commentary,
        "query_status": query_status,
        "generated_sql": query_str if query_str else None,
        "operation_type": "destructive" if is_destructive_operation(intent) else "read",
        "used_query_builder": True if query_str else False,
        "ai_calls_used": ai_calls_used
    }
        
    if error_message:
        response_payload["error"] = error_message

    return response_payload

@app.post("/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    temp_file_path = f"./temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        with open(temp_file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read file: {e}")
    finally:
        os.remove(temp_file_path)
        
    normalized_text, _ = normalize_dates(content.lower())
    normalized_text, _ = normalize_units(normalized_text)
        
    tokens = tokenize(normalized_text)["Final Tokens"]
        
    schema_entities = schema_entity_recognizer(tokens)
    value_entities = value_entity_recognizer(normalized_text)
        
    extracted_pills = set()
        
    for entity in schema_entities:
        extracted_pills.add(entity['value'])
            
    for entity_type, value, _, _ in value_entities:
        if entity_type != "STRING":
            extracted_pills.add(value)
            
    return {"entities": sorted(list(extracted_pills))}

@app.post("/summarize-document")
async def summarize_document(file: UploadFile = File(...)):
    global _ollama_client
        
    temp_file_path = f"./temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    content = ""
    try:
        with open(temp_file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read file: {e}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    if not content:
        raise HTTPException(status_code=400, detail="Document is empty.")
    try:
        prompt = f"Please provide a concise summary of the following document:\n\n---\n\n{content}\n\n---\n\nSummary:"
                
        response = await _ollama_client.post(
            "http://localhost:11434/api/generate",
            json={
                "prompt": prompt,
                "model": "gemma:2b",
                "stream": False
            }
        )
        response.raise_for_status()
                
        json_response = response.json()
        summary = json_response.get("response", "").strip()
                
        if not summary:
            raise HTTPException(status_code=500, detail="Failed to generate summary from the model.")
                    
        return {"summary": summary}
            
    except Exception as e:
        print(f"Ollama summarization error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while generating the summary.")

@app.post("/summarize-document-with-auth")
async def summarize_document_with_auth(
    file: UploadFile = File(...),
    username: str = Form(...),
    password: str = Form(...)
):
    user = get_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if username not in _active_sessions:
        raise HTTPException(status_code=403, detail="User not actively logged in")
    
    print(f"Document summarization requested by user: {username} ({user['role']})")
    
    result = await summarize_document(file)
    
    result["requested_by"] = username
    result["user_role"] = user["role"]
    
    return result

@app.get("/logs/access")
def access_logs(admin_user: str, admin_pass: str):
    user = get_user(admin_user, admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(403, "Only admin can view logs.")
        
    try:
        conn = mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="root", 
            database="your_auth_db"
        )
        cur = conn.cursor(dictionary=True)
                
        cur.execute("SHOW TABLES LIKE 'access_log'")
        table_exists = cur.fetchone()
                
        if not table_exists:
            cur.close()
            conn.close()
            return {"logs": [], "error": "Access log table does not exist"}
                
        cur.execute("""
            SELECT username, status, event_time as timestamp 
            FROM access_log 
            ORDER BY event_time DESC 
            LIMIT 20
        """)
        direct_logs = cur.fetchall()
                
        formatted_logs = []
        for log in direct_logs:
            formatted_log = {
                "username": log.get("username", "N/A"),
                "action": log.get("status", "N/A"),
                "timestamp": log.get("timestamp").strftime("%Y-%m-%d %H:%M:%S") if log.get("timestamp") else "N/A"
            }
            formatted_logs.append(formatted_log)
                
        cur.close()
        conn.close()
                
        return {"logs": formatted_logs}
            
    except mysql.connector.Error as db_error:
        return {"logs": [], "error": f"Database connection error: {str(db_error)}"}
    except Exception as e:
        return {"logs": [], "error": f"Unexpected error: {str(e)}"}

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
    log_access_to_db(data.target_user, f"ADMIN_LOCKOUT_{data.duration_minutes}m")
    return {"locked_user": data.target_user, "until": until.strftime("%Y-%m-%d %H:%M:%S")}

@app.post("/message")
def send_message(data: MessageRequest):
    user = get_user(data.username, data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials.")
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
        cur = conn.cursor()
        cur.execute("INSERT INTO messages(from_user, to_user, message) VALUES(%s, %s, %s)", (data.username, "admin", data.message))
        conn.commit()
    except Exception as e:
        raise HTTPException(500, f"Database error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
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
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
        cur = conn.cursor()
        cur.execute("INSERT INTO messages(from_user,to_user,message) VALUES(%s,%s,%s)", ("admin", data.target_user, data.message))
        conn.commit()
    except Exception as e:
        raise HTTPException(500, f"Database error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cur.close()
            conn.close()
    return {"message": f"Message sent to {data.target_user}."}

@app.get("/messages")
def user_inbox(username: str, password: str):
    user = get_user(username, password)
    if not user:
        raise HTTPException(401, "Invalid credentials.")
            
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
        cur = conn.cursor(dictionary=True)
        query = """
            SELECT id, from_user, to_user, message, created_at as time
            FROM messages 
            WHERE from_user = %s OR to_user = %s
            ORDER BY created_at ASC
        """
        cur.execute(query, (username, username))
        messages = cur.fetchall()
                
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": msg["id"],
                "from": msg["from_user"],
                "to": msg["to_user"],
                "message": msg["message"],
                "time": msg['time'].strftime('%Y-%m-%d %H:%M:%S') if msg.get('time') else None
            })
        return {"messages": formatted_messages}
    except Exception as e:
        print(f"Error fetching messages for {username}: {e}")
        return {"messages": []}
    finally:
        if 'conn' in locals() and conn.is_connected():
            cur.close()
            conn.close()

@app.get("/admin/messages")
def view_all_messages(admin_user: str, admin_pass: str):
    user = get_user(admin_user, admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(403, "Only admin can view messages.")
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
        cur = conn.cursor()
        cur.execute("""
            SELECT id, from_user, to_user, message, created_at 
            FROM messages 
            ORDER BY created_at DESC 
            LIMIT 20
        """)
        rows = cur.fetchall()
    except Exception as e:
        raise HTTPException(500, f"Database error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cur.close()
            conn.close()
    return {"messages": [{"id": r[0], "from": r[1], "to": r[2], "message": r[3], "time": r[4].strftime("%Y-%m-%d %H:%M:%S")} for r in rows]}

@app.get("/admin/conversations")
def get_conversations(admin_user: str, admin_pass: str):
    user = get_user(admin_user, admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(403, "Authentication failed or user is not an admin.")
            
    conversations = get_admin_conversations(admin_user)
    return {"conversations": conversations}

@app.get("/admin/conversation/{username}")
def get_conversation_messages_admin(username: str, admin_user: str, admin_pass: str):
    user = get_user(admin_user, admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(403, "Authentication failed or user is not an admin.")
            
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT id, from_user, to_user, message, created_at as timestamp 
            FROM messages 
            WHERE (from_user = %s AND to_user = %s) OR (from_user = %s AND to_user = %s)
            ORDER BY created_at ASC
        """
        cursor.execute(query, (admin_user, username, username, admin_user))
        messages = cursor.fetchall()
                        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": msg["id"],
                "from": msg["from_user"],
                "to": msg["to_user"],
                "message": msg["message"],
                "time": msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if msg.get('time') else None
            })
        return {"messages": formatted_messages}
    except Exception as e:
        print(f"Error fetching messages for {username}: {e}")
        return {"messages": []}
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@app.get("/user/conversation")
def user_conversation(username: str, password: str):
    user = get_user(username, password)
    if not user:
        raise HTTPException(401, "Invalid credentials.")

    if user["role"] == "admin":
        raise HTTPException(403, "Admin users should use /admin/conversations endpoint.")

    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
        cur = conn.cursor(dictionary=True)
            
        cur.execute("""
            SELECT id, from_user, to_user, message, created_at as timestamp
            FROM messages 
            WHERE (from_user = %s AND to_user = 'admin')
               OR (from_user = 'admin' AND to_user = %s)
            ORDER BY created_at ASC
        """, (username, username))
            
        messages = cur.fetchall()
            
        for msg in messages:
            if 'timestamp' in msg and hasattr(msg['timestamp'], 'strftime'):
                msg['timestamp'] = msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            
        cur.close()
        conn.close()
            
        return {
            "conversation": {
                "with_user": "admin",
                "messages": messages,
                "message_count": len(messages)
            }
        }
        
    except Exception as e:
        print(f"Error fetching user conversation for {username}: {e}")
        raise HTTPException(500, f"Database error: {e}")

@app.post("/user/message")
def send_user_message(data: MessageRequest):
    user = get_user(data.username, data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials.")

    if user["role"] == "admin":
        raise HTTPException(403, "Admin users should use /admin/message endpoint.")

    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
        cur = conn.cursor()
        cur.execute("INSERT INTO messages(from_user, to_user, message) VALUES(%s, %s, %s)", 
                    (data.username, "admin", data.message))
        conn.commit()
    except Exception as e:
        raise HTTPException(500, f"Database error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cur.close()
            conn.close()
        
    return {"message": "Message sent to admin successfully."}

@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    username: str = Form(...),
    password: str = Form(...),
    target_user: str = Form(...)):
        
    user = get_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
            
    message_text = f"Shared a file: {file.filename}"
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="your_auth_db")
        cur = conn.cursor()
        query = "INSERT INTO messages(from_user, to_user, message) VALUES(%s, %s, %s)"
        cur.execute(query, (username, target_user, message_text))
        conn.commit()
    except Exception as e:
        raise HTTPException(500, f"Database error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cur.close()
            conn.close()
                
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

@app.get("/download-document/{filename}")
async def download_document(filename: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

@app.post("/admin/add_user")
def add_user(data: AddUserRequest):
    user = get_user(data.admin_user, data.admin_pass)
    if not user or user["role"] != "admin":
        raise HTTPException(403, "Only admin can add users.")
    if user_exists(data.target_user):
        raise HTTPException(400, "Username already exists.")
    pwd = create_user(data.target_user, data.department, data.position)
    return {"username": data.target_user, "password": pwd}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
