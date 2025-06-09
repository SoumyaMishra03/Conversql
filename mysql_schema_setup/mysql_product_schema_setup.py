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
    Creates the necessary tables for the products dataset schema:
    products, pricing, and availability.
    """
    TABLES = {}

    # -----------------------------
    # 1. products Table
    # -----------------------------
    TABLES['products'] = (
        "CREATE TABLE IF NOT EXISTS products ("
        "  UniqId VARCHAR(255) PRIMARY KEY, "
        "  Category VARCHAR(255), "
        "  ProductTitle VARCHAR(255), "
        "  ProductDescription TEXT, "
        "  Brand VARCHAR(255), "
        "  PackSizeOrQuantity VARCHAR(100), "
        "  ImageUrls TEXT"
        ") ENGINE=InnoDB"
    )

    # -----------------------------
    # 2. pricing Table
    # -----------------------------
    TABLES['pricing'] = (
        "CREATE TABLE IF NOT EXISTS pricing ("
        "  UniqId VARCHAR(255) PRIMARY KEY, "
        "  Mrp DECIMAL(10,2), "
        "  Price DECIMAL(10,2), "
        "  Offers TEXT, "
        "  ComboOffers TEXT, "
        "  FOREIGN KEY (UniqId) REFERENCES products(UniqId) "
        "    ON DELETE CASCADE ON UPDATE CASCADE"
        ") ENGINE=InnoDB"
    )

    # -----------------------------
    # 3. availability Table
    # -----------------------------
    TABLES['availability'] = (
        "CREATE TABLE IF NOT EXISTS availability ("
        "  UniqId VARCHAR(255) PRIMARY KEY, "
        "  SiteName VARCHAR(255), "
        "  StockAvailibility VARCHAR(50), "
        "  ProductAsin VARCHAR(255), "
        "  FOREIGN KEY (UniqId) REFERENCES products(UniqId) "
        "    ON DELETE CASCADE ON UPDATE CASCADE"
        ") ENGINE=InnoDB"
    )

    # Create each table
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
    # Specify your database name; for example, 'products_db'
    db_name = 'products_db'
    
    # Update your MySQL connection credentials accordingly.
    config = {
        'user': 'root',      # Replace with your MySQL username
        'password': 'Helloworld@2025',  # Replace with your MySQL password
        'host': 'localhost',          # Change if your MySQL server is on another host
        'raise_on_warnings': True
    }
    
    try:
        # Connect to the MySQL server.
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        
        # Create the database if it doesn't exist and select it.
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
