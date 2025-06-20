USE natural_satellites_db;

-- 1. List all satellites
SELECT *
FROM satellite_identity;

-- 2. Get the satellite name for a specific planet
SELECT name
FROM satellite_identity
WHERE planet = 'Jupiter';

-- 3. Filter physical records by numeric density (cast from VARCHAR)
SELECT planet,
       radius,
       CAST(density AS DECIMAL(10,5)) AS density
FROM satellite_physical
WHERE CAST(density AS DECIMAL(10,5)) > 3.0;

-- 4. Join identity & physical to show key attributes
SELECT si.planet,
       si.name,
       CAST(sp.gm       AS DECIMAL(15,5)) AS gm,
       CAST(sp.radius   AS DECIMAL(10,5)) AS radius,
       CAST(sp.albedo   AS DECIMAL(10,5)) AS albedo
FROM satellite_identity AS si
JOIN satellite_physical AS sp
  ON si.planet = sp.planet;

-- 5. Satellites denser than average (subquery + cast)
SELECT planet,
       CAST(density AS DECIMAL(10,5)) AS density
FROM satellite_physical
WHERE CAST(density AS DECIMAL(10,5)) > (
  SELECT AVG(CAST(density AS DECIMAL(10,5)))
  FROM satellite_physical
);

-- 6. Satellite(s) with the maximum radius
SELECT si.name,
       CAST(sp.radius AS DECIMAL(10,5)) AS radius
FROM satellite_physical AS sp
JOIN satellite_identity  AS si
  ON sp.planet = si.planet
WHERE CAST(sp.radius AS DECIMAL(10,5)) = (
  SELECT MAX(CAST(radius AS DECIMAL(10,5)))
  FROM satellite_physical
);

-- 7. Top 3 brightest satellites (lowest magnitude)
SELECT name,
       magnitude
FROM (
  SELECT si.name,
         CAST(sp.magnitude AS DECIMAL(10,5)) AS magnitude,
         RANK() OVER (ORDER BY CAST(sp.magnitude AS DECIMAL(10,5)) ASC) AS mag_rank
  FROM satellite_identity AS si
  JOIN satellite_physical  AS sp
    ON si.planet = sp.planet
) AS ranked
WHERE mag_rank <= 3;

-- 8. Safely update albedo for 'Saturn' (cast + numeric filter)
UPDATE satellite_physical AS sp
SET sp.albedo = CAST(sp.albedo AS DECIMAL(10,5)) * 1.05
WHERE sp.planet = 'Saturn'
  AND sp.albedo REGEXP '^[0-9]+(\\.[0-9]+)?$';

-- 9. Remove identity entries without matching physical data
DELETE si
FROM satellite_identity AS si
LEFT JOIN satellite_physical AS sp
  ON si.planet = sp.planet
WHERE sp.planet IS NULL;
