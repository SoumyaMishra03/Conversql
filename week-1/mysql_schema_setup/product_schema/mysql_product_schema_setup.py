import mysql.connector
from mysql.connector import errorcode

def create_database(cursor, db_name):
    try:
        cursor.execute(f"drop database {db_name}")
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    TABLES = {}
    TABLES['products'] = (
        "CREATE TABLE IF NOT EXISTS products ("
        "  UniqId VARCHAR(255), "
        "  Category VARCHAR(255), "
        "  ProductTitle VARCHAR(500), "
        "  ProductDescription TEXT, "
        "  Brand VARCHAR(255), "
        "  PackSizeOrQuantity VARCHAR(500), "
        "  ImageUrls TEXT"
        ")"
    )

    TABLES['pricing'] = (
        "CREATE TABLE IF NOT EXISTS pricing ("
        "  UniqId VARCHAR(255), "
        "  Mrp varchar(100), "
        "  Price varchar(100), "
        "  Offers TEXT, "
        "  ComboOffers TEXT"
        ")"
    )

    TABLES['availability'] = (
        "CREATE TABLE IF NOT EXISTS availability ("
        "  UniqId VARCHAR(255), "
        "  SiteName VARCHAR(255), "
        "  StockAvailibility VARCHAR(50), "
        "  ProductAsin VARCHAR(255)"
        ")"
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
    db_name = 'products_db'
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
