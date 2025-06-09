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
        for row in reader:
            query = """
                INSERT INTO properties (
                    Name, PropertyTitle, Price, Description
                ) VALUES (%s, %s, %s, %s)
            """
            values = (
                row['Name'],
                row['Property Title'],
                row['Price'],
                row['Description']
            )
            try:
                cursor.execute(query, values)
                print(f"Inserted property: {values}")
            except mysql.connector.Error as e:
                print(f"Error inserting property: {e}")


def insert_locations(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = """
                INSERT INTO locations (
                    Name, Location, Total_Area, Price_per_SQFT
                ) VALUES (%s, %s, %s, %s)
            """
            values = (
                row['Name'],
                row['Location'],
                float(row['Total_Area']) if row['Total_Area'] else None,
                float(row['Price_per_SQFT']) if row['Price_per_SQFT'] else None
            )
            try:
                cursor.execute(query, values)
                print(f"Inserted location: {values}")
            except mysql.connector.Error as e:
                print(f"Error inserting location: {e}")


def insert_features(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = """
                INSERT INTO features (
                    Name, Baths, Balcony
                ) VALUES (%s, %s, %s)
            """
            values = (
                row['Name'],
                int(row['Baths']) if row['Baths'] else None,
                row['Balcony']
            )
            try:
                cursor.execute(query, values)
                print(f"Inserted feature: {values}")
            except mysql.connector.Error as e:
                print(f"Error inserting feature: {e}")

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
        print(f"Database error: {err}")

    finally:
        cursor.close()
        cnx.close()

if __name__ == "__main__":
    main()
