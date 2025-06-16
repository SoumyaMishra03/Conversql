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

    TABLES['rocket_general_info'] = (
        "CREATE TABLE IF NOT EXISTS rocket_general_info ("
        "  Name VARCHAR(100),"
        "  Cmp VARCHAR(50),"
        "  Wiki VARCHAR(100),"
        "  Status VARCHAR(20)"
        ")"
    )

    TABLES['rocket_technical_specs'] = (
        "CREATE TABLE IF NOT EXISTS rocket_technical_specs ("
        "  Name VARCHAR(100),"
        "  Liftoff_Thrust FLOAT,"
        "  Payload_LEO FLOAT,"
        "  Stages INT,"
        "  Strap_ons INT,"
        "  Rocket_Height_m FLOAT,"
        "  Price_MUSD FLOAT,"
        "  Payload_GTO FLOAT,"
        "  Fairing_Diameter_m FLOAT,"
        "  Fairing_Height_m FLOAT"
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
    db_name = 'rockets_db'
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