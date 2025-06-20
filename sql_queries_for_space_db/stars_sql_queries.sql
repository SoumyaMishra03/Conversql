SELECT *
FROM stars
WHERE "star name" = 'Sirius';

SELECT "star name", "constellation", "apparent magnitude"
FROM stars
WHERE "constellation" = 'Orion';

SELECT "star name", "distance from earth", "luminosity"
FROM stars
WHERE "apparent magnitude" < 2;

SELECT COUNT(*) AS stars_count, "constellation"
FROM stars
GROUP BY "constellation";

SELECT "star name", "absolute magnitude", "spectral type", "mass",
       RANK() OVER (PARTITION BY "constellation" ORDER BY "absolute magnitude" ASC) AS rank_absolute
FROM stars
WHERE "binary system" = 'Yes';

UPDATE stars
SET "metallicity" = metallicity * 1.05
WHERE "star name" = 'Betelgeuse';

DELETE FROM stars
WHERE "age" < 1;
