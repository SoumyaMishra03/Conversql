USE space_missions_db;

-- 1. List all organizations  
SELECT *  
FROM organizations;

-- 2. Rockets priced above 100 M  
SELECT id, Organisation, Price  
FROM rockets  
WHERE Price > 100.0;

-- 3. Organizations with scheduled missions (subquery)  
SELECT Organisation  
FROM organizations  
WHERE id IN (
  SELECT id 
  FROM missions 
  WHERE Mission_Status = 'Scheduled'
);

-- 4. Join organizations → rockets  
SELECT org.Organisation,
       rock.Details,
       rock.Rocket_Status
FROM organizations AS org
JOIN rockets       AS rock
  ON org.id = rock.id;

-- 5. Join organizations → missions  
SELECT org.Organisation,
       mis.Mission_Status
FROM organizations AS org
JOIN missions      AS mis
  ON org.id = mis.id;

-- 6. Count rockets per location  
SELECT org.Location,
       COUNT(rock.id) AS rocket_count
FROM organizations AS org
LEFT JOIN rockets AS rock
  ON org.id = rock.id
GROUP BY org.Location;

-- 7. Average rocket price for active missions (HAVING)  
SELECT org.Organisation,
       AVG(rock.Price) AS avg_price
FROM organizations AS org
JOIN rockets       AS rock
  ON org.id = rock.id
JOIN missions      AS mis
  ON org.id = mis.id
WHERE mis.Mission_Status = 'Active'
GROUP BY org.Organisation
HAVING avg_price > 50.0;

-- 8. Top 3 most expensive rockets (window function)  
SELECT id, Details, Price
FROM (
  SELECT id, Details, Price,
         RANK() OVER (ORDER BY Price DESC) AS rk
  FROM rockets
) AS ranked
WHERE rk <= 3;

-- 9. Archive cancelled missions  
UPDATE missions
SET Mission_Status = 'Archived'
WHERE Mission_Status = 'Cancelled';

-- 10. Delete rockets without an organization  
DELETE rock
FROM rockets AS rock
LEFT JOIN organizations AS org
  ON rock.id = org.id
WHERE org.id IS NULL;
