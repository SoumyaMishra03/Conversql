-- student_db_overall_queries.sql
-- **********************************************************************
-- This file contains a comprehensive set of SQL queries for the student
-- database, which consists of 3 tables:
--
-- 1. student_academic
--    - Roll_No, Student_Names, Study_Hours, Part_Time_Job,
--      Math, Physics, Chemistry, Grade, Comment
--
-- 2. student_courses
--    - Roll_No, Student_Names, Course_Recommendation, CourseCode, 
--      ListofCourses, RatingOfCourses
--
-- 3. student_personal
--    - Roll_No, Student_Names, Phone_No, Gender
--
-- The queries below cover:
--    • Basic retrievals for each table
--    • Filtering, sorting, and aggregation examples
--    • Multi-table join queries for full student profiles and reports
-- **********************************************************************

-----------------------------------------------------
--         QUERIES FOR student_academic TABLE
-----------------------------------------------------

-- 1. Retrieve all academic records.
SELECT * 
FROM student_academic;

-- 2. Retrieve the academic record for a specific student (e.g., Roll_No = 1).
SELECT *
FROM student_academic
WHERE Roll_No = 1;

-- 3. List students who study more than 8 hours.
SELECT *
FROM student_academic
WHERE Study_Hours > 8;

-- 4. List students having a part-time job.
SELECT *
FROM student_academic
WHERE Part_Time_Job = 'Yes';

-- 5. List students of a particular Grade (for example: 'A').
SELECT *
FROM student_academic
WHERE Grade = 'A';

-- 6. Calculate the average study hours across all students.
SELECT AVG(Study_Hours) AS AvgStudyHours
FROM student_academic;

-- 7. Count the number of students per Grade.
SELECT Grade, COUNT(*) AS TotalStudents
FROM student_academic
GROUP BY Grade;

-----------------------------------------------------
--         QUERIES FOR student_courses TABLE
-----------------------------------------------------

-- 8. Retrieve all course records.
SELECT *
FROM student_courses;

-- 9. Retrieve course records for a specific student (e.g., Roll_No = 1).
SELECT *
FROM student_courses
WHERE Roll_No = 1;

-- 10. List all records sorted by course rating (RatingOfCourses descending).
SELECT *
FROM student_courses
ORDER BY RatingOfCourses DESC;

-- 11. Aggregate: Calculate the average rating of courses.
SELECT AVG(RatingOfCourses) AS AvgCourseRating
FROM student_courses;

-- 12. Group course records by CourseCode to count enrolled students.
SELECT CourseCode, COUNT(*) AS TotalStudents
FROM student_courses
GROUP BY CourseCode;

-----------------------------------------------------
--         QUERIES FOR student_personal TABLE
-----------------------------------------------------

-- 13. Retrieve all personal records.
SELECT *
FROM student_personal;

-- 14. Retrieve personal details for a specific student (e.g., Roll_No = 1).
SELECT *
FROM student_personal
WHERE Roll_No = 1;

-- 15. List all students of a specific gender (e.g., Female).
SELECT *
FROM student_personal
WHERE Gender = 'Female';

-- 16. Search for students whose names contain a specific string (e.g., 'Alex').
SELECT *
FROM student_personal
WHERE Student_Names LIKE '%Alex%';

-- 17. Count the total number of students.
SELECT COUNT(*) AS TotalStudents
FROM student_personal;

-----------------------------------------------------
--         COMBINED / JOIN QUERIES
-----------------------------------------------------

-- 18. Full Student Profile:
--     Join student_personal and student_academic to obtain a comprehensive academic profile.
SELECT p.Roll_No,
       p.Student_Names,
       p.Phone_No,
       p.Gender,
       a.Study_Hours,
       a.Part_Time_Job,
       a.Math,
       a.Physics,
       a.Chemistry,
       a.Grade,
       a.Comment
FROM student_personal p
JOIN student_academic a ON p.Roll_No = a.Roll_No
ORDER BY p.Roll_No;

-- 19. Student Course Report:
--     Join student_personal with student_courses to display course details for each student.
SELECT p.Roll_No,
       p.Student_Names,
       p.Phone_No,
       p.Gender,
       c.Course_Recommendation,
       c.CourseCode,
       c.ListofCourses,
       c.RatingOfCourses
FROM student_personal p
JOIN student_courses c ON p.Roll_No = c.Roll_No
ORDER BY p.Roll_No, c.CourseCode;

-- 20. Comprehensive Student Details:
--     Join all three tables to get a full portrait of each student's academic,
--     course, and personal information.
SELECT p.Roll_No,
       p.Student_Names,
       p.Phone_No,
       p.Gender,
       a.Study_Hours,
       a.Part_Time_Job,
       a.Math,
       a.Physics,
       a.Chemistry,
       a.Grade,
       a.Comment,
       c.Course_Recommendation,
       c.CourseCode,
       c.ListofCourses,
       c.RatingOfCourses
FROM student_personal p
JOIN student_academic a ON p.Roll_No = a.Roll_No
JOIN student_courses c ON p.Roll_No = c.Roll_No
ORDER BY p.Roll_No;

-- 21. List students with high course ratings (RatingOfCourses > 4) along with their Grades.
SELECT p.Roll_No,
       p.Student_Names,
       a.Grade,
       c.CourseCode,
       c.RatingOfCourses
FROM student_personal p
JOIN student_academic a ON p.Roll_No = a.Roll_No
JOIN student_courses c ON p.Roll_No = c.Roll_No
WHERE c.RatingOfCourses > 4
ORDER BY c.RatingOfCourses DESC;

-- 22. Count of students by gender.
SELECT Gender, COUNT(*) AS TotalByGender
FROM student_personal
GROUP BY Gender;

-- 23. Report: Average study hours for students with an 'A' Grade.
SELECT AVG(a.Study_Hours) AS AvgStudyHours_A_Grade
FROM student_academic a
WHERE a.Grade = 'A';
