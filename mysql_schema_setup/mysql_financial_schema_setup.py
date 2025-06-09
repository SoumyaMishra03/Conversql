import mysql.connector
from mysql.connector import errorcode

def create_database(cursor, db_name):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created or already exists.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    # Define table creation statements for the financial transaction schema.
    TABLES = {}

    # ----------------------------------------------
    # Customers Table: contains customer-specific details.
    # ----------------------------------------------
    TABLES['customers'] = (
        "CREATE TABLE IF NOT EXISTS customers ("
        "  CustomerID VARCHAR(20) PRIMARY KEY, "
        "  CustomerDOB DATE, "
        "  CustGender VARCHAR(10), "
        "  CustLocation VARCHAR(50), "
        "  CustAccountBalance FLOAT"
        ") ENGINE=InnoDB"
    )
    
    # ----------------------------------------------
    # Transactions Table: contains each transaction record.
    # ----------------------------------------------
    TABLES['transactions'] = (
        "CREATE TABLE IF NOT EXISTS transactions ("
        "  TransactionID VARCHAR(20) PRIMARY KEY, "
        "  CustomerID VARCHAR(20), "
        "  TransactionDate DATE, "
        "  TransactionTime TIME, "
        "  TransactionAmount_INR FLOAT, "
        "  FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID)"
        ") ENGINE=InnoDB"
    )

    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print(f"Creating table `{table_name}`: ", end="")
            cursor.execute(table_description)
            print("OK")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)

def main():
    # Specify your database name.
    db_name = 'financial_transaction'
    
    # Provide your MySQL connection configuration.
    config = {
    'user': 'root',
    'password': 'Helloworld@2025',
    'host': 'localhost',
    'auth_plugin':'mysql_native_password',  # Force mysql_native_password if supported
    'raise_on_warnings': True
}


    try:
        # Connect to MySQL server.
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Create the database if it doesn't exist.
        create_database(cursor, db_name)
        cursor.execute(f"USE {db_name}")
        
        # Create the tables.
        create_tables(cursor)
        
        # Commit changes to the database.
        cnx.commit()
        cursor.close()
        cnx.close()
        print("All tables created successfully in the database.")
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
