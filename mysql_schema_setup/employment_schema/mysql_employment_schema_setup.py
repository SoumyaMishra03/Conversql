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
    TABLES = {}
    TABLES['employee_personal'] = (
        "CREATE TABLE IF NOT EXISTS employee_personal ("
        "  EmpID VARCHAR(20) , "
        "  FirstName VARCHAR(50), "
        "  LastName VARCHAR(50), "
        "  DOB varchar(30), "
        "  GenderCode VARCHAR(10), "
        "  RaceDesc VARCHAR(50), "
        "  MaritalDesc VARCHAR(50), "
        "  State VARCHAR(50), "
        "  LocationCode VARCHAR(50), "
        "  ADEmail VARCHAR(100) "
        ") ENGINE=InnoDB"
    )
    TABLES['employee_employment'] = (
        "CREATE TABLE IF NOT EXISTS employee_employment ("
        "  EmpID VARCHAR(20), "
        "  StartDate varchar(30), "
        "  ExitDate varchar(30), "
        "  Title VARCHAR(100), "
        "  Supervisor VARCHAR(100), "
        "  BusinessUnit VARCHAR(50), "
        "  EmployeeStatus VARCHAR(20), "
        "  EmployeeType VARCHAR(20), "
        "  PayZone VARCHAR(20), "
        "  EmployeeClassificationType VARCHAR(50), "
        "  DepartmentType VARCHAR(50), "
        "  Division VARCHAR(50), "
        "  JobFunctionDescription VARCHAR(100), "
        "  PerformanceScore FLOAT, "
        "  CurrentEmployeeRating FLOAT "
        ") ENGINE=InnoDB"
    )

    TABLES['employee_termination'] = (
        "CREATE TABLE IF NOT EXISTS employee_termination ("
        "  EmpID VARCHAR(20) , "
        "  TerminationType VARCHAR(50), "
        "  TerminationDescription VARCHAR(255) "
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
    db_name = 'employee_db'
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
