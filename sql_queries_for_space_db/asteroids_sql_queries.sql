SELECT *
FROM asteroids
WHERE "neo reference id" = 12345;

SELECT "name", "absolute magnitude", hazardous
FROM asteroids
WHERE hazardous = 'Yes';

SELECT "neo reference id", "name", "est dia in km(min)" AS dia_min_km, "est dia in km(max)" AS dia_max_km
FROM asteroids
WHERE "est dia in km(min)" >= 0.5 AND "est dia in km(max)" <= 3.0;

SELECT "neo reference id", "name", "close approach date"
FROM asteroids
WHERE "close approach date" >= '2025-01-01'
ORDER BY "close approach date" DESC;

SELECT COUNT(*) AS earth_orbit_count
FROM asteroids
WHERE "orbiting body" = 'Earth';

SELECT a."neo reference id", a."name", a."relative velocity km per sec"
FROM asteroids a
WHERE a."relative velocity km per sec" > (
    SELECT AVG("relative velocity km per sec")
    FROM asteroids
    WHERE hazardous = 'Yes'
)
ORDER BY a."relative velocity km per sec" DESC;

SELECT "neo reference id", "name", "absolute magnitude", "orbiting body", mag_rank
FROM (
    SELECT "neo reference id", "name", "absolute magnitude", "orbiting body",
           RANK() OVER (PARTITION BY "orbiting body" ORDER BY "absolute magnitude" ASC) AS mag_rank
    FROM asteroids
) AS ranked
WHERE mag_rank <= 3;

DELETE FROM asteroids
WHERE hazardous = 'No' AND "absolute magnitude" > 25;

UPDATE asteroids
SET hazardous = 'No'
WHERE "neo reference id" = 67890
  AND "est dia in km(max)" < 0.5;
