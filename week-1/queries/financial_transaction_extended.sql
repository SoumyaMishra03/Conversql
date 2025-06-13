-- financial_transaction_extended.sql
-- **********************************************************************
-- This file contains a comprehensive set of queries for the 
-- financial_transaction database which includes two tables:
--   • customers
--   • transactions
--
-- The queries range from basic retrievals, filtering, sorting, 
-- aggregations, to complex join and analytical queries.
-- **********************************************************************


-----------------------------------------------------
--              QUERIES FOR customers TABLE
-----------------------------------------------------

-- 1. Retrieve all customer records
SELECT *
FROM customers;

-- 2. Retrieve details for a specific customer by CustomerID
SELECT *
FROM customers
WHERE CustomerID = 'C1010011';

-- 3. Search for customers by partial CustomerID (or name if available)
-- If CustomerName exists, you may use: WHERE CustomerName LIKE '%John%'
SELECT *
FROM customers
WHERE CustomerID LIKE '%101%';

-- 4. List customers from a specific location (e.g., MUMBAI)
SELECT *
FROM customers
WHERE CustLocation = 'MUMBAI';

-- 5. Filter customers by gender
SELECT *
FROM customers
WHERE CustGender = 'F';  -- Change to 'M' for male customers

-- 6. List all customers sorted by account balance (highest first)
SELECT *
FROM customers
ORDER BY CustAccountBalance DESC;

-- 7. Calculate the average account balance for all customers
SELECT AVG(CustAccountBalance) AS AvgAccountBalance
FROM customers;

-- 8. Count the total number of customers
SELECT COUNT(*) AS TotalCustomers
FROM customers;

-- 9. Count customers grouped by location
SELECT CustLocation, COUNT(*) AS NumCustomers
FROM customers
GROUP BY CustLocation;

-- 10. Count customers by gender
SELECT CustGender, COUNT(*) AS TotalByGender
FROM customers
GROUP BY CustGender;

-- 11. List customers along with computed age.
-- Assuming CustomerDOB is in 'DD/MM/YYYY' format.
SELECT CustomerID, CustGender, CustLocation, CustAccountBalance,
       TIMESTAMPDIFF(YEAR, STR_TO_DATE(CustomerDOB, '%d/%m/%Y'), CURDATE()) AS Age
FROM customers
ORDER BY Age DESC;

-- 12. Identify customers with account balance above a threshold (e.g., > 50000)
SELECT *
FROM customers
WHERE CustAccountBalance > 50000;

-- 13. Retrieve customers whose birthdays fall in a specific month (e.g., May)
SELECT *
FROM customers
WHERE MONTH(STR_TO_DATE(CustomerDOB, '%d/%m/%Y')) = 5;

-----------------------------------------------------
--              QUERIES FOR transactions TABLE
-----------------------------------------------------

-- 1. Retrieve all transaction records
SELECT *
FROM transactions;

-- 2. Retrieve details for a specific transaction by TransactionID
SELECT *
FROM transactions
WHERE TransactionID = 'T1000003';

-- 3. Retrieve transactions on a specific date (e.g., '14/9/16')
SELECT *
FROM transactions
WHERE TransactionDate = '14/9/16';

-- 4. Retrieve transactions for a specific customer (e.g., CustomerID 'C5231923')
SELECT *
FROM transactions
WHERE CustomerID = 'C5231923';

-- 5. Retrieve transactions with an amount greater than a threshold (e.g., > 1000 INR)
SELECT *
FROM transactions
WHERE TransactionAmount_INR > 1000;

-- 6. List transactions sorted chronologically (by date then time)
-- Adjust the date format ('%d/%m/%y') according to your actual format.
SELECT *
FROM transactions
ORDER BY STR_TO_DATE(TransactionDate, '%d/%m/%y') ASC, TransactionTime ASC;

-- 7. List transactions sorted by TransactionAmount_INR in descending order
SELECT *
FROM transactions
ORDER BY TransactionAmount_INR DESC;

-- 8. Calculate the total transaction amount (sum over all transactions)
SELECT SUM(TransactionAmount_INR) AS TotalTransactionAmount
FROM transactions;

-- 9. Count the total number of transactions
SELECT COUNT(*) AS TotalTransactions
FROM transactions;

-- 10. Calculate the average transaction amount
SELECT AVG(TransactionAmount_INR) AS AverageTransactionAmount
FROM transactions;

-- 11. Group transactions by TransactionDate to compute daily totals and averages
SELECT TransactionDate,
       COUNT(*) AS TransactionCount,
       SUM(TransactionAmount_INR) AS DailyTotal,
       AVG(TransactionAmount_INR) AS DailyAverage
