import mysql.connector
import csv
import re
import os

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'space_missions_db'
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def clean_float(value):
    if not value or value.strip() == "":
        return None
    value = value.replace(",", "").strip()
    value = re.sub(r"[^\d.\-]", "", value)
    try:
        return float(value)
    except ValueError:
        return None

def insert_organizations(cursor, filename):
    path = os.path.join(BASE_DIR, filename)
    with open(path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        seen = set()
        for row in reader:
            key = (row['Organisation'], row['Location'])
            if key in seen:
                continue
            seen.add(key)
            data.append((row['Organisation'], row['Location']))
    query = """
        INSERT IGNORE INTO organizations (Organisation, Location)
        VALUES (%s, %s)
    """
    cursor.executemany(query, data)
    print(f"Inserted {len(data)} organizations.")

def insert_rockets(cursor, filename):
    path = os.path.join(BASE_DIR, filename)
    with open(path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        for row in reader:
            data.append((
                row['Organisation'],
                row['Details'],
                row['Rocket_Status'],
                clean_float(row['Price'])
            ))
    query = """
        INSERT INTO rockets (Organisation, Details, Rocket_Status, Price)
        VALUES (%s, %s, %s, %s)
    """
    cursor.executemany(query, data)
    print(f"Inserted {len(data)} rockets.")

def insert_missions(cursor, filename):
    path = os.path.join(BASE_DIR, filename)
    with open(path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = [(row['Organisation'], row['Mission_Status']) for row in reader]
    query = """
        INSERT INTO missions (Organisation, Mission_Status)
        VALUES (%s, %s)
    """
    cursor.executemany(query, data)
    print(f"Inserted {len(data)} missions.")

def main():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        insert_organizations(cursor, 'organizations.csv')
        insert_rockets(cursor, 'rockets.csv')
        insert_missions(cursor, 'missions.csv')
        conn.commit()
        print("All data inserted successfully.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
