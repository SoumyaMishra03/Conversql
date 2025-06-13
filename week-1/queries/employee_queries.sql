-- employee_queries.sql
-- **********************************************************************
-- This file contains queries for the following tables:
--   • employee_employment
--   • employee_personal
--   • employee_termination
--
-- The queries include basic selections, filtering, sorting, aggregations,
-- and extra complex queries that join tables and compute additional metrics.
-- **********************************************************************

-----------------------------------------------------
--              QUERIES FOR employee_employment
-----------------------------------------------------

-- 1. Retrieve all employee employment records
SELECT * FROM employee_employment;

-- 2. Retrieve details for a specific employee (by EmpID)
SELECT * FROM employee_employment
WHERE EmpID = 'E001';

-- 3. List active employees (EmployeeStatus 'Active' OR no ExitDate)
SELECT * FROM employee_employment
WHERE EmployeeStatus = 'Active'
      OR ExitDate IS NULL;

-- 4. List employees by a specific Business Unit (e.g., 'Sales')
SELECT * FROM employee_employment
WHERE BusinessUnit = 'Sales';

-- 5. List employees with managerial titles (any title containing 'Manager')
SELECT * FROM employee_employment
WHERE Title LIKE '%Manager%';

-- 6. List employees reporting to a specific supervisor (e.g., 'John Doe')
SELECT * FROM employee_employment
WHERE Supervisor = 'John Doe';

-- 7. Retrieve employees who joined on or after a given date ('2023-01-01')
SELECT * FROM employee_employment
WHERE StartDate >= '2023-01-01';

-- 8. List employees by EmployeeType and PayZone (e.g., Full-Time in Zone A)
SELECT * FROM employee_employment
WHERE EmployeeType = 'Full-Time'
  AND PayZone = 'Zone A';

-- 9. List terminated employees (those with a non-null ExitDate)
SELECT * FROM employee_employment
WHERE ExitDate IS NOT NULL;

-- 10. List employees sorted by their joining date (StartDate ascending)
SELECT * FROM employee_employment
ORDER BY StartDate ASC;

-- 11. Count employees by EmployeeClassification
SELECT EmployeeClassification, COUNT(*) AS TotalEmployees
FROM employee_employment
GROUP BY EmployeeClassification;

-- 12. Count employees per BusinessUnit
SELECT BusinessUnit, COUNT(*) AS EmployeeCount
FROM employee_employment
GROUP BY BusinessUnit;

-----------------------------------------------------
--              QUERIES FOR employee_personal
-----------------------------------------------------

-- 1. Retrieve personal details for a specific employee (by EmpID)
SELECT * FROM employee_personal
WHERE EmpID = 'E001';

-- 2. List employees who are married
SELECT EmpID, FirstName, LastName, MaritalDesc
FROM employee_personal
WHERE MaritalDesc = 'Married';

-- 3. List employees residing in a specific state (e.g., 'MA')
SELECT EmpID, FirstName, LastName, State
FROM employee_personal
WHERE State = 'MA';

-- 4. List employees by a specific RaceDesc (e.g., 'White')
SELECT EmpID, FirstName, LastName, RaceDesc
FROM employee_personal
WHERE RaceDesc = 'White';

-- 5. Search for employees by partial name match (e.g., containing 'Sam')
SELECT * FROM employee_personal
WHERE FirstName LIKE '%Sam%' OR LastName LIKE '%Sam%';

-- 6. List all employees sorted by date of birth (oldest to youngest)
--    Note: Convert DOB (assumed format DD-MM-YYYY) to date type for sorting
SELECT * FROM employee_personal
ORDER BY STR_TO_DATE(DOB, '%d-%m-%Y') ASC;

-- 7. Count the number of employees by GenderCode
SELECT GenderCode, COUNT(*) AS TotalEmployees
FROM employee_personal
GROUP BY GenderCode;

-- 8. List all employees with their ADEmail addresses
SELECT EmpID, FirstName, LastName, ADEmail
FROM employee_personal;

-----------------------------------------------------
--              QUERIES FOR employee_termination
-----------------------------------------------------

-- 1. Retrieve termination details for a specific employee (by EmpID)
SELECT * FROM employee_termination
WHERE EmpID = 'E001';

-- 2. List all employees with a specific termination type (e.g., 'Involuntary')
SELECT * FROM employee_termination
WHERE TerminationType = 'Involuntary';

-- 3. List records with empty or null TerminationDescription
SELECT * FROM employee_termination
WHERE TerminationDescription IS NULL
   OR TRIM(TerminationDescription) = '';

-- 4. List employees with non-empty TerminationDescription
SELECT * FROM employee_termination
WHERE TerminationDescription IS NOT NULL
  AND TRIM(TerminationDescription) <> '';

