import os
from datetime import datetime
import traceback

LOG_DIR          = os.path.dirname(__file__) or "."
QUERY_LOG_FILE   = os.path.join(LOG_DIR, "query_log.txt")
ACCESS_LOG_FILE  = os.path.join(LOG_DIR, "access_log.txt")

def log_query(username, role, raw_query, db, action, sql=None):
    """
    Append one line to query_log.txt and print debug info if it fails.
    """
    line = [
        datetime.now().isoformat(sep=" ", timespec="seconds"),
        username,
        role,
        action,
        db or "",
        raw_query.replace("\n"," "),
        sql or ""
    ]
    out = "\t".join(line) + "\n"
    try:
        # DEBUG: let me know where this is
        print(f"[DEBUG] Writing to query log at: {QUERY_LOG_FILE}")
        with open(QUERY_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(out)
            f.flush()
    except Exception as e:
        print(f"[ERROR] Could not write to {QUERY_LOG_FILE}: {e}")
        traceback.print_exc()

def log_access(username: str, status: str):
    """
    Append one line to access_log.txt
    """
    line = [
        datetime.now().isoformat(sep=" ", timespec="seconds"),
        username,
        status
    ]
    out = "\t".join(line) + "\n"
    try:
        print(f"[DEBUG] Writing to access log at: {ACCESS_LOG_FILE}")
        with open(ACCESS_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(out)
            f.flush()
    except Exception as e:
        print(f"[ERROR] Could not write to {ACCESS_LOG_FILE}: {e}")
        traceback.print_exc()

def fetch_access_logs(limit: int = 20):
    """
    Read the last `limit` lines from access_log.txt
    """
    try:
        if not os.path.exists(ACCESS_LOG_FILE):
            return []
        with open(ACCESS_LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        last = lines[-limit:]
        start_no = max(1, len(lines) - len(last) + 1)
        result = []
        for idx, ln in enumerate(last, start=start_no):
            parts = ln.rstrip("\n").split("\t")
            if len(parts) >= 3:
                ts, usernm, status = parts[:3]
                result.append((idx, usernm, ts, status))
        return result
    except Exception as e:
        print(f"[ERROR] Could not read {ACCESS_LOG_FILE}: {e}")
        traceback.print_exc()
        return []