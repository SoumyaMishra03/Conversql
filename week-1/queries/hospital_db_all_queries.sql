-- hospital_db_all_queries.sql
-- **********************************************************************
-- This file contains a comprehensive set of queries for the hospital_db
-- application containing two tables:
--
-- 1. patients
--    - Patient_ID
--    - Age
--    - Gender
--
-- 2. hospital_encounters
--    - Patient_ID
--    - Condition
--    - Procedure
--    - Cost
--    - Length_of_Stay
--    - Readmission
--    - Outcome
--    - Satisfaction
--
-- The queries range from basic retrievals to complex analytical and join
-- queries that a user might ask in a reporting or NLP-driven interface.
-- **********************************************************************

-----------------------------------------------------
--              QUERIES FOR patients TABLE
-----------------------------------------------------

-- 1. Retrieve all patient records.
SELECT *
FROM patients;

-- 2. Retrieve details for a specific patient by Patient_ID.
SELECT *
FROM patients
WHERE Patient_ID = 'P1001';

-- 3. List patients filtered by gender.
--    a) Female patients:
SELECT *
FROM patients
WHERE Gender = 'F';

--    b) Male patients:
SELECT *
FROM patients
WHERE Gender = 'M';

-- 4. List patients above a certain age (e.g., over 60).
SELECT *
FROM patients
WHERE Age > 60;

-- 5. List patients within an age range (e.g., between 30 and 50).
SELECT *
FROM patients
WHERE Age BETWEEN 30 AND 50;

-- 6. Sort patients by age (ascending order).
SELECT *
FROM patients
ORDER BY Age ASC;

-- 7. Sort patients by age (descending order).
SELECT *
FROM patients
ORDER BY Age DESC;

-- 8. Aggregate: Calculate the average, minimum, and maximum age of all patients.
SELECT AVG(Age) AS AvgAge,
       MIN(Age) AS Youngest,
       MAX(Age) AS Oldest
FROM patients;

-- 9. Grouping: Count the total number of patients and group them by gender.
SELECT Gender, COUNT(*) AS TotalPatients
FROM patients
GROUP BY Gender;

-- 10. Advanced: Group patients into age brackets.
SELECT
    CASE 
        WHEN Age < 20 THEN 'Below 20'
        WHEN Age BETWEEN 20 AND 29 THEN '20s'
        WHEN Age BETWEEN 30 AND 39 THEN '30s'
        WHEN Age BETWEEN 40 AND 49 THEN '40s'
        WHEN Age BETWEEN 50 AND 59 THEN '50s'
        ELSE '60 and above'
    END AS AgeBracket,
    COUNT(*) AS TotalPatients
FROM patients
GROUP BY AgeBracket
ORDER BY AgeBracket;


-----------------------------------------------------
--         QUERIES FOR hospital_encounters TABLE
-----------------------------------------------------

-- 11. Retrieve all hospital encounter records.
SELECT *
FROM hospital_encounters;

-- 12. Retrieve all encounters for a specific patient (by Patient_ID).
SELECT *
FROM hospital_encounters
WHERE Patient_ID = 'P1001';

-- 13. Filter encounters by Condition (e.g., Heart Disease).
SELECT *
FROM hospital_encounters
WHERE Condition = 'Heart Disease';

-- 14. Filter encounters by Procedure (e.g., Angioplasty).
SELECT *
FROM hospital_encounters
WHERE Procedure LIKE '%Angioplasty%';

-- 15. Retrieve encounters that cost more than a given threshold (e.g., > 10000 INR).
SELECT *
FROM hospital_encounters
WHERE Cost > 10000;

-- 16. Retrieve encounters with extended hospital stays (e.g., Length_of_Stay > 7 days).
SELECT *
FROM hospital_encounters
WHERE Length_of_Stay > 7;

-- 17. Retrieve encounters where the patient was readmitted.
SELECT *
FROM hospital_encounters
WHERE Readmission = 'Yes';

-- 18. Sort encounters by Cost (highest first).
SELECT *
FROM hospital_encounters
ORDER BY Cost DESC;

-- 19. Sort encounters by Length_of_Stay (longest stays first).
SELECT *
FROM hospital_encounters
ORDER BY Length_of_Stay DESC;

-- 20. Aggregate: Count the total number of encounters grouped by Outcome.
SELECT Outcome, COUNT(*) AS TotalEncounters
FROM hospital_encounters
GROUP BY Outcome;

-- 21. Aggregate: Total cost incurred per Condition.
SELECT Condition, SUM(Cost) AS TotalCost
FROM hospital_encounters
GROUP BY Condition;

