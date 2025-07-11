import mysql.connector
from mysql.connector import Error
MYSQL_HOST     = "localhost"
MYSQL_USER     = "root"
MYSQL_PASSWORD = "root"

def get_db_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database="your_auth_db"
    )

def get_user(username: str, password: str):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT username, password, role FROM users WHERE username=%s",
            (username,)
        )
        row = cur.fetchone()
        if row and row["password"] == password:
            return {"username": row["username"], "role": row["role"]}
    except Error as e:
        print("users_manager MySQL error:", e)
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()
    return None
