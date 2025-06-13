-- product_db_overall.sql
-- **********************************************************************
-- This file contains a comprehensive set of queries for the product_db 
-- database, covering all three tables:
--
-- 1. products
--    - UniqId
--    - Category
--    - ProductTitle
--    - ProductDescription
--    - Brand
--    - PackSizeOrQuantity
--    - ImageUrls
--
-- 2. pricing
--    - UniqId (unique identifier for the pricing record)
--    - Mrp
--    - Price
--    - Offers
--    - ComboOffers
--
-- 3. availability
--    - UniqId (unique identifier for the availability record)
--    - SiteName
--    - StockAvailability
--    - ProductAsin
--
-- The queries below range from basic retrievals and filtering to complex
-- analytical joins covering all tables.
-- **********************************************************************

-----------------------------------------------------
--              QUERIES FOR products TABLE
-----------------------------------------------------

-- 1. Retrieve all product records
SELECT * 
FROM products;

-- 2. Retrieve details for a specific product by UniqId.
SELECT *
FROM products
WHERE UniqId = 'YOUR_SPECIFIC_UNIQID';

-- 3. Search for products by a partial match on the ProductTitle.
SELECT *
FROM products
WHERE ProductTitle LIKE '%Phone%';

-- 4. Retrieve products belonging to a specific Category.
SELECT *
FROM products
WHERE Category = 'Electronics';

-- 5. Retrieve products from a specific Brand.
SELECT *
FROM products
WHERE Brand = 'Dove';

-- 6. Filter products by PackSizeOrQuantity
--    (For example, cast the PackSizeOrQuantity if it is numeric in part)
SELECT *
FROM products
WHERE CAST(PackSizeOrQuantity AS UNSIGNED) > 500;

-- 7. List products sorted alphabetically by ProductTitle.
SELECT *
FROM products
ORDER BY ProductTitle ASC;

-- 8. Count the total number of products.
SELECT COUNT(*) AS TotalProducts
FROM products;

-- 9. Count products per Category.
SELECT Category, COUNT(*) AS TotalInCategory
FROM products
GROUP BY Category;

-- 10. Count products per Brand.
SELECT Brand, COUNT(*) AS TotalByBrand
FROM products
GROUP BY Brand;

-- 11. List products with long descriptions (e.g., > 100 characters).
SELECT *
FROM products
WHERE LENGTH(ProductDescription) > 100;

-- 12. List products along with a snippet (first 50 characters) of their description.
SELECT UniqId, ProductTitle, SUBSTRING(ProductDescription, 1, 50) AS DescriptionSnippet
FROM products;

-- 13. Find products whose PackSizeOrQuantity meets exactly '500g'.
SELECT *
FROM products
WHERE PackSizeOrQuantity = '500g';

-- 14. Retrieve products with multiple image URLs (assumed to be separated by a comma).
SELECT *
FROM products
WHERE INSTR(ImageUrls, ',') > 0;

-- 15. List distinct categories available.
SELECT DISTINCT Category
FROM products;

-----------------------------------------------------
--              QUERIES FOR pricing TABLE
-----------------------------------------------------

-- 16. Retrieve all pricing records.
SELECT * 
FROM pricing;

-- 17. Retrieve details for a specific pricing record by UniqId.
SELECT *
FROM pricing
WHERE UniqId = '0004e9533f8f25ab54cefae6eca80eca';

-- 18. Retrieve pricing records with MRP greater than 1000 INR.
SELECT *
FROM pricing
WHERE Mrp > 1000;

-- 19. List pricing records sorted by Price in ascending order.
SELECT *
FROM pricing
ORDER BY Price ASC;

-- 20. List pricing records sorted by Offers (assuming Offers stored as text with '%').
SELECT *
FROM pricing
ORDER BY REPLACE(Offers, '%', '') * 1 DESC;

-- 21. Calculate the average Price.
SELECT AVG(Price) AS AvgPrice
FROM pricing;

-- 22. Count pricing records with zero discount.
SELECT COUNT(*) AS ZeroOfferCount
FROM pricing
WHERE Offers = '0%';

-- 23. Count the total number of pricing records.
SELECT COUNT(*) AS TotalPricingRecords
FROM pricing;

-- 24. Retrieve products with high discount (Offers > 40%).
SELECT *
FROM pricing
WHERE REPLACE(Offers, '%', '') * 1 > 40;

-- 25. Identify products where MRP equals Price (i.e., no discount).
SELECT *
FROM pricing
WHERE Mrp = Price;

-- 26. Calculate effective discount amount (MRP - Price) and list by highest discount.
SELECT UniqId, Mrp, Price, (Mrp - Price) AS DiscountAmount
FROM pricing
ORDER BY DiscountAmount DESC;

-- 27. List pricing records that have a combo offer.
SELECT *
FROM pricing
WHERE ComboOffers IS NOT NULL 
  AND TRIM(ComboOffers) <> '';

-----------------------------------------------------
--              QUERIES FOR availability TABLE
-----------------------------------------------------

