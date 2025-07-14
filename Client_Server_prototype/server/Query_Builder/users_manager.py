import mysql.connector
from mysql.connector import Error
import secrets

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

def user_exists(username: str):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT username FROM users WHERE username=%s",
            (username,)
        )
        exists = cur.fetchone() is not None
        return exists
    except Error as e:
        print("users_manager MySQL error:", e)
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()
    return False

def create_user(new_username: str, role: str, position: str):
    password = secrets.token_hex(4)
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, role, position) VALUES (%s, %s, %s, %s)",
            (new_username, password, role, position)
        )
        conn.commit()
        return password
    except Error as e:
        print("users_manager MySQL error:", e)
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()
    return None
