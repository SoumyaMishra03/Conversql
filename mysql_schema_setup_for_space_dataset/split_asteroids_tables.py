import mysql.connector

def create_database(cursor, db_name):
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    TABLES = {}

    TABLES['neo_reference'] = (
        "CREATE TABLE IF NOT EXISTS neo_reference ("
        "  `Neo Reference ID` VARCHAR(20),"
        "  `Name` VARCHAR(100),"
        "  `Absolute Magnitude` FLOAT,"
        "  `Est Dia in KM(min)` FLOAT,"
        "  `Est Dia in KM(max)` FLOAT,"
        "  `Est Dia in M(min)` FLOAT,"
        "  `Est Dia in M(max)` FLOAT,"
        "  `Est Dia in Miles(min)` FLOAT,"
        "  `Est Dia in Miles(max)` FLOAT,"
        "  `Est Dia in Feet(min)` FLOAT,"
        "  `Est Dia in Feet(max)` FLOAT"
        ")"
    )

    TABLES['close_approach'] = (
        "CREATE TABLE IF NOT EXISTS close_approach ("
        "  `Neo Reference ID` VARCHAR(20),"
        "  `Close Approach Date` DATE,"
        "  `Epoch Date Close Approach` DATE,"
        "  `Relative Velocity km per sec` FLOAT,"
        "  `Relative Velocity km per hr` FLOAT,"
        "  `Miles per hour` FLOAT,"
        "  `Miss Dist.(Astronomical)` FLOAT,"
        "  `Miss Dist.(lunar)` FLOAT,"
        "  `Miss Dist.(kilometers)` FLOAT,"
        "  `Miss Dist.(miles)` FLOAT"
        ")"
    )

    TABLES['orbit_data'] = (
        "CREATE TABLE IF NOT EXISTS orbit_data ("
        "  `Neo Reference ID` VARCHAR(20),"
        "  `Orbiting Body` VARCHAR(50),"
        "  `Orbit ID` VARCHAR(20),"
        "  `Orbit Determination Date` DATE,"
        "  `Orbit Uncertainity` INT,"
        "  `Minimum Orbit Intersection` FLOAT,"
        "  `Jupiter Tisserand Invariant` FLOAT,"
        "  `Epoch Osculation` DATE,"
        "  `Eccentricity` FLOAT,"
        "  `Semi Major Axis` FLOAT,"
        "  `Inclination` FLOAT,"
        "  `Asc Node Longitude` FLOAT,"
        "  `Orbital Period` FLOAT,"
        "  `Perihelion Distance` FLOAT,"
        "  `Perihelion Arg` FLOAT,"
        "  `Aphelion Dist` FLOAT,"
        "  `Perihelion Time` VARCHAR(50),"
        "  `Mean Anomaly` FLOAT,"
        "  `Mean Motion` FLOAT,"
        "  `Equinox` VARCHAR(20),"
        "  `Hazardous` VARCHAR(10)"
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
    db_name = 'asteroids'
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
