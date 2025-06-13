import mysql.connector
import csv

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'student_db'
}

def is_ascii(s):
    try:
        s.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

def insert_student_personal(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        roll_no = 1
        for row in reader:
            name = row['Student_Names']
            if not is_ascii(name):
                print(f"Skipped non-ASCII name: {name}")
                continue
            data.append((roll_no, name, row['Phone_No.'], row['Gender']))
            roll_no += 1

    query = """
        INSERT INTO student_personal (Roll_No, Student_Names, Phone_No, Gender)
        VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} unique rows into student_personal.")
    except mysql.connector.Error as e:
        print(f"Error inserting into student_personal: {e}")

def insert_student_academic(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        roll_no = 1
        for row in reader:
            name = row['Student_Names']
            if not is_ascii(name):
                print(f"Skipped non-ASCII name: {name}")
                continue
            try:
                data.append((
                    roll_no,
                    name,
                    float(row['Study_Hours']) if row['Study_Hours'] else None,
                    row['Part_Time_Job'],
                    float(row['Math']) if row['Math'] else None,
                    float(row['Physics']) if row['Physics'] else None,
                    float(row['Chemistry']) if row['Chemistry'] else None,
                    row['Grade'],
                    row['Comment']
                ))
                roll_no += 1
            except ValueError as e:
                print(f"Skipped row due to invalid number format: {row} | Error: {e}")

    query = """
        INSERT INTO student_academic (
            Roll_No, Student_Names, Study_Hours, Part_Time_Job, 
            Math, Physics, Chemistry, Grade, Comment
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} unique rows into student_academic.")
    except mysql.connector.Error as e:
        print(f"Error inserting into student_academic: {e}")

def insert_student_courses(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        roll_no = 1
        for row in reader:
            name = row['Student_Names']
            if not is_ascii(name):
                print(f"Skipped non-ASCII name: {name}")
                continue
            try:
                data.append((
                    roll_no,
                    name,
                    row['Course_Recommendation'],
                    row['CourseCode'],
                    row['ListofCourses'],
                    float(row['RatingOfCourses']) if row['RatingOfCourses'] else None
                ))
                roll_no += 1
            except ValueError as e:
                print(f"Skipped row due to invalid number format: {row} | Error: {e}")

    query = """
        INSERT INTO student_courses (
            Roll_No, Student_Names, Course_Recommendation, 
            CourseCode, ListofCourses, RatingOfCourses
        ) VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} unique rows into student_courses.")
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
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
