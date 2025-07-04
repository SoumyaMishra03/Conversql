import re
import mysql.connector

def detect_database_from_query(query):
    m = re.search(r'\bfrom\s+([a-zA-Z0-9_\.]+)', query, re.IGNORECASE)
    if m:
        table = m.group(1)
        if '.' in table:
            db, _ = table.split('.', 1)
            return db
    return None

def verify_query(query, host='localhost', user='root', password='root', database=None):
    if database is None:
        database = detect_database_from_query(query)
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return True, rows
    except mysql.connector.Error as e:
        return False, str(e)
