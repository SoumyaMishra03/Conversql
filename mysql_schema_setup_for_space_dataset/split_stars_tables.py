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

    TABLES['stars'] = (
        "CREATE TABLE IF NOT EXISTS stars ("
        "  `Star_name` VARCHAR(100),"
        "  `Distance` FLOAT,"
        "  `Mass` FLOAT,"
        "  `Radius` FLOAT,"
        "  `Luminosity` FLOAT"
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
    db_name = 'stars_db'
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
        print("Stars table created successfully in the database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
