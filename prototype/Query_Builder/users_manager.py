import mysql.connector
from mysql.connector import Error

# MySQL auth‐DB connection settings
MYSQL_HOST     = "localhost"
MYSQL_PORT     = 3306
MYSQL_USER     = "root"
MYSQL_PASSWORD = "Helloworld@2025" 

def get_db_connection():
    """
    Returns a connection to the auth database which holds
    `users`, `access_log` and `sql_log` tables.
    """
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database="your_auth_db"
    )

def get_user(username: str, password: str):
    """
    Look up `username` in the users table, verify `password`.
    Returns {"username":…, "role":…} or None.
    """
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
        print("❌ users_manager MySQL error:", e)
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()
    return None
