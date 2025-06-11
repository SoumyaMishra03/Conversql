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
        for row in reader:
            age_val = int(row['Age']) if row['Age'] else None
            data.append((
                row['Passenger ID'],
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
        print(f"Inserted {len(data)} passengers.")
    except mysql.connector.Error as e:
        print(f"Error inserting passengers: {e}")

def insert_airports(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = [
            (
                row['Airport Name'],
                row['Airport Country Code'],
                row['Country Name'],
                row['Airport Continent']
            ) for row in reader
        ]

    query = """
        INSERT INTO airports (AirportName, CountryCode, CountryName, Continent)
        VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} airports.")
    except mysql.connector.Error as e:
        print(f"Error inserting airports: {e}")

def insert_flights(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = [
            (
                row['Passenger ID'],
                row['Departure Date'],
                row['Pilot Name'],
                row['Flight Status']
            ) for row in reader
        ]

    query = """
        INSERT INTO flights (PassengerID, DepartureDate, PilotName, FlightStatus)
        VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} flights.")
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
        print("All data inserted successfully!")

    except mysql.connector.Error as e:
        print(f"Database error: {e}")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
