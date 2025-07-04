import datetime

LOG_FILE = "query_log.txt"

def log_query(username, role, query, db, access, sql=None, success=True, error=None):
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] User: {username} | Role: {role} | Access: {access}\n")
        f.write(f"  Query: {query}\n")
        f.write(f"  Target DB: {db}\n")
        if sql:
            f.write(f" SQL: {sql}\n")
        if success:
            f.write("  Status: SUCCESS\n")
        else:
            f.write(f" Status: FAILED | Error: {error}\n")
        f.write("-" * 80 + "\n")
