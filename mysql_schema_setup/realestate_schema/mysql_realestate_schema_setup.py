import mysql.connector
from mysql.connector import errorcode

def create_database(cursor, db_name):
    try:
        cursor.execute(f"drop database {db_name}")
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
    TABLES['properties'] = (
        "CREATE TABLE IF NOT EXISTS properties ("
        "  Name VARCHAR(255), "  
        "  PropertyTitle VARCHAR(255), "
        "  Price varchar(40), "
        "  Description TEXT"
        ") ENGINE=InnoDB"
    )


    TABLES['locations'] = (
        "CREATE TABLE IF NOT EXISTS locations ("
        "  Name VARCHAR(255) , " 
        "  Location VARCHAR(255), "
        "  Total_Area DECIMAL(10,2), "
        "  Price_per_SQFT DECIMAL(10,2) "
        ") ENGINE=InnoDB"
    )


    TABLES['features'] = (
        "CREATE TABLE IF NOT EXISTS features ("
        "  Name VARCHAR(255) , " 
        "  Baths INT, "
        "  Balcony VARCHAR(10)"
        ") ENGINE=InnoDB"
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
    db_name = 'real_estate_db'

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
