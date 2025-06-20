USE astronauts_db;

-- 1. List all astronauts  
SELECT *  
FROM personal_info;

-- 2. Filter by birth year  
SELECT name, nationality, year_of_birth  
FROM personal_info  
WHERE year_of_birth >= 1980;

-- 3. Join personal and mission info  
SELECT pi.name, mi.total_number_of_missions  
FROM personal_info AS pi  
JOIN mission_info AS mi  
  ON pi.id = mi.id;

-- 4. Avg EVA hours by occupation  
SELECT mi.occupation,  
       AVG(mp.eva_hrs_mission) AS avg_eva_per_mission  
FROM mission_performance AS mp  
JOIN mission_info     AS mi  
  ON mp.id = mi.id  
GROUP BY mi.occupation;

-- 5. Earliest mission per astronaut (subquery)  
SELECT pi.name, mi.year_of_mission  
FROM personal_info AS pi  
JOIN mission_info   AS mi  
  ON pi.id = mi.id  
WHERE mi.year_of_mission = (  
  SELECT MIN(year_of_mission)  
  FROM mission_info  
  WHERE id = pi.id  
);

-- 6. Top 5 by total hours in space (window function)  
SELECT id, name, total_hrs_sum  
FROM (  
  SELECT pi.id, pi.name, mp.total_hrs_sum,  
         RANK() OVER (ORDER BY mp.total_hrs_sum DESC) AS rank_hrs  
  FROM personal_info     AS pi  
  JOIN mission_performance AS mp  
    ON pi.id = mp.id  
) AS ranked  
WHERE rank_hrs <= 5;

-- 7. Update high-EVA performers  
UPDATE mission_performance  
SET field21 = 'EVA Specialist'  
WHERE total_eva_hrs > 50;

-- 8. Delete personal records without missions  
DELETE pi  
FROM personal_info AS pi  
LEFT JOIN mission_info AS mi  
  ON pi.id = mi.id  
WHERE mi.id IS NULL;

-- 9. Delete orphan mission entries  
DELETE mi  
FROM mission_info AS mi  
LEFT JOIN personal_info AS pi  
  ON mi.id = pi.id  
WHERE pi.id IS NULL;
