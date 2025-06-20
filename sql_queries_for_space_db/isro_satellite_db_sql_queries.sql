USE isro_satellites_db;

-- 1. Retrieve all satellite records
SELECT *
FROM basic_info;

-- 2. Filter by registry country
SELECT `Current Official Name of Satellite`, `Operator/Owner`
FROM basic_info
WHERE `Country/Org of UN Registry` = 'India';

-- 3. Join basic and launch details
SELECT bi.`Current Official Name of Satellite` AS satellite,
       li.`Date of Launch`,
       li.`Launch Vehicle`
FROM basic_info AS bi
JOIN launch_info AS li
  ON bi.`Satellite ID(Fake)` = li.`Satellite ID(Fake)`;

-- 4. Count satellites per operator
SELECT `Operator/Owner`, COUNT(*) AS satellite_count
FROM basic_info
GROUP BY `Operator/Owner`;

-- 5. Satellites heavier than average mass
SELECT li.`Satellite ID(Fake)`, li.`Launch Mass (kg.)`
FROM launch_info AS li
WHERE li.`Launch Mass (kg.)` > (
    SELECT AVG(`Launch Mass (kg.)`)
    FROM launch_info
);

-- 6. Low-perigee orbits
SELECT bi.`Current Official Name of Satellite` AS satellite,
       oi.`Perigee (km)`, oi.`Inclination (degrees)`
FROM orbital_info AS oi
JOIN basic_info   AS bi
  ON oi.`Satellite ID(Fake)` = bi.`Satellite ID(Fake)`
WHERE oi.`Perigee (km)` < 500;

-- 7. Top 3 largest apogees
SELECT satellite, `Apogee (km)`
FROM (
    SELECT bi.`Current Official Name of Satellite` AS satellite,
           oi.`Apogee (km)`,
           RANK() OVER (ORDER BY oi.`Apogee (km)` DESC) AS rk
    FROM orbital_info AS oi
    JOIN basic_info   AS bi
      ON oi.`Satellite ID(Fake)` = bi.`Satellite ID(Fake)`
) AS ranked
WHERE rk <= 3;

-- 8. Mark expired satellites in launch_info.comments
UPDATE launch_info AS li
JOIN basic_info AS bi
  ON li.`Satellite ID(Fake)` = bi.`Satellite ID(Fake)`
SET li.`Comments` = CONCAT(IFNULL(li.`Comments`, ''), ' | Status: Expired')
WHERE TIMESTAMPDIFF(
    YEAR,
    li.`Date of Launch`,
    CURDATE()
) > li.`Expected Lifetime (yrs.)`;

-- 9. Remove orphan launch records
DELETE li
FROM launch_info AS li
LEFT JOIN basic_info AS bi
  ON li.`Satellite ID(Fake)` = bi.`Satellite ID(Fake)`
WHERE bi.`Satellite ID(Fake)` IS NULL;
