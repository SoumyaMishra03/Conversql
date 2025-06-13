import mysql.connector  # or any other DB adapter (e.g., psycopg2 for PostgreSQL)

# Establish a database connection (update with your credentials)
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Helloworld@2025",
        database="airline_db"
    )

# ***** Airports Functions *****

def get_airports_by_country(country_code):
    query = "SELECT * FROM airports WHERE CountryCode = %s;"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (country_code,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_airports_by_continent(continent):
    query = "SELECT * FROM airports WHERE Continent = %s;"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (continent,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def search_airport_by_name(airport_name):
    query = "SELECT * FROM airports WHERE AirportName LIKE %s;"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, ('%' + airport_name + '%',))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# ***** Flights Functions *****

def get_flights_by_date(departure_date):
    query = "SELECT * FROM flights WHERE DepartureDate = %s;"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (departure_date,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_flights_by_pilot(pilot_name):
    query = "SELECT * FROM flights WHERE PilotName = %s;"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (pilot_name,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_cancelled_flights():
    query = "SELECT PassengerID, DepartureDate FROM flights WHERE FlightStatus = 'Cancelled';"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# ***** Passengers Functions *****

def get_passengers_by_nationality(nationality):
    query = "SELECT * FROM passengers WHERE Nationality = %s;"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (nationality,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_passenger_by_id(passenger_id):
    query = "SELECT * FROM passengers WHERE PassengerID = %s;"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (passenger_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_average_age_by_nationality():
    query = "SELECT Nationality, AVG(Age) AS AverageAge FROM passengers GROUP BY Nationality;"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Sample usage - these can be triggered via UI or NLP inputs
if __name__ == '__main__':
    # Example: Get all US airports
    print("US Airports:")
    print(get_airports_by_country('US'))
    
    # Example: Get flights on a specific date
    print("Flights on 2025-06-20:")
    print(get_flights_by_date('2025-06-20'))
    
    # Example: Get details for a specific passenger
    print("Passenger with ID '00kDrw':")
    print(get_passenger_by_id('00kDrw'))
