SET SQL_SAFE_UPDATES = 0;
USE stars_db;

-- 1. Retrieve all star records
SELECT *
FROM stars;

-- 2. Find stars within 10 light‐years
SELECT Star_name, Distance
FROM stars
WHERE Distance < 10.0
ORDER BY Distance ASC;

-- 3. Compute mass‐to‐luminosity ratio
SELECT Star_name,
       Mass / NULLIF(Luminosity,0) AS mass_lum_ratio
FROM stars;

-- 4. Stars more luminous than average
SELECT Star_name, Luminosity
FROM stars
WHERE Luminosity > (
    SELECT AVG(Luminosity)
    FROM stars
);

-- 5. Size category counts by radius
SELECT
  CASE
    WHEN Radius < 1.0   THEN 'Small'
    WHEN Radius < 10.0  THEN 'Medium'
    ELSE 'Large'
  END AS size_category,
  COUNT(*) AS star_count
FROM stars
GROUP BY size_category;

-- 6. Star with maximum mass
SELECT Star_name, Mass
FROM stars
WHERE Mass = (
    SELECT MAX(Mass)
    FROM stars
);

-- 7. Top 5 closest stars (window function)
SELECT Star_name, Distance
FROM (
  SELECT Star_name,
         Distance,
         RANK() OVER (ORDER BY Distance ASC) AS rk
  FROM stars
) AS ranked
WHERE rk <= 5;

-- 8. Increase luminosity of heavy stars by 10% (fixed subquery for UPDATE)
UPDATE stars
SET Luminosity = Luminosity * 1.10
WHERE Mass > (
    SELECT avg_mass
    FROM (
      SELECT AVG(Mass) AS avg_mass
      FROM stars
    ) AS sub
);

-- 9. Remove very distant stars (beyond 1000 ly)
DELETE FROM stars
WHERE Distance > 1000.0;

-- 10. Average properties for nearby stars
SELECT
  AVG(Distance)   AS avg_distance,
  AVG(Mass)       AS avg_mass,
  AVG(Radius)     AS avg_radius,
  AVG(Luminosity) AS avg_luminosity
FROM stars
WHERE Distance <= 50.0;
