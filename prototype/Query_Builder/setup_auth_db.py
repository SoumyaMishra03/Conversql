import mysql.connector
from mysql.connector import Error

HOST     = "localhost"
USER     = "root"
PASSWORD = "root"

def main():
    try:
        conn = mysql.connector.connect(
            host=HOST, user=USER, password=PASSWORD
        )
        cur = conn.cursor()
        cur.execute("CREATE DATABASE IF NOT EXISTS your_auth_db;")
        cur.execute("USE your_auth_db;")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
          username VARCHAR(50) PRIMARY KEY,
          password VARCHAR(255) NOT NULL,
          role     VARCHAR(20)  NOT NULL
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS access_log (
          id         INT AUTO_INCREMENT PRIMARY KEY,
          username   VARCHAR(50),
          event_time DATETIME DEFAULT CURRENT_TIMESTAMP,
          status     VARCHAR(50)
        );
        """)
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
        );
        """)
        users = [
            ("admin",  "rootaccess",      "admin"),
            ("soumya", "nebula123",       "science"),
            ("anita",  "headlines22",     "news"),
            ("kabir",  "rocketmissions",  "missions")
        ]
        cur.executemany("""
          REPLACE INTO users (username, password, role)
          VALUES (%s, %s, %s);
        """, users)

        conn.commit()
        print("your_auth_db and tables created; users seeded.")
    except Error as e:
        print("MySQL error during setup:", e)
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

if __name__ == "__main__":
    main()
