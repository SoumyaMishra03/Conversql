import mysql.connector

def create_database(cursor, db_name):
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created (or already exists).")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    TABLES = {}

    TABLES['basic_info'] = (
        "CREATE TABLE IF NOT EXISTS basic_info ("
        "  `Satellite ID(Fake)` VARCHAR(20),"
        "  `Name of Satellite, Alternate Names` VARCHAR(150),"
        "  `Current Official Name of Satellite` VARCHAR(150),"
        "  `Country/Org of UN Registry` VARCHAR(100),"
        "  `Country of Operator/Owner` VARCHAR(100),"
        "  `Operator/Owner` VARCHAR(100),"
        "  `Users` VARCHAR(100),"
        "  `Purpose` VARCHAR(100),"
        "  `Detailed Purpose` VARCHAR(255)"
        ")"
    )

    TABLES['orbital_info'] = (
        "CREATE TABLE IF NOT EXISTS orbital_info ("
        "  `Satellite ID(Fake)` VARCHAR(20),"
        "  `Class of Orbit` VARCHAR(50),"
        "  `Type of Orbit` VARCHAR(50),"
        "  `Longitude of GEO (degrees)` FLOAT,"
        "  `Perigee (km)` FLOAT,"
        "  `Apogee (km)` FLOAT,"
        "  `Eccentricity` FLOAT,"
        "  `Inclination (degrees)` FLOAT,"
        "  `Period (minutes)` FLOAT"
        ")"
    )

    TABLES['launch_info'] = (
        "CREATE TABLE IF NOT EXISTS launch_info ("
        "  `Satellite ID(Fake)` VARCHAR(20),"
        "  `Launch Mass (kg.)` FLOAT,"
        "  `Dry Mass (kg.)` FLOAT,"
        "  `Power (watts)` FLOAT,"
        "  `Date of Launch` DATE,"
        "  `Expected Lifetime (yrs.)` INT,"
        "  `Contractor` VARCHAR(100),"
        "  `Country of Contractor` VARCHAR(100),"
        "  `Launch Site` VARCHAR(100),"
        "  `Launch Vehicle` VARCHAR(100),"
        "  `COSPAR Number` VARCHAR(50),"
        "  `NORAD Number` VARCHAR(50),"
        "  `Comments` VARCHAR(500)"
        ")"
    )

    for table_name, ddl in TABLES.items():
        try:
            print(f"Creating table {table_name}: ", end="")
            cursor.execute(ddl)
            print("OK")
        except mysql.connector.Error as err:
            print(f"Error creating table {table_name}: {err.msg}")

def main():
    db_name = 'isro_satellites_db'
    config = {
        'user': 'root',
        'password': 'Helloworld@2025',
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
