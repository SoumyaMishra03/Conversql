import mysql.connector

def create_database(cursor, db_name):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    TABLES = {}

    TABLES['organizations'] = (
        "CREATE TABLE IF NOT EXISTS organizations ("
        "  Organisation VARCHAR(100), "
        "  Location VARCHAR(100)"
        ")"
    )

    TABLES['rockets'] = (
        "CREATE TABLE IF NOT EXISTS rockets ("
        "  Organisation VARCHAR(100), "
        "  Details TEXT, "
        "  Rocket_Status VARCHAR(50), "
        "  Price VARCHAR(50)"
        ")"
    )

    TABLES['missions'] = (
        "CREATE TABLE IF NOT EXISTS missions ("
        "  Organisation VARCHAR(100), "
        "  Mission_Status VARCHAR(50)"
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
    db_name = 'space_missions_db'
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