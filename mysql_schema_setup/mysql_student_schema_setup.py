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
    Creates the necessary tables for the student dataset schema:
    student_personal, student_academic, and student_courses.
    """
    TABLES = {}

    # ----------------------------------------------
    # student_personal: Basic personal details.
    # ----------------------------------------------
    TABLES['student_personal'] = (
        "CREATE TABLE IF NOT EXISTS student_personal ("
        "  StudentID INT PRIMARY KEY AUTO_INCREMENT, "
        "  Student_Names VARCHAR(100) NOT NULL, "
        "  Phone_No VARCHAR(20), "
        "  Gender VARCHAR(10)"
        ") ENGINE=InnoDB"
    )

    # ----------------------------------------------
    # student_academic: Academic information for each student.
    # ----------------------------------------------
    TABLES['student_academic'] = (
        "CREATE TABLE IF NOT EXISTS student_academic ("
        "  AcademicID INT PRIMARY KEY AUTO_INCREMENT, "
        "  StudentID INT NOT NULL, "
        "  Study_Hours FLOAT, "
        "  Part_Time_Job VARCHAR(10), "
        "  Math FLOAT, "
        "  Physics FLOAT, "
        "  Chemistry FLOAT, "
        "  Grade VARCHAR(10), "
        "  Comment VARCHAR(255), "
        "  FOREIGN KEY (StudentID) REFERENCES student_personal(StudentID)"
        ") ENGINE=InnoDB"
    )

    # ----------------------------------------------
    # student_courses: Course details for each student.
    # ----------------------------------------------
    TABLES['student_courses'] = (
        "CREATE TABLE IF NOT EXISTS student_courses ("
        "  CourseID INT PRIMARY KEY AUTO_INCREMENT, "
        "  StudentID INT NOT NULL, "
        "  Course_Recommendation VARCHAR(255), "
        "  CourseCode VARCHAR(50), "
        "  ListofCourses VARCHAR(255), "
        "  RatingOfCourses FLOAT, "
        "  FOREIGN KEY (StudentID) REFERENCES student_personal(StudentID)"
        ") ENGINE=InnoDB"
    )

    # Create each table and report status
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
    # Specify your database name; for example, 'student_db'
    db_name = 'student_db'

    # Update the following MySQL connection credentials with your actual MySQL user info.
    config = {
        'user': 'root',      # Replace with your MySQL username
        'password': 'Helloworld@2025',  # Replace with your MySQL password
        'host': 'localhost',          # Replace if your MySQL server is hosted elsewhere
        'raise_on_warnings': True
    }

    try:
        # Connect to the MySQL server.
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Create the database if it doesn't exist and switch to it.
        create_database(cursor, db_name)
        cursor.execute(f"USE {db_name}")

        # Create the tables for the student dataset.
        create_tables(cursor)

        # Commit the changes and close the connection.
        cnx.commit()
        cursor.close()
        cnx.close()
        print("All tables created successfully in the database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
