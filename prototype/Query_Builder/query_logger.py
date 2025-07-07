from Query_Builder.users_manager import get_db_connection
from mysql.connector import Error, errorcode

def log_query(username, role, raw_query, db, action, sql=None):
    """
    Log each executed SQL query into the `sql_log` table.
    Creates the table on first call if needed.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        insert_sql = """
            INSERT INTO sql_log
              (username, role, raw_query, target_db, action, sql_text)
            VALUES
              (%s, %s, %s, %s, %s, %s)
        """
        params = (username, role, raw_query, db, action, sql or "")
        try:
            cur.execute(insert_sql, params)
            conn.commit()
        except Error as e:
            if e.errno == errorcode.ER_NO_SUCH_TABLE:
                # create table then retry
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS sql_log (
                      id         INT AUTO_INCREMENT PRIMARY KEY,
                      username   VARCHAR(50),
                      role       VARCHAR(20),
                      raw_query  TEXT,
                      target_db  VARCHAR(100),
                      action     VARCHAR(20),
                      sql_text   LONGTEXT,
                      log_time   DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                cur.execute(insert_sql, params)
                conn.commit()
            else:
                print("❌ query_logger MySQL error (log_query):", e)
    except Error as e:
        print("❌ query_logger MySQL error (connection):", e)
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def log_access(username: str, status: str):
    """
    Log every login attempt or lockout into `access_log`.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO access_log (username, status) VALUES (%s, %s)",
            (username, status)
        )
        conn.commit()
    except Error as e:
        print("❌ query_logger MySQL error (log_access):", e)
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def fetch_access_logs(limit: int = 20):
    """
    Return the most recent `limit` rows from access_log.
    Each row is a tuple: (id, username, event_time, status).
    """
    conn = None
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute(
            "SELECT id, username, event_time, status "
            "FROM access_log "
            "ORDER BY event_time DESC "
            "LIMIT %s",
            (limit,)
        )
        return cur.fetchall()
    except Error as e:
        print("❌ query_logger MySQL error (fetch_access_logs):", e)
        return []
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()