-- 28. Retrieve all availability records.
SELECT *
FROM availability;

-- 29. Retrieve details for a specific availability record by UniqId.
SELECT *
FROM availability
WHERE UniqId = '0004e9533f8f25ab54cefaefe6eca80eca';

-- 30. Retrieve availability records for a specific SiteName (e.g., 'Amazon In').
SELECT *
FROM availability
WHERE SiteName = 'Amazon In';

-- 31. Retrieve availability records where StockAvailability is 'YES'.
SELECT *
FROM availability
WHERE StockAvailability = 'YES';

-- 32. Search for records by partial ProductAsin (e.g., Asin containing 'B07').
SELECT *
FROM availability
WHERE ProductAsin LIKE '%B07%';

-- 33. List availability records sorted by ProductAsin.
SELECT *
FROM availability
ORDER BY ProductAsin ASC;

-- 34. Count total availability records.
SELECT COUNT(*) AS TotalAvailabilityRecords
FROM availability;

-- 35. Count records per SiteName.
SELECT SiteName, COUNT(*) AS TotalProducts
FROM availability
GROUP BY SiteName;

-- 36. List distinct ProductAsin values.
SELECT DISTINCT ProductAsin
FROM availability;

-- 37. Count the number of unique products available.
SELECT COUNT(DISTINCT ProductAsin) AS UniqueProducts
FROM availability;

-----------------------------------------------------
--              COMPLEX JOIN & ANALYTICAL QUERIES
-----------------------------------------------------

-- 38. Product Summary: Join products, pricing, and availability to produce a full view.
SELECT p.UniqId AS ProductID,
       p.ProductTitle,
       p.Category,
       p.Brand,
       p.PackSizeOrQuantity,
       p.ImageUrls,
       pr.Price,
       pr.Offers,
       pr.ComboOffers,
       pr.Mrp,
       pr.EffectiveDate,
       av.StockAvailability,
       av.SiteName,
       av.ProductAsin
FROM products p
LEFT JOIN pricing pr ON p.UniqId = pr.UniqId
LEFT JOIN availability av ON p.UniqId = av.ProductAsin;  
-- Note: Adjust join condition if ProductAsin in availability maps to products.UniqId

-- 39. Identify products low in stock with an active discount.
SELECT p.UniqId AS ProductID,
       p.ProductTitle,
       av.StockAvailability,
       pr.Price,
       pr.Discount
FROM products p
JOIN availability av ON p.UniqId = av.ProductAsin
JOIN pricing pr ON p.UniqId = pr.UniqId
WHERE av.StockAvailability = 'YES'
  AND av.UniqId IS NOT NULL
  AND pr.Discount > 0
ORDER BY av.StockAvailability ASC;

-- 40. Monthly Pricing Changes: Summary of pricing changes by month.
SELECT DATE_FORMAT(EffectiveDate, '%Y-%m') AS PriceMonth,
       COUNT(*) AS PricingChanges,
       AVG(Price) AS AvgPrice,
       AVG(REPLACE(Offers, '%', '') * 1) AS AvgOffer
FROM pricing
GROUP BY PriceMonth
ORDER BY PriceMonth;

-- 41. Total Inventory Value per Warehouse:
--     Compute value as Price * StockCount. Assuming pricing holds current price.
SELECT av.SiteName,
       SUM(pr.Price * 1 * -- Multiply by stock count; adjust if needed.
           (SELECT COUNT(*) FROM availability av2 WHERE av2.ProductAsin = pr.UniqId)
          ) AS InventoryValue
FROM pricing pr
JOIN availability av ON pr.UniqId = av.ProductAsin
GROUP BY av.SiteName
ORDER BY InventoryValue DESC;

-- 42. Calculate effective sale price after applying discount.
SELECT p.UniqId AS ProductID,
       p.ProductTitle,
       pr.Price,
       pr.Discount,
       pr.Price * (1 - REPLACE(pr.Discount, '%', '') / 100) AS EffectivePrice
FROM products p
JOIN pricing pr ON p.UniqId = pr.UniqId;

-- 43. Category Inventory Analysis: Count products, average stock, and average effective sale price by category.
SELECT p.Category,
       COUNT(*) AS TotalProducts,
       AVG( (SELECT COUNT(*) FROM availability av WHERE av.ProductAsin = p.UniqId) ) AS AvgStock,
       AVG(pr.Price * (1 - REPLACE(pr.Discount, '%', '') / 100)) AS AvgEffectivePrice
FROM products p
JOIN pricing pr ON p.UniqId = pr.UniqId
GROUP BY p.Category
ORDER BY TotalProducts DESC;

-- 44. Data Gap Report: List products without corresponding pricing or availability records.
SELECT p.UniqId,
       p.ProductTitle,
       p.Category,
       p.Brand
FROM products p
LEFT JOIN pricing pr ON p.UniqId = pr.UniqId
LEFT JOIN availability av ON p.UniqId = av.ProductAsin
WHERE pr.UniqId IS NULL OR av.ProductAsin IS NULL;
