import mysql.connector
import csv
import os

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'stars_db'
}

def clean_float(val):
    try:
        return float(val.replace(",", "").strip()) if val and val.strip() else None
    except:
        return None

def insert_stars(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = [
            (
                row['Star_name'],
                clean_float(row['Distance']),
                clean_float(row['Mass']),
                clean_float(row['Radius']),
                clean_float(row['Luminosity'])
            ) for row in reader
        ]
    query = """
        INSERT INTO stars (Star_name, Distance, Mass, Radius, Luminosity)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.executemany(query, data)
    print(f"Inserted {len(data)} rows into stars.")

def main():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, 'stars.csv')
        insert_stars(cursor, csv_path)

        conn.commit()
        cursor.close()
        conn.close()
        print("All data inserted successfully.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except FileNotFoundError as ferr:
        print(f"File error: {ferr}")

if __name__ == "__main__":
    main()
