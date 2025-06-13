import mysql.connector
from mysql.connector import errorcode

def create_database(cursor, db_name):
    try:
        cursor.execute(f"DROP DATABASE if exists {db_name}")
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    TABLES = {}

    TABLES['student_personal'] = (
        "CREATE TABLE IF NOT EXISTS student_personal ("
        "  Roll_No INT, "
        "  Student_Names VARCHAR(100) NOT NULL, "
        "  Phone_No VARCHAR(20), "
        "  Gender VARCHAR(10)"
        ")"
    )

    TABLES['student_academic'] = (
        "CREATE TABLE IF NOT EXISTS student_academic ("
        "  Roll_No INT, "
        "  Student_Names VARCHAR(100), "
        "  Study_Hours FLOAT, "
        "  Part_Time_Job VARCHAR(10), "
        "  Math FLOAT, "
        "  Physics FLOAT, "
        "  Chemistry FLOAT, "
        "  Grade VARCHAR(10), "
        "  Comment VARCHAR(255)"
        ")"
    )

    TABLES['student_courses'] = (
        "CREATE TABLE IF NOT EXISTS student_courses ("
        "  Roll_No INT, "
        "  Student_Names VARCHAR(100), "
        "  Course_Recommendation VARCHAR(255), "
        "  CourseCode VARCHAR(50), "
        "  ListofCourses VARCHAR(255), "
        "  RatingOfCourses FLOAT"
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
    db_name = 'student_db'
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
