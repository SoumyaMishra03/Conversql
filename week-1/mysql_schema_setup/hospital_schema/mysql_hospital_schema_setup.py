import mysql.connector
from mysql.connector import errorcode

def create_database(cursor, db_name):
    try:
        cursor.execute(f"drop database {db_name}")
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created or already exists.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    TABLES = {}

    TABLES['patients'] = (
        "CREATE TABLE IF NOT EXISTS patients ("
        "  Patient_ID VARCHAR(20), "
        "  Age INT, "
        "  Gender VARCHAR(10)"
        ") "
    )

    TABLES['hospital_encounters'] = (
        "CREATE TABLE IF NOT EXISTS hospital_encounters ("
        "  Patient_ID VARCHAR(20), "
        "  `Condition` VARCHAR(100), "
        "  `Procedure` VARCHAR(100), "
        "  Cost FLOAT, "
        "  Length_of_Stay INT, "
        "  Readmission VARCHAR(10), "
        "  Outcome VARCHAR(50), "
        "  Satisfaction VARCHAR(50)"
        ") "
    )

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
    db_name = 'hospital_db'
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
