import mysql.connector
import csv

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'employee_db'
}

def insert_employee_personal(cursor, filepath):
    rows = []
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            values = (
                row['EmpID'], row['FirstName'], row['LastName'], row['DOB'],
                row['GenderCode'], row['RaceDesc'], row['MaritalDesc'],
                row['State'], row['LocationCode'], row['ADEmail']
            )
            rows.append(values)
    cursor.executemany("""
        INSERT INTO employee_personal (
            EmpID, FirstName, LastName, DOB, GenderCode,
            RaceDesc, MaritalDesc, State, LocationCode, ADEmail
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, rows)
    print(f"Inserted {len(rows)} rows into employee_personal.")

def insert_employee_employment(cursor, filepath):
    rows = []
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            values = (
                row['EmpID'], row['StartDate'], row['ExitDate'], row['Title'],
                row['Supervisor'], row['BusinessUnit'], row['EmployeeStatus'],
                row['EmployeeType'], row['PayZone'], row['EmployeeClassificationType'],
                row['DepartmentType'], row['Division'], row['JobFunctionDescription'],
                row['Performance Score'], row['Current Employee Rating']
            )
            rows.append(values)
    cursor.executemany("""
        INSERT INTO employee_employment (
            EmpID, StartDate, ExitDate, Title, Supervisor,
            BusinessUnit, EmployeeStatus, EmployeeType, PayZone,
            EmployeeClassificationType, DepartmentType, Division,
            JobFunctionDescription, PerformanceScore, CurrentEmployeeRating
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, rows)
    print(f"Inserted {len(rows)} rows into employee_employment.")

def insert_employee_termination(cursor, filepath):
    rows = []
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            values = (
                row['EmpID'], row['TerminationType'], row['TerminationDescription']
            )
            rows.append(values)
    cursor.executemany("""
        INSERT INTO employee_termination (
            EmpID, TerminationType, TerminationDescription
        ) VALUES (%s, %s, %s)
    """, rows)
    print(f"Inserted {len(rows)} rows into employee_termination.")

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
        if cursor: cursor.close()
        if cnx: cnx.close()

if __name__ == "__main__":
    main()
