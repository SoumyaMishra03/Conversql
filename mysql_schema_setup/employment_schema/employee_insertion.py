import mysql.connector
import csv
from datetime import datetime

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'employee_db'
}

def insert_employee_personal(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = """
                INSERT INTO employee_personal (
                    EmpID, FirstName, LastName, DOB, GenderCode,
                    RaceDesc, MaritalDesc, State, LocationCode, ADEmail
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                row['EmpID'], row['FirstName'], row['LastName'],
                row['DOB'], row['GenderCode'], row['RaceDesc'],
                row['MaritalDesc'], row['State'], row['LocationCode'],
                row['ADEmail']
            )
            try:
                cursor.execute(query, values)
                print(f"Inserted employee_personal: {values}")
            except mysql.connector.Error as e:
                print(f"Error inserting into employee_personal: {e}")

def insert_employee_employment(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = """
                INSERT INTO employee_employment (
                    EmpID, StartDate, ExitDate, Title, Supervisor,
                    BusinessUnit, EmployeeStatus, EmployeeType, PayZone,
                    EmployeeClassificationType, DepartmentType, Division,
                    JobFunctionDescription, PerformanceScore, CurrentEmployeeRating
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                row['EmpID'],
                parse_date(row['StartDate']),
                parse_date(row['ExitDate']),
                row['Title'], row['Supervisor'], row['BusinessUnit'],
                row['EmployeeStatus'], row['EmployeeType'], row['PayZone'],
                row['EmployeeClassificationType'], row['DepartmentType'],
                row['Division'], row['JobFunctionDescription'],
                row['Performance Score'],
                row['Current Employee Rating']
            )
            try:
                cursor.execute(query, values)
                print(f"Inserted employee_employment: {values}")
            except mysql.connector.Error as e:
                print(f"Error inserting into employee_employment: {e}")

def insert_employee_termination(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = """
                INSERT INTO employee_termination (
                    EmpID, TerminationType, TerminationDescription
                ) VALUES (%s, %s, %s)
            """
            values = (
                row['EmpID'],
                row['TerminationType'],
                row['TerminationDescription']
            )
            try:
                cursor.execute(query, values)
                print(f"Inserted employee_termination: {values}")
            except mysql.connector.Error as e:
                print(f"Error inserting into employee_termination: {e}")

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        print(f"Invalid date format: {date_str}")
        return None

def main():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        insert_employee_personal(cursor, 'employee_personal.csv')
        insert_employee_employment(cursor, 'employee_employment.csv')
        insert_employee_termination(cursor, 'employee_termination.csv')

        cnx.commit()
        print("All data inserted successfully.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        cnx.close()

if __name__ == "__main__":
    main()
