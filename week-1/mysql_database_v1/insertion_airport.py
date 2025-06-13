import mysql.connector
import csv

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'airline_db'
}

def insert_passengers(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        seen = set()
        for row in reader:
            key = row['Passenger ID']
            if key in seen:
                continue
            seen.add(key)
            age_val = int(row['Age']) if row['Age'] else None
            data.append((
                key,
                row['First Name'],
                row['Last Name'],
                row['Gender'],
                age_val,
                row['Nationality']
            ))

    query = """
        INSERT INTO passengers (PassengerID, FirstName, LastName, Gender, Age, Nationality)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} unique passengers.")
    except mysql.connector.Error as e:
        print(f"Error inserting passengers: {e}")

def insert_airports(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        seen = set()
        for row in reader:
            key = (row['Airport Name'], row['Airport Country Code'])
            if key in seen:
                continue
            seen.add(key)
            data.append((
                row['Airport Name'],
                row['Airport Country Code'],
                row['Country Name'],
                row['Airport Continent']
            ))

    query = """
        INSERT INTO airports (AirportName, CountryCode, CountryName, Continent)
        VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} unique airports.")
    except mysql.connector.Error as e:
        print(f"Error inserting airports: {e}")

def insert_flights(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        seen = set()
        for row in reader:
            key = (row['Passenger ID'], row['Departure Date'], row['Pilot Name'], row['Flight Status'])
            if key in seen:
                continue
            seen.add(key)
            data.append(key)

    query = """
        INSERT INTO flights (PassengerID, DepartureDate, PilotName, FlightStatus)
        VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} unique flights.")
    except mysql.connector.Error as e:
        print(f"Error inserting flights: {e}")

def main():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        insert_passengers(cursor, 'passengers_table.csv')
        insert_airports(cursor, 'airports_table.csv')
        insert_flights(cursor, 'flights_table.csv')

        conn.commit()
        print("All data inserted successfully.")

    except mysql.connector.Error as e:
        print(f"Database error: {e}")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
