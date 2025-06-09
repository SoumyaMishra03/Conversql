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
    Creates the tables for the employee data schema:
    employee_personal, employee_employment, and employee_termination.
    """
    TABLES = {}

    # ----------------------------------------------
    # employee_personal: Basic personal details.
    # ----------------------------------------------
    TABLES['employee_personal'] = (
        "CREATE TABLE IF NOT EXISTS employee_personal ("
        "  EmpID VARCHAR(20) PRIMARY KEY, "
        "  FirstName VARCHAR(50), "
        "  LastName VARCHAR(50), "
        "  DOB DATE, "
        "  GenderCode VARCHAR(10), "
        "  RaceDesc VARCHAR(50), "
        "  MaritalDesc VARCHAR(50), "
        "  State VARCHAR(50), "
        "  LocationCode VARCHAR(50), "
        "  ADEmail VARCHAR(100) "
        ") ENGINE=InnoDB"
    )

    # ----------------------------------------------
    # employee_employment: Employment details.
    # ----------------------------------------------
    TABLES['employee_employment'] = (
        "CREATE TABLE IF NOT EXISTS employee_employment ("
        "  EmpID VARCHAR(20) NOT NULL, "
        "  StartDate DATE, "
        "  ExitDate DATE, "
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
        "  CurrentEmployeeRating FLOAT, "
        "  PRIMARY KEY (EmpID), "
        "  FOREIGN KEY (EmpID) REFERENCES employee_personal(EmpID) "
        ") ENGINE=InnoDB"
    )

    # ----------------------------------------------
    # employee_termination: Termination related details.
    # ----------------------------------------------
    TABLES['employee_termination'] = (
        "CREATE TABLE IF NOT EXISTS employee_termination ("
        "  EmpID VARCHAR(20) NOT NULL, "
        "  TerminationType VARCHAR(50), "
        "  TerminationDescription VARCHAR(255), "
        "  PRIMARY KEY (EmpID), "
        "  FOREIGN KEY (EmpID) REFERENCES employee_personal(EmpID) "
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
    # Database name - for example, 'employee_db'
    db_name = 'employee_db'

    # Update your MySQL connection credentials accordingly.
    config = {
        'user': 'root',       # Replace with your MySQL username
        'password': 'Helloworld@2025',   # Replace with your MySQL password
        'host': 'localhost',           # Replace if your MySQL server is on a different host
        'raise_on_warnings': True
    }

    try:
        # Connect to MySQL
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Create database if it doesn't exist and use it
        create_database(cursor, db_name)
        cursor.execute(f"USE {db_name}")

        # Create the tables for employee data
        create_tables(cursor)

        # Commit changes and close connection
        cnx.commit()
        cursor.close()
        cnx.close()
        print("All tables created successfully in the database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