-- 5. Search for a specific keyword (e.g., 'redundancy') in termination descriptions
SELECT * FROM employee_termination
WHERE TerminationDescription LIKE '%redundancy%';

-- 6. Count terminations by TerminationType
SELECT TerminationType, COUNT(*) AS TerminationCount
FROM employee_termination
GROUP BY TerminationType;

-----------------------------------------------------
--              COMPLEX QUERIES (JOIN & COMPUTATIONS)
-----------------------------------------------------

-- 1. Full Employee Details: Join employment, personal, and termination info.
--    This outer join ensures that if termination info is missing, we still get the record.
SELECT e.EmpID, e.Title, e.BusinessUnit, e.EmployeeStatus, e.StartDate, e.ExitDate,
       p.FirstName, p.LastName, p.DOB, p.GenderCode, p.State, p.ADEmail,
       t.TerminationType, t.TerminationDescription
FROM employee_employment e
JOIN employee_personal p ON e.EmpID = p.EmpID
LEFT JOIN employee_termination t ON e.EmpID = t.EmpID;

-- 2. Calculate Employee Tenure: Compute the number of days between StartDate and ExitDate.
--    For active employees, we can use the current date.
--    (Assumes that StartDate and ExitDate are in a date-compatible format.)
SELECT EmpID, Title, StartDate,
       COALESCE(ExitDate, CURDATE()) AS EndDate,
       DATEDIFF(COALESCE(ExitDate, CURDATE()), StartDate) AS TenureDays
FROM employee_employment;

-- 3. Average Tenure of Terminated Employees: Compute average tenure for employees that have been terminated.
SELECT AVG(TenureDays) AS AvgTenure
FROM (
    SELECT DATEDIFF(ExitDate, StartDate) AS TenureDays
    FROM employee_employment
    WHERE ExitDate IS NOT NULL
) AS terminated_tenure;

-- 4. Employees with Age Above Overall Average:
--    First, compute overall average age from employee_personal and then list employees whose DOB indicates higher age.
--    (Note: This example assumes you convert DOB into age. Replace calculation as needed.)
SELECT p.EmpID, p.FirstName, p.LastName,
       TIMESTAMPDIFF(YEAR, STR_TO_DATE(p.DOB, '%d-%m-%Y'), CURDATE()) AS Age
FROM employee_personal p
WHERE TIMESTAMPDIFF(YEAR, STR_TO_DATE(p.DOB, '%d-%m-%Y'), CURDATE()) >
      (SELECT AVG(TIMESTAMPDIFF(YEAR, STR_TO_DATE(DOB, '%d-%m-%Y'), CURDATE()))
       FROM employee_personal);

-- 5. Count of Active vs. Terminated Employees by Business Unit:
--    An example of subqueries and grouping.
SELECT BusinessUnit,
       (SELECT COUNT(*) FROM employee_employment e2
        WHERE e2.BusinessUnit = e.BusinessUnit
          AND (EmployeeStatus = 'Active' OR ExitDate IS NULL)) AS ActiveCount,
       (SELECT COUNT(*) FROM employee_employment e3
        WHERE e3.BusinessUnit = e.BusinessUnit
          AND ExitDate IS NOT NULL) AS TerminatedCount
FROM employee_employment e
GROUP BY BusinessUnit;

-- 6. List Employees whose Termination Reason Contains a Specific Word, WITH their Full Details:
SELECT e.EmpID, p.FirstName, p.LastName, t.TerminationDescription
FROM employee_employment e
JOIN employee_personal p ON e.EmpID = p.EmpID
JOIN employee_termination t ON e.EmpID = t.EmpID
WHERE t.TerminationDescription LIKE '%performance%';

-- 7. Find Employees with More Than One Record Issue:
--    For instance, if an employee is duplicated in personal table (an anomaly), list them.
--    Note: This query uses a HAVING clause to detect duplicates by EmpID.
SELECT EmpID, COUNT(*) AS RecordCount
FROM employee_personal
GROUP BY EmpID
HAVING COUNT(*) > 1;

-- 8. Comprehensive Search: Retrieve full details for employees with a specific criteria,
--    such as being active, belonging to a certain business unit, and over a certain age.
SELECT e.EmpID, e.Title, e.BusinessUnit, e.StartDate,
       p.FirstName, p.LastName, TIMESTAMPDIFF(YEAR, STR_TO_DATE(p.DOB, '%d-%m-%Y'), CURDATE()) AS Age
FROM employee_employment e
JOIN employee_personal p ON e.EmpID = p.EmpID
WHERE (e.EmployeeStatus = 'Active' OR e.ExitDate IS NULL)
  AND e.BusinessUnit = 'Engineering'
  AND TIMESTAMPDIFF(YEAR, STR_TO_DATE(p.DOB, '%d-%m-%Y'), CURDATE()) > 30;
