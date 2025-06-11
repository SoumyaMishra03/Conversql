import mysql.connector
import csv

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'student_db'
}

def insert_student_personal(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = [
            (row['Student_Names'], row['Phone_No.'], row['Gender'])
            for row in reader
        ]

    query = """
        INSERT INTO student_personal (Student_Names, Phone_No, Gender)
        VALUES (%s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} rows into student_personal.")
    except mysql.connector.Error as e:
        print(f"Error inserting into student_personal: {e}")

def insert_student_academic(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        for row in reader:
            try:
                data.append((
                    row['Student_Names'],
                    float(row['Study_Hours']) if row['Study_Hours'] else None,
                    row['Part_Time_Job'],
                    float(row['Math']) if row['Math'] else None,
                    float(row['Physics']) if row['Physics'] else None,
                    float(row['Chemistry']) if row['Chemistry'] else None,
                    row['Grade'],
                    row['Comment']
                ))
            except ValueError as e:
                print(f"Skipped row due to invalid number format: {row} | Error: {e}")

    query = """
        INSERT INTO student_academic (
            Student_Names, Study_Hours, Part_Time_Job, 
            Math, Physics, Chemistry, Grade, Comment
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} rows into student_academic.")
    except mysql.connector.Error as e:
        print(f"Error inserting into student_academic: {e}")

def insert_student_courses(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        for row in reader:
            try:
                data.append((
                    row['Student_Names'],
                    row['Course_Recommendation'],
                    row['CourseCode'],
                    row['ListofCourses'],
                    float(row['RatingOfCourses']) if row['RatingOfCourses'] else None
                ))
            except ValueError as e:
                print(f"Skipped row due to invalid number format: {row} | Error: {e}")

    query = """
        INSERT INTO student_courses (
            Student_Names, Course_Recommendation, 
            CourseCode, ListofCourses, RatingOfCourses
        ) VALUES (%s, %s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} rows into student_courses.")
    except mysql.connector.Error as e:
        print(f"Error inserting into student_courses: {e}")

def main():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        insert_student_personal(cursor, 'student_personal.csv')
        insert_student_academic(cursor, 'student_academic.csv')
        insert_student_courses(cursor, 'student_courses.csv')

        conn.commit()
        print("All data inserted successfully.")

    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    main()
