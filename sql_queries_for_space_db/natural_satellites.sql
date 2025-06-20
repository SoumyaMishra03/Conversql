SELECT *
FROM natural_satellites
WHERE "satellite id" = 201;

SELECT "name","planet","discovery date"
FROM natural_satellites
WHERE "planet" = 'Jupiter';

SELECT "name","orbital period days","mean radius km"
FROM natural_satellites
WHERE "mean radius km" >= 1000 AND "orbital period days" <= 200;

SELECT "planet", COUNT(*) AS satellite_count
FROM natural_satellites
GROUP BY "planet";

SELECT "name","eccentricity"
FROM natural_satellites
WHERE "eccentricity" > (
    SELECT AVG("eccentricity")
    FROM natural_satellites
)
ORDER BY "eccentricity" DESC;

SELECT "name","planet","mass kg"
FROM (
    SELECT "name","planet","mass kg",
           RANK() OVER (PARTITION BY "planet" ORDER BY "mass kg" DESC) AS mass_rank
    FROM natural_satellites
) AS ranked
WHERE mass_rank <= 3;

UPDATE natural_satellites
SET "mean radius km" = "mean radius km" * 1.02
WHERE "satellite id" = 202;

DELETE FROM natural_satellites
WHERE "discovery date" < '1600-01-01';