FROM transactions
GROUP BY TransactionDate
ORDER BY STR_TO_DATE(TransactionDate, '%d/%m/%y') ASC;

-- 12. Identify the transaction with the highest amount
SELECT *
FROM transactions
ORDER BY TransactionAmount_INR DESC
LIMIT 1;

-- 13. Identify the transaction with the lowest amount
SELECT *
FROM transactions
ORDER BY TransactionAmount_INR ASC
LIMIT 1;

-- 14. Retrieve transactions falling within a specific time window.
--     For instance, transactions between 12:00:00 and 14:00:00 given TransactionTime stored as HHMMSS.
SELECT *
FROM transactions
WHERE TransactionTime BETWEEN 120000 AND 140000;

-- 15. Calculate total transaction amount per Customer
SELECT CustomerID, SUM(TransactionAmount_INR) AS TotalSpent
FROM transactions
GROUP BY CustomerID
ORDER BY TotalSpent DESC;

-- 16. Identify customers with more than 3 transactions
SELECT CustomerID, COUNT(*) AS NumTransactions
FROM transactions
GROUP BY CustomerID
HAVING COUNT(*) > 3;

-- 17. Retrieve transactions within a specific date range (e.g., from '1/8/16' to '14/9/16')
SELECT *
FROM transactions
WHERE STR_TO_DATE(TransactionDate, '%d/%m/%y') BETWEEN STR_TO_DATE('1/8/16', '%d/%m/%y')
                                                 AND STR_TO_DATE('14/9/16', '%d/%m/%y')
ORDER BY STR_TO_DATE(TransactionDate, '%d/%m/%y') ASC;

-- 18. Group transactions by month (format YYYY-MM) and compute monthly summaries
SELECT DATE_FORMAT(STR_TO_DATE(TransactionDate, '%d/%m/%y'), '%Y-%m') AS TransactionMonth,
       COUNT(*) AS TransactionCount,
       SUM(TransactionAmount_INR) AS TotalAmount
FROM transactions
GROUP BY TransactionMonth
ORDER BY TransactionMonth;

-- 19. Retrieve transactions with amounts in a specific range (e.g., between 200 and 1000 INR)
SELECT *
FROM transactions
WHERE TransactionAmount_INR BETWEEN 200 AND 1000;

-----------------------------------------------------
--              COMPLEX JOIN & ANALYTICAL QUERIES
-----------------------------------------------------

-- 1. Full Customer Transaction Summary:
--    Join customers and transactions to display, per customer, the total number
--    of transactions, total amount spent, and average transaction amount.
SELECT c.CustomerID,
       -- If additional fields exist such as CustomerName and Email, add them here.
       COUNT(t.TransactionID) AS TransactionCount,
       SUM(t.TransactionAmount_INR) AS TotalSpent,
       AVG(t.TransactionAmount_INR) AS AvgTransactionAmount
FROM customers c
LEFT JOIN transactions t ON c.CustomerID = t.CustomerID
GROUP BY c.CustomerID
ORDER BY TotalSpent DESC;

-- 2. List Customers with No Transactions:
SELECT c.CustomerID
FROM customers c
LEFT JOIN transactions t ON c.CustomerID = t.CustomerID
WHERE t.TransactionID IS NULL;

-- 3. Top 5 Customers by Total Transaction Amount:
SELECT c.CustomerID,
       SUM(t.TransactionAmount_INR) AS TotalSpent
FROM customers c
JOIN transactions t ON c.CustomerID = t.CustomerID
GROUP BY c.CustomerID
ORDER BY TotalSpent DESC
LIMIT 5;

-- 4. Month-over-Month Growth in Transaction Volume:
--    Summarize transaction count and total amount per month.
SELECT DATE_FORMAT(STR_TO_DATE(TransactionDate, '%d/%m/%y'), '%Y-%m') AS TransactionMonth,
       COUNT(*) AS TotalTransactions,
       SUM(TransactionAmount_INR) AS TotalAmount
FROM transactions
GROUP BY TransactionMonth
ORDER BY TransactionMonth;

-- 5. Customers with Consistent High-Value Transactions:
--    Identify customers who have more than 3 transactions each having amount above 5000 INR.
SELECT CustomerID, COUNT(*) AS HighValueTransactionCount
FROM transactions
WHERE TransactionAmount_INR > 5000
GROUP BY CustomerID
HAVING COUNT(*) > 3;
