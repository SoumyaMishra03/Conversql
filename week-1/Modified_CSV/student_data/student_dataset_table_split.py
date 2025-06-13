import pandas as pd

def split_student_dataset(input_csv_file):
    # Load the master CSV file
    df = pd.read_csv(input_csv_file)
    
    # Print columns for debugging purposes (optional)
    print("Columns in the CSV:", df.columns.tolist())
    
    # --- 1. Create the Student Personal Information Table ---
    personal_columns = ["Student_Names", "Phone_No.", "Gender"]
    # Use drop_duplicates() to ensure one row per student if there are duplicates
    student_personal_df = df[personal_columns].drop_duplicates()
    student_personal_df.to_csv("student_personal.csv", index=False)
    
    # --- 2. Create the Student Academic Performance Table ---
    academic_columns = [
        "Student_Names", "Study_Hours", "Part_Time_Job",
        "Math", "Physics", "Chemistry", "Grade", "Comment"
    ]
    # If one student may have multiple records (e.g., different tests) you might not drop duplicates.
    student_academic_df = df[academic_columns]
    student_academic_df.to_csv("student_academic.csv", index=False)
    
    # --- 3. Create the Student Course Information Table ---
    course_columns = [
        "Student_Names", "Course_Recommendation", 
        "CourseCode", "ListofCourses", "RatingOfCourses"
    ]
    # Drop duplicates if the same student appears multiple times with the same course info
    student_courses_df = df[course_columns].drop_duplicates()
    student_courses_df.to_csv("student_courses.csv", index=False)
    
    print("Created student_personal.csv, student_academic.csv, and student_courses.csv successfully.")

# Specify your master CSV file for the student dataset
input_csv_file = r"C:\Users\NITRO\OneDrive\Desktop\Datasets\student_dataset_v1.csv"
split_student_dataset(input_csv_file)