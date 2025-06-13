import mysql.connector
from mysql.connector import errorcode

def create_database(cursor, db_name):
    try:
        cursor.execute(f"drop database if exists {db_name}")
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created .")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    TABLES = {}

    TABLES['customers'] = (
        "CREATE TABLE IF NOT EXISTS customers ("
        "  CustomerID VARCHAR(20) , "
        "  CustomerDOB varchar(30), "
        "  CustGender VARCHAR(10), "
        "  CustLocation VARCHAR(50), "
        "  CustAccountBalance FLOAT"
        ") "
    )
    

    TABLES['transactions'] = (
        "CREATE TABLE IF NOT EXISTS transactions ("
        "  TransactionID VARCHAR(20) , "
        "  CustomerID VARCHAR(20), "
        "  TransactionDate varchar(30), "
        "  TransactionTime varchar(30), "
        "  TransactionAmount_INR FLOAT"
        ")"
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
    db_name = 'financial_transaction'

    config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
     #'auth_plugin':'mysql_native_password',  
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
