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
    Creates the necessary tables for the hospital data schema:
    patients and hospital_encounters.
    """
    TABLES = {}

    # ----------------------------------------------
    # Patients Table: holds patient demographic details.
    # ----------------------------------------------
    TABLES['patients'] = (
        "CREATE TABLE IF NOT EXISTS patients ("
        "  Patient_ID VARCHAR(20) PRIMARY KEY, "
        "  Age INT, "
        "  Gender VARCHAR(10)"
        ") ENGINE=InnoDB"
    )

    # ----------------------------------------------
    # Hospital Encounters Table: holds details for each encounter.
    # ----------------------------------------------
    TABLES['hospital_encounters'] = (
        "CREATE TABLE IF NOT EXISTS hospital_encounters ("
        "  Encounter_ID INT PRIMARY KEY AUTO_INCREMENT, "
        "  Patient_ID VARCHAR(20), "
        "  Condition VARCHAR(100), "
        "  Procedure VARCHAR(100), "
        "  Cost FLOAT, "
        "  Length_of_Stay INT, "
        "  Readmission VARCHAR(10), "  # Example: 'Yes' or 'No'
        "  Outcome VARCHAR(50), "
        "  Satisfaction VARCHAR(50), "
        "  FOREIGN KEY (Patient_ID) REFERENCES patients(Patient_ID)"
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
    # Specify your database name; for example, 'hospital_db'
    db_name = 'hospital_db'

    # Update your MySQL connection credentials accordingly.
    config = {
        'user': 'root',      # Replace with your MySQL username
        'password': 'Helloworld@2025',  # Replace with your MySQL password
        'host': 'localhost',          # Replace if your MySQL server is running elsewhere
        'raise_on_warnings': True
    }

    try:
        # Connect to the MySQL server.
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Create the database if it doesn't exist.
        create_database(cursor, db_name)
        cursor.execute(f"USE {db_name}")

        # Create the tables for the hospital data schema.
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
