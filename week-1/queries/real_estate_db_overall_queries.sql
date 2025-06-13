-- real_estate_db_overall_queries.sql
-- **********************************************************************
-- This file contains a comprehensive set of SQL queries for the real estate
-- database that includes the following 3 tables:
--
-- 1. features
--    - Columns: Property, Baths, Balcony
--
-- 2. locations
--    - Columns: Name, Location, Total_Area, Price_per_SQFT
--
-- 3. properties
--    - Columns: Name, PropertyTitle, Price, Description
--
-- The queries below include basic retrievals, filtering, sorting, aggregation,
-- and multi‑table join queries that combine data from these three tables.
-- **********************************************************************

-----------------------------------------------------
--         QUERIES FOR THE features TABLE
-----------------------------------------------------

-- 1. Retrieve all records from the features table.
SELECT * FROM features;

-- 2. Retrieve details for a specific property (e.g., 'Casagrand ECR 14').
SELECT *
FROM features
WHERE Property = 'Casagrand ECR 14';

-- 3. List properties with more than 3 bathrooms.
SELECT *
FROM features
WHERE Baths > 3;

-- 4. List properties that have a balcony.
SELECT *
FROM features
WHERE Balcony = 'Yes';

-- 5. Count the total number of properties without a balcony.
SELECT COUNT(*) AS NoBalconyCount
FROM features
WHERE Balcony = 'No';

-- 6. Calculate the average number of baths across all properties.
SELECT AVG(Baths) AS AvgBaths
FROM features;

-- 7. Retrieve properties with exactly 2 baths.
SELECT *
FROM features
WHERE Baths = 2;

-- 8. Retrieve properties with at least 5 baths and that have a balcony.
SELECT *
FROM features
WHERE Baths >= 5 AND Balcony = 'Yes';

-- 9. Group properties by balcony availability and count records.
SELECT Balcony, COUNT(*) AS TotalProperties
FROM features
GROUP BY Balcony;

-----------------------------------------------------
--         QUERIES FOR THE locations TABLE
-----------------------------------------------------

-- 10. Retrieve all records from the locations table.
SELECT * FROM locations;

-- 11. Retrieve details for a specific location (by Name).
SELECT *
FROM locations
WHERE Name = 'Madhurangan Apartment, Ambegaon, Pune';

-- 12. Retrieve locations for properties in a specific city (e.g., Pune).
SELECT *
FROM locations
WHERE Location LIKE '%Pune%';

-- 13. Sort locations by Price_per_SQFT in ascending order.
SELECT *
FROM locations
ORDER BY Price_per_SQFT ASC;

-- 14. Sort locations by Total_Area in descending order.
SELECT *
FROM locations
ORDER BY Total_Area DESC;

-- 15. Count the number of listings per unique Name.
SELECT Name, COUNT(*) AS ListingsCount
FROM locations
GROUP BY Name;

-- 16. Average Price_per_SQFT by City.
-- (Assuming city can be extracted from the Location field; here we assume the city is the last comma‐separated token)
SELECT SUBSTRING_INDEX(Location, ',', -1) AS City, 
       AVG(Price_per_SQFT) AS AvgPricePerSQFT
FROM locations
GROUP BY SUBSTRING_INDEX(Location, ',', -1);

-----------------------------------------------------
--         QUERIES FOR THE properties TABLE
-----------------------------------------------------

-- 17. Retrieve all records from the properties table.
SELECT * FROM properties;

-- 18. Retrieve details for a specific property by Name (e.g., 'Casagrand ECR 14').
SELECT *
FROM properties
WHERE Name = 'Casagrand ECR 14';

-- 19. Search for properties with a partial match in PropertyTitle (e.g., containing 'Apartment').
SELECT *
FROM properties
WHERE PropertyTitle LIKE '%Apartment%';

-- 20. List all properties sorted by Price in ascending order.
SELECT *
FROM properties
ORDER BY Price ASC;

-- 21. List properties sorted by Price in descending order.
SELECT *
FROM properties
ORDER BY Price DESC;

-- 22. Count the total number of properties.
SELECT COUNT(*) AS TotalProperties
FROM properties;

-- 23. Retrieve properties within a specific price range.
-- For example, properties priced between ₹50 Lakh and ₹1 Crore.
SELECT *
FROM properties
WHERE Price BETWEEN 5000000 AND 10000000;

-- 24. Retrieve properties that mention "Luxury" in either the PropertyTitle or Description.
SELECT *
FROM properties
WHERE PropertyTitle LIKE '%Luxury%' OR Description LIKE '%Luxury%';

-- 25. Retrieve a summary report: Name, PropertyTitle, and Price.
SELECT Name, PropertyTitle, Price
FROM properties;

-- 26. Retrieve properties with "Sea view" mentioned in the Description.
SELECT *
FROM properties
WHERE Description LIKE '%Sea view%';

-- 27. Calculate the average price of properties.
SELECT AVG(Price) AS AvgPrice
FROM properties;

-----------------------------------------------------
--         COMPLEX JOIN & ANALYTICAL QUERIES
-----------------------------------------------------

-- 28. Full Property Profile:
--     Join properties with features and locations to produce a comprehensive view.
SELECT p.Name AS PropertyName,
       p.PropertyTitle,
       p.Price,
       p.Description,
       l.Location,
       l.Total_Area,
       l.Price_per_SQFT,
       f.Baths,
       f.Balcony
FROM properties p
LEFT JOIN features f ON p.Name = f.Property
LEFT JOIN locations l ON p.Name = l.Name
ORDER BY p.Price DESC;

-- 29. Properties in a Specific City with Required Features:
--     For example, properties in Pune with more than 3 baths and with a balcony.
SELECT p.Name,
       p.PropertyTitle,
       p.Price,
       l.Location,
       f.Baths,
       f.Balcony
FROM properties p
JOIN features f ON p.Name = f.Property
JOIN locations l ON p.Name = l.Name
WHERE l.Location LIKE '%Pune%'
  AND f.Baths > 3
  AND f.Balcony = 'Yes'
ORDER BY p.Price ASC;

-- 30. Average Listing Price by City:
SELECT l.Location AS FullLocation,
       AVG(p.Price) AS AvgListingPrice,
       COUNT(*) AS NumProperties
FROM properties p
JOIN locations l ON p.Name = l.Name
GROUP BY l.Location
ORDER BY AvgListingPrice DESC;

-- 31. Count of Properties and Average Area By State:
-- (Assuming state is a component in the Location field; adjust extraction as needed)
SELECT SUBSTRING_INDEX(l.Location, ',', -2) AS StatePart,
       COUNT(*) AS TotalProperties,
       AVG(l.Total_Area) AS AvgArea
FROM locations l
GROUP BY SUBSTRING_INDEX(l.Location, ',', -2);

-- 32. Top 5 Most Expensive Properties:
SELECT *
FROM properties
ORDER BY Price DESC
LIMIT 5;

-- 33. Combined Report: List properties with high square footage and luxury price range.
-- For example, properties with Total_Area > 1000 (from locations) and Price > ₹1 Crore.
SELECT p.Name,
       p.PropertyTitle,
       p.Price,
       l.Total_Area,
       l.Location
FROM properties p
JOIN locations l ON p.Name = l.Name
WHERE l.Total_Area > 1000
  AND p.Price > 10000000
ORDER BY p.Price DESC;
