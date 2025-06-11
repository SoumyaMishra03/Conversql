import mysql.connector
import csv

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'real_estate_db'
}

def insert_properties(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        seen_names = set()
        for row in reader:
            name = row['Name']
            name_key = name.strip().lower()  
            if name_key in seen_names:
                continue  
            seen_names.add(name_key)
            data.append((name, row['Property Title'], row['Price'], row['Description']))

    query = """
        INSERT INTO properties (
            Name, PropertyTitle, Price, Description
        ) VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} unique rows into properties.")
    except mysql.connector.Error as e:
        print(f"Error inserting into properties: {e}")

def insert_locations(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        seen_names = set()
        for row in reader:
            name = row['Name']
            name_key = name.strip().lower()
            if name_key in seen_names:
                continue
            try:
                seen_names.add(name_key)
                data.append((
                    name,
                    row['Location'],
                    float(row['Total_Area']) if row['Total_Area'] else None,
                    float(row['Price_per_SQFT']) if row['Price_per_SQFT'] else None
                ))
            except ValueError as e:
                print(f"Skipped invalid row in locations: {row} | Error: {e}")

    query = """
        INSERT INTO locations (
            Name, Location, Total_Area, Price_per_SQFT
        ) VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} unique rows into locations.")
    except mysql.connector.Error as e:
        print(f"Error inserting into locations: {e}")

def insert_features(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        seen_names = set()
        for row in reader:
            name = row['Name']
            name_key = name.strip().lower()
            if name_key in seen_names:
                continue
            try:
                seen_names.add(name_key)
                data.append((
                    name,
                    int(row['Baths']) if row['Baths'] else None,
                    row['Balcony']
                ))
            except ValueError as e:
                print(f"Skipped invalid row in features: {row} | Error: {e}")

    query = """
        INSERT INTO features (
            Name, Baths, Balcony
        ) VALUES (%s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} unique rows into features.")
    except mysql.connector.Error as e:
        print(f"Error inserting into features: {e}")

def main():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        insert_properties(cursor, 'properties_table.csv')
        insert_locations(cursor, 'locations_table.csv')
        insert_features(cursor, 'features_table.csv')

        cnx.commit()
        print("All data inserted successfully.")

    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")

    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

if __name__ == "__main__":
    main()
