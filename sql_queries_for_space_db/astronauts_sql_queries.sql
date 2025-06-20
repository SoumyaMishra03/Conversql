SELECT *
FROM astronauts
WHERE "astronaut id" = 101;

SELECT "name", "nationality", "total time in space"
FROM astronauts
WHERE "nationality" = 'India';

SELECT "astronaut id", "name", "missions"
FROM astronauts
WHERE "missions" LIKE '%Apollo%';

SELECT "space agency", AVG("total time in space") AS average_time
FROM astronauts
GROUP BY "space agency";

UPDATE astronauts
SET "missions" = CONCAT("missions", ', Lunar Mission')
WHERE "astronaut id" = 102;

DELETE FROM astronauts
WHERE "total time in space" < 50;
