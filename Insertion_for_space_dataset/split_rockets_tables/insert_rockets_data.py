import mysql.connector
import csv
import re
import time

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Helloworld@2025',
    'database': 'rockets_db'
}

CHUNK_SIZE = 500

def clean_float(value):
    if not value or value.strip() == "":
        return None
    value = value.replace(",", "").strip()
    value = re.sub(r"[^\d.\-]", "", value)
    try:
        return float(value)
    except ValueError:
        return None

def clean_int(value):
    f = clean_float(value)
    return int(f) if f is not None else None

def clean_price(value):
    if "million" in value.lower():
        f = clean_float(value)
        return f if f is None else f  
    return clean_float(value)

def insert_in_chunks(cursor, query, data, label):
    total = len(data)
    print(f"Inserting {total} rows into {label}...")
    for i in range(0, total, CHUNK_SIZE):
        chunk = data[i:i + CHUNK_SIZE]
        try:
            cursor.executemany(query, chunk)
            print(f"  → Inserted {i + len(chunk)} / {total}")
        except mysql.connector.Error as e:
            print(f" Failed to insert chunk at row {i}: {e}")
            time.sleep(1)

def insert_general_info(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = [(row['Name'], row['Cmp'], row['Wiki'], row['Status']) for row in reader]
    query = """
        INSERT INTO rocket_general_info (Name, Cmp, Wiki, Status)
        VALUES (%s, %s, %s, %s)
    """
    insert_in_chunks(cursor, query, data, "rocket_general_info")

def insert_technical_specs(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = [(
            row['Name'],
            clean_float(row['Liftoff Thrust']),
            clean_float(row['Payload to LEO']),
            clean_int(row['Stages']),
            clean_int(row['Strap-ons']),
            clean_float(row['Rocket Height']),
            clean_price(row['Price']),
            clean_float(row['Payload to GTO']),
            clean_float(row['Fairing Diameter']),
            clean_float(row['Fairing Height'])
        ) for row in reader]
    query = """
        INSERT INTO rocket_technical_specs (
            Name, Liftoff_Thrust, Payload_LEO, Stages, Strap_ons,
            Rocket_Height_m, Price_MUSD, Payload_GTO, Fairing_Diameter_m, Fairing_Height_m
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    insert_in_chunks(cursor, query, data, "rocket_technical_specs")

def main():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        insert_general_info(cursor, 'rocket_general_info.csv')
        insert_technical_specs(cursor, 'rocket_technical_specs.csv')

        conn.commit()
        print(" All data inserted successfully.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()