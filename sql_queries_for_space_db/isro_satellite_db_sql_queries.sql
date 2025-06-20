SELECT *
FROM isro_satellites
WHERE "satellite id(fake)" = 101;

SELECT "basic info", "launch info", "orbital info"
FROM isro_satellites
WHERE "orbital info" LIKE '%geostationary%';

SELECT "satellite id(fake)", "basic info"
FROM isro_satellites
WHERE "launch info" >= '2020-01-01';

UPDATE isro_satellites
SET "basic info" = 'Updated basic info'
WHERE "satellite id(fake)" = 102;

DELETE FROM isro_satellites
WHERE "basic info" IS NULL;
