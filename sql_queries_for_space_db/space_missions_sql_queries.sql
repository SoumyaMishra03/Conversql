SELECT *
FROM space_missions
WHERE "mission id" = 501;

SELECT "mission id", "mission name", "launch date", "destination"
FROM space_missions
WHERE "mission status" = 'Successful';

SELECT "mission id", "mission name", "space agency", "crew count"
FROM space_missions
WHERE "launch date" >= '2024-01-01';

SELECT COUNT(*) AS total_missions, "space agency"
FROM space_missions
GROUP BY "space agency";

SELECT "mission id", "mission name", "mission success rate"
FROM (
    SELECT "mission id", "mission name", "mission success rate", 
           RANK() OVER (PARTITION BY "space agency" ORDER BY "mission success rate" DESC) AS rank_success
    FROM space_missions
) AS ranked
WHERE rank_success <= 3;

UPDATE space_missions
SET "mission status" = 'Delayed'
WHERE "mission id" = 502
  AND "launch date" < CURRENT_DATE;

DELETE FROM space_missions
WHERE "mission duration" < 24;
