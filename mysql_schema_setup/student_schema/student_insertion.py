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
        for row in reader:
            query = """
                INSERT INTO student_personal (Student_Names, Phone_No, Gender)
                VALUES (%s, %s, %s)
            """
            values = (row['Student_Names'], row['Phone_No.'], row['Gender'])
            try:
                cursor.execute(query, values)
                print(f"Inserted personal: {values}")
            except mysql.connector.Error as e:
                print(f"Error inserting student_personal {row['Student_Names']}: {e}")

def insert_student_academic(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = """
                INSERT INTO student_academic (
                    Student_Names, Study_Hours, Part_Time_Job, 
                    Math, Physics, Chemistry, Grade, Comment
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                row['Student_Names'], 
                float(row['Study_Hours']) if row['Study_Hours'] else None,
                row['Part_Time_Job'],
                float(row['Math']) if row['Math'] else None,
                float(row['Physics']) if row['Physics'] else None,
                float(row['Chemistry']) if row['Chemistry'] else None,
                row['Grade'], row['Comment']
            )
            try:
                cursor.execute(query, values)
                print(f"Inserted academic: {values}")
            except mysql.connector.Error as e:
                print(f"Error inserting student_academic {row['Student_Names']}: {e}")

def insert_student_courses(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = """
                INSERT INTO student_courses (
                    Student_Names, Course_Recommendation, 
                    CourseCode, ListofCourses, RatingOfCourses
                ) VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                row['Student_Names'],
                row['Course_Recommendation'],
                row['CourseCode'],
                row['ListofCourses'],
                float(row['RatingOfCourses']) if row['RatingOfCourses'] else None
            )
            try:
                cursor.execute(query, values)
                print(f"Inserted course: {values}")
            except mysql.connector.Error as e:
                print(f"Error inserting student_courses {row['Student_Names']}: {e}")

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
        print(f"Database error: {e}")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
