SELECT *
FROM rockets
WHERE "rocket name" = 'Falcon 9';

SELECT "rocket name", "rocket type", "manufacturer", "launch site", "launch date"
FROM rockets
WHERE "payload capacity" >= 5000;

SELECT "rocket name", "fuel type", "thrust"
FROM rockets
WHERE "reusability" = 'Yes';

SELECT COUNT(*) AS manufacturer_count, "manufacturer"
FROM rockets
GROUP BY "manufacturer";

SELECT "rocket name", "stage count", "orbital capability", "engine type"
FROM rockets
WHERE "thrust" > (
    SELECT AVG("thrust") FROM rockets
)
ORDER BY "thrust" DESC;

UPDATE rockets
SET "reusability" = 'Yes'
WHERE "rocket name" = 'Falcon Heavy';

DELETE FROM rockets
WHERE "payload capacity" < 1000;