-- 22. Aggregate: Compute the average Length_of_Stay grouped by Condition.
SELECT Condition, AVG(Length_of_Stay) AS AvgStay
FROM hospital_encounters
GROUP BY Condition;

-- 23. Aggregate: Calculate the average Satisfaction score grouped by Outcome.
SELECT Outcome, AVG(Satisfaction) AS AvgSatisfaction
FROM hospital_encounters
GROUP BY Outcome;

-----------------------------------------------------
--          COMPLEX JOIN & ANALYTICAL QUERIES
-----------------------------------------------------

-- 24. Full Patient Encounter Summary:
--     Join patients with hospital_encounters to show each patient’s total encounters
--     and the most recent encounter information.
SELECT p.Patient_ID,
       p.Age,
       p.Gender,
       COUNT(e.Condition) AS EncounterCount,
       MAX(e.Cost) AS HighestEncounterCost  -- example metric; adjust as needed
FROM patients p
LEFT JOIN hospital_encounters e ON p.Patient_ID = e.Patient_ID
GROUP BY p.Patient_ID, p.Age, p.Gender
ORDER BY EncounterCount DESC;

-- 25. Detailed encounter list for patients older than 60.
SELECT p.Patient_ID,
       p.Age,
       e.Condition,
       e.Procedure,
       e.Cost,
       e.Length_of_Stay,
       e.Readmission,
       e.Outcome,
       e.Satisfaction
FROM patients p
JOIN hospital_encounters e ON p.Patient_ID = e.Patient_ID
WHERE p.Age > 60
ORDER BY p.Patient_ID;

-- 26. Identify patients with frequent encounters.
--     For example, list patients with more than 5 encounters.
SELECT Patient_ID, COUNT(*) AS EncounterCount
FROM hospital_encounters
GROUP BY Patient_ID
HAVING COUNT(*) > 5;

-- 27. Analysis by Condition:
--     Summary per Condition showing average cost, average length of stay, and average satisfaction.
SELECT Condition,
       COUNT(*) AS EncounterCount,
       AVG(Cost) AS AvgCost,
       AVG(Length_of_Stay) AS AvgStay,
       AVG(Satisfaction) AS AvgSatisfaction
FROM hospital_encounters
GROUP BY Condition
ORDER BY EncounterCount DESC;

-- 28. Outcome Vs. Readmission Analysis:
--     Show the count of each Outcome split by Readmission status.
SELECT Readmission, Outcome, COUNT(*) AS CountPerGroup
FROM hospital_encounters
GROUP BY Readmission, Outcome
ORDER BY Readmission, CountPerGroup DESC;

-- 29. Identify encounters with high cost and long stays.
SELECT *
FROM hospital_encounters
WHERE Cost > 10000
  AND Length_of_Stay > 7;

-- 30. Retrieve encounters for a specific combination:
--     For example, encounters for Allergic Reactions where readmission is 'No' and satisfaction >= 4.
SELECT *
FROM hospital_encounters
WHERE Condition = 'Allergic Reaction'
  AND Readmission = 'No'
  AND Satisfaction >= 4;

-----------------------------------------------------
--          EXTRA QUERIES AND INSIGHTS
-----------------------------------------------------

-- 31. Compare average costs between encounters with and without readmission.
SELECT Readmission,
       AVG(Cost) AS AvgCost
FROM hospital_encounters
GROUP BY Readmission;

-- 32. Identify the top 3 conditions by total cost incurred.
SELECT Condition, SUM(Cost) AS TotalCost
FROM hospital_encounters
GROUP BY Condition
ORDER BY TotalCost DESC
LIMIT 3;

-- 33. For patients with a specific condition (e.g., Heart Disease),
--     list those who were readmitted along with their average satisfaction.
SELECT Patient_ID,
       AVG(Satisfaction) AS AvgSatisfaction,
       COUNT(*) AS Encounters
FROM hospital_encounters
WHERE Condition = 'Heart Disease'
  AND Readmission = 'Yes'
GROUP BY Patient_ID;

-- 34. Retrieve a combined report: for each condition, show the number of patients
--     (distinct Patient_ID) and the average cost.
SELECT Condition, COUNT(DISTINCT Patient_ID) AS NumPatients,
       AVG(Cost) AS AvgCost
FROM hospital_encounters
GROUP BY Condition;

-- 35. Find encounters with satisfaction below 3 and cost above average.
SELECT *
FROM hospital_encounters
WHERE Satisfaction < 3
  AND Cost > (SELECT AVG(Cost) FROM hospital_encounters);
