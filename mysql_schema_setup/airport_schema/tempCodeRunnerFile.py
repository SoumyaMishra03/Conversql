import mysql.connector

def create_database(cursor, db_name):
    try:
        cursor.execute(f"drop database {db_name}")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created or already exists.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    TABLES = {}

    # Passengers Table
    TABLES['passengers'] = (
        "CREATE TABLE IF NOT EXISTS passengers ("
        "  PassengerID VARCHAR(10) PRIMARY KEY, "
        "  FirstName VARCHAR(50), "
        "  LastName VARCHAR(50), "
        "  Gender VARCHAR(10), "
        "  Age INT, "
        "  Nationality VARCHAR(50)"
        ") ENGINE=InnoDB"
    )

    # Airports Table
    TABLES['airports'] = (
        "CREATE TABLE IF NOT EXISTS airports ("           
        "  AirportName VARCHAR(100) primary key, "
        "  CountryCode VARCHAR(10), "
        "  CountryName VARCHAR(50), "
        "  Continent VARCHAR(50)"
        ") ENGINE=InnoDB"
    )

    # Flights Table
    TABLES['flights'] = (
        "CREATE TABLE IF NOT EXISTS flights ("
        "  FlightID INT AUTO_INCREMENT PRIMARY KEY, "
        "  PassengerID Varchar(10), "
        "  DepartureTime DATETIME, "
        "  PilotName VARCHAR(50), "
        "  FlightStatus VARCHAR(20), "
        "  FOREIGN KEY (PassengerID) REFERENCES passengers(PassengerID), "
        "  INDEX idx_passenger (PassengerID), "
        ") ENGINE=InnoDB"
    )

    for table_name, ddl in TABLES.items():
        try:
            print(f"Creating table `{table_name}`: ", end="")
            cursor.execute(ddl)
            print("OK")
        except mysql.connector.Error as err:
            print(f"Error creating table `{table_name}`: {err.msg}")

def main():
    db_name = 'airline_db'
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'localhost',
        'raise_on_warnings': True
    }

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        create_database(cursor, db_name)
        cursor.execute(f"USE {db_name}")
        create_tables(cursor)
        cnx.commit()
        cursor.close()
        cnx.close()
        print("All tables created successfully in the database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
