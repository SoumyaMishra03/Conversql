SET SQL_SAFE_UPDATES = 0;
USE rockets_db;

-- 1. Retrieve all rockets
SELECT *
FROM rocket_general_info;

-- 2. Active rockets and their manufacturers
SELECT Name, Cmp, Status
FROM rocket_general_info
WHERE Status = 'Active';

-- 3. Rockets capable of >20 000 kg to LEO
SELECT Name, Payload_LEO
FROM rocket_technical_specs
WHERE Payload_LEO > 20000;

-- 4. Join general info with technical specs
SELECT g.Name,
       g.Cmp,
       g.Status,
       t.Liftoff_Thrust,
       t.Payload_LEO,
       t.Price_MUSD
FROM rocket_general_info AS g
JOIN rocket_technical_specs AS t
  ON g.Name = t.Name;

-- 5. Count rockets per company
SELECT Cmp,
       COUNT(*) AS rocket_count
FROM rocket_general_info
GROUP BY Cmp;

-- 6. Average price by stage count
SELECT Stages,
       AVG(Price_MUSD) AS avg_price_musd
FROM rocket_technical_specs
GROUP BY Stages;

-- 7. Rocket with maximum liftoff thrust
SELECT Name,
       Liftoff_Thrust
FROM rocket_technical_specs
WHERE Liftoff_Thrust = (
  SELECT MAX(Liftoff_Thrust)
  FROM rocket_technical_specs
);

-- 8. Top 3 rockets by GTO payload (window function)
SELECT Name,
       Payload_GTO
FROM (
  SELECT Name,
         Payload_GTO,
         RANK() OVER (ORDER BY Payload_GTO DESC) AS rnk
  FROM rocket_technical_specs
) AS ranked
WHERE rnk <= 3;

-- 9. Increase price of heavy rockets (stages > 2) by 5%
UPDATE rocket_technical_specs
SET Price_MUSD = Price_MUSD * 1.05
WHERE Stages > 2;

-- 10. Remove orphan general_info records
DELETE g
FROM rocket_general_info AS g
LEFT JOIN rocket_technical_specs AS t
  ON g.Name = t.Name
WHERE t.Name IS NULL;
