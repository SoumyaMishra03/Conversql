import mysql.connector
from mysql.connector import errorcode

def create_database(cursor, db_name):
    """Creates the target database if it doesn't already exist."""
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created or already exists.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    """
    Creates the necessary tables for the airline dataset with:
    passengers, airports, and flights.
    """
    TABLES = {}

    # ----------------------------------------------
    # Passengers Table: holds passenger details.
    # ----------------------------------------------
    TABLES['passengers'] = (
        "CREATE TABLE IF NOT EXISTS passengers ("
        "  PassengerID VARCHAR(20) PRIMARY KEY, "       # from 'Passenger ID'
        "  FirstName VARCHAR(50), "                      # from 'First Name'
        "  LastName VARCHAR(50), "                       # from 'Last Name'
        "  Gender VARCHAR(10), "
        "  Age INT, "
        "  Nationality VARCHAR(50)"
        ") ENGINE=InnoDB"
    )

    # ----------------------------------------------
    # Airports Table: holds airport details.
    # ----------------------------------------------
    TABLES['airports'] = (
        "CREATE TABLE IF NOT EXISTS airports ("
        "  AirportName VARCHAR(100) PRIMARY KEY, "       # from 'Airport Name'
        "  AirportCountryCode VARCHAR(20), "             # from 'Airport Country Code'
        "  CountryName VARCHAR(50), "                    # from 'Country Name'
        "  AirportContinent VARCHAR(50), "               # from 'Airport Continent'
        "  Continents VARCHAR(50) "                      # from 'Continents'
        ") ENGINE=InnoDB"
    )

    # ----------------------------------------------
    # Flights Table: holds flight records.
    # ----------------------------------------------
    TABLES['flights'] = (
        "CREATE TABLE IF NOT EXISTS flights ("
        "  FlightID INT PRIMARY KEY AUTO_INCREMENT, "  # Auto-generated flight identifier
        "  PassengerID VARCHAR(20), "                   # FK to passengers
        "  DepartureAirport VARCHAR(100), "             # FK to airports (using AirportName)
        "  DepartureDate DATE, "                        
        "  ArrivalAirport VARCHAR(100), "               # FK to airports (using AirportName)
        "  PilotName VARCHAR(50), "
        "  FlightStatus VARCHAR(20), "
        "  FOREIGN KEY (PassengerID) REFERENCES passengers(PassengerID), "
        "  FOREIGN KEY (DepartureAirport) REFERENCES airports(AirportName), "
        "  FOREIGN KEY (ArrivalAirport) REFERENCES airports(AirportName) "
        ") ENGINE=InnoDB"
    )

    # Create each table and report status
    for table_name, ddl in TABLES.items():
        try:
            print(f"Creating table `{table_name}`: ", end="")
            cursor.execute(ddl)
            print("OK")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(f"Error creating table {table_name}: {err.msg}")

def main():
    # Specify your database name; for example, 'airline_db'
    db_name = 'airline_db'

    # Update your MySQL connection credentials accordingly.
    config = {
        'user': 'root',      # Replace with your MySQL username
        'password': 'Helloworld@2025',  # Replace with your MySQL password
        'host': 'localhost',          # Replace if your MySQL server is hosted elsewhere
        'raise_on_warnings': True
    }

    try:
        # Connect to the MySQL server.
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Create the database if it doesn't exist.
        create_database(cursor, db_name)
        cursor.execute(f"USE {db_name}")

        # Create the tables for the airline schema.
        create_tables(cursor)

        # Commit the changes and close the connection.
        cnx.commit()
        cursor.close()
        cnx.close()
        print("All tables created successfully in the database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
