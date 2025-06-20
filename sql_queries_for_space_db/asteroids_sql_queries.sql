USE asteroids;
set SQL_SAFE_UPDATES = 0; 
-- 1. Retrieve all Near‐Earth Objects
SELECT *
FROM neo_reference;

-- 2. Filter by absolute magnitude (dimmer objects)
SELECT `Name`, `Absolute Magnitude`
FROM neo_reference
WHERE `Absolute Magnitude` > 22.0;

-- 3. Diameter‐based filtering
SELECT `Name`, `Est Dia in KM(min)`, `Est Dia in KM(max)`
FROM neo_reference
WHERE `Est Dia in KM(min)` >= 0.5
  AND `Est Dia in KM(max)` <= 2.0;

-- 4. Join with approach details for upcoming encounters
SELECT nr.`Name`,
       ca.`Close Approach Date`,
       ca.`Miss Dist.(kilometers)`
FROM neo_reference AS nr
JOIN close_approach AS ca
  ON nr.`Name` = ca.`Neo Reference ID`
WHERE ca.`Close Approach Date` >= '2025-01-01'
ORDER BY ca.`Close Approach Date`;

-- 5. Count of approach events per object
SELECT nr.`Name`, 
       COUNT(*) AS approach_count
FROM close_approach AS ca
JOIN neo_reference AS nr
  ON ca.`Neo Reference ID` = nr.`Name`
GROUP BY nr.`Name`;

-- 6. Smallest absolute magnitude (brightest) via subquery
SELECT `Name`, `Absolute Magnitude`
FROM neo_reference
WHERE `Absolute Magnitude` = (
    SELECT MIN(`Absolute Magnitude`)
    FROM neo_reference
);

-- 7. Top 5 fastest objects by relative velocity (window function)
SELECT Name, `Relative Velocity km per sec`
FROM (
    SELECT nr.`Name`,
           ca.`Relative Velocity km per sec`,
           RANK() OVER (ORDER BY ca.`Relative Velocity km per sec` DESC) AS rnk
    FROM close_approach AS ca
    JOIN neo_reference AS nr
      ON ca.`Neo Reference ID` = nr.`Name`
) AS ranked
WHERE rnk <= 5;

-- 8. Mark low‐eccentricity orbits as non‐hazardous
UPDATE orbit_data
SET `Hazardous` = 'No'
WHERE `Eccentricity` < 0.1;

-- 9. Delete orphan orbit records
DELETE od
FROM orbit_data AS od
LEFT JOIN neo_reference AS nr
  ON od.`Neo Reference ID` = nr.`Name`
WHERE nr.`Name` IS NULL;
