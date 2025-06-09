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
    Creates the tables for the real estate schema:
    properties, locations, and features.
    """
    TABLES = {}

    # ------------------------------------------
    # Properties Table: Stores basic property info.
    # ------------------------------------------
    TABLES['properties'] = (
        "CREATE TABLE IF NOT EXISTS properties ("
        "  PropertyID INT AUTO_INCREMENT PRIMARY KEY, "
        "  Name VARCHAR(255) NOT NULL UNIQUE, "  # Unique property name (the linking field)
        "  PropertyTitle VARCHAR(255), "
        "  Price DECIMAL(12,2), "
        "  Description TEXT"
        ") ENGINE=InnoDB"
    )

    # ------------------------------------------
    # Locations Table: Stores location details.
    # ------------------------------------------
    TABLES['locations'] = (
        "CREATE TABLE IF NOT EXISTS locations ("
        "  LocationID INT AUTO_INCREMENT PRIMARY KEY, "
        "  Name VARCHAR(255) NOT NULL, "  # References properties(Name)
        "  Location VARCHAR(255), "
        "  Total_Area DECIMAL(10,2), "
        "  Price_per_SQFT DECIMAL(10,2), "
        "  FOREIGN KEY (Name) REFERENCES properties(Name)"
        "    ON DELETE CASCADE ON UPDATE CASCADE"
        ") ENGINE=InnoDB"
    )

    # ------------------------------------------
    # Features Table: Stores additional property features.
    # ------------------------------------------
    TABLES['features'] = (
        "CREATE TABLE IF NOT EXISTS features ("
        "  FeatureID INT AUTO_INCREMENT PRIMARY KEY, "
        "  Name VARCHAR(255) NOT NULL, "  # References properties(Name)
        "  Baths INT, "
        "  Balcony VARCHAR(10), "
        "  FOREIGN KEY (Name) REFERENCES properties(Name)"
        "    ON DELETE CASCADE ON UPDATE CASCADE"
        ") ENGINE=InnoDB"
    )

    # Create each table and report status.
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
    # Specify your target database name; for example, 'real_estate_db'
    db_name = 'real_estate_db'
    
    # Update MySQL connection credentials as needed.
    config = {
        'user': 'root',      # Replace with your MySQL username
        'password': 'Helloworld@2025',  # Replace with your MySQL password
        'host': 'localhost',          # Change if your MySQL server is hosted elsewhere
        'raise_on_warnings': True
    }
    
    try:
        # Connect to the MySQL server.
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        
        # Create database if it doesn't exist and select it.
        create_database(cursor, db_name)
        cursor.execute(f"USE {db_name}")
        
        # Create the tables.
        create_tables(cursor)
        
        # Commit changes and close connection.
        cnx.commit()
        cursor.close()
        cnx.close()
        print("All tables created successfully in the database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
