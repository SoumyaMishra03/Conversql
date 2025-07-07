#!/usr/bin/env python3

import mysql.connector
from mysql.connector import Error

HOST     = "localhost"
PORT     = 3306
USER     = "root"
PASSWORD = "Helloworld@2025"

def main():
    try:
        conn = mysql.connector.connect(
            host=HOST, port=PORT, user=USER, password=PASSWORD
        )
        cur = conn.cursor()

        # 1) Create the auth DB
        cur.execute("CREATE DATABASE IF NOT EXISTS your_auth_db;")
        cur.execute("USE your_auth_db;")

        # 2) users table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
          username VARCHAR(50) PRIMARY KEY,
          password VARCHAR(255) NOT NULL,
          role     VARCHAR(20)  NOT NULL
        );
        """)

        # 3) access_log table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS access_log (
          id         INT AUTO_INCREMENT PRIMARY KEY,
          username   VARCHAR(50),
          event_time DATETIME DEFAULT CURRENT_TIMESTAMP,
          status     VARCHAR(50)
        );
        """)

        # 4) sql_log table
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

        # 5) Seed an admin user (and any others)
        users = [
            ("admin",    "rootaccess",    "admin"),
            ("soumya",  "nebula123",          "science"),
            ("anita",    "headlines22",        "news"),
            ("kabir",    "rocketmissions",     "missions")
        ]
        cur.executemany("""
          REPLACE INTO users (username, password, role)
          VALUES (%s, %s, %s);
        """, users)

        conn.commit()
        print("✅ your_auth_db + tables created; users seeded.")
    except Error as e:
        print("❌ MySQL error during setup:", e)
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

if __name__ == "__main__":
    main()
