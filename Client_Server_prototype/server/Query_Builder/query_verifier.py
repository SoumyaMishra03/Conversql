import mysql.connector
from mysql.connector import Error

def verify_query(sql, host, user, password, database=None):
    conn = None
    try:
        conn = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return True, rows
    except Error as e:
        return False, str(e)
    finally:
        if 'cur' in locals():
            cur.close()
        if conn and conn.is_connected():
            conn.close()
