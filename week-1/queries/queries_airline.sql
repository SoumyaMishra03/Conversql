-- extended_queries.sql
-- This SQL file contains a comprehensive set of queries
-- that cover common and extra requests users might have.
-- It includes queries for the airports, flights, and passengers tables.

---------------------------------------------------------------------
--                    QUERIES FOR AIRPORTS TABLE
---------------------------------------------------------------------

-- 1. List all airports in a specific country
SELECT * FROM airports
WHERE CountryCode = 'US';

-- 2. Display all airports on a specific continent
SELECT * FROM airports
WHERE Continent = 'EU';

-- 3. Search for airports by partial name match (e.g., containing "International")
SELECT * FROM airports
WHERE AirportName LIKE '%International%';

-- 4. Filter airports by city
SELECT * FROM airports
WHERE City = 'Los Angeles';

-- 5. List airports sorted alphabetically by name
SELECT * FROM airports
ORDER BY AirportName ASC;

-- 6. Count the number of airports per country
SELECT CountryName, COUNT(*) AS NumberOfAirports
FROM airports
GROUP BY CountryName;

-- 7. Get a distinct list of countries that have airports in the system
SELECT DISTINCT CountryName
FROM airports;

-- 8. Retrieve airports for a specific country and sort them by city
SELECT * FROM airports
WHERE CountryCode = 'US'
ORDER BY City ASC;

---------------------------------------------------------------------
--                    QUERIES FOR FLIGHTS TABLE
---------------------------------------------------------------------

-- 1. List all flights departing on a specific date
SELECT * FROM flights
WHERE DepartureDate = '2025-06-20';

-- 2. Show all flights with a specific status (e.g., Delayed)
SELECT * FROM flights
WHERE FlightStatus = 'Delayed';

-- 3. Find flights piloted by a specific pilot
SELECT * FROM flights
WHERE PilotName = 'Captain Smith';

-- 4. Retrieve flight details (PassengerID and DepartureDate) for cancelled flights
SELECT PassengerID, DepartureDate
FROM flights
WHERE FlightStatus = 'Cancelled';

-- 5. List all flights sorted by departure date in ascending order
SELECT * FROM flights
ORDER BY DepartureDate ASC;

-- 6. Count the total number of flights by each flight status
SELECT FlightStatus, COUNT(*) AS TotalFlights
FROM flights
GROUP BY FlightStatus;

-- 7. Retrieve flights by a pilot within a specific date range
SELECT * FROM flights
WHERE PilotName = 'Captain Smith'
  AND DepartureDate BETWEEN '2025-06-01' AND '2025-06-30';

-- 8. Find flights for a specific passenger
SELECT * FROM flights
WHERE PassengerID = '00kDrw';

-- 9. Retrieve flight details displaying departure and arrival times (if applicable)
SELECT FlightID, DepartureDate, DepartureTime, ArrivalTime, FlightStatus
FROM flights;

---------------------------------------------------------------------
--                    QUERIES FOR PASSENGERS TABLE
---------------------------------------------------------------------

-- 1. List all passengers from a specific nationality
SELECT * FROM passengers
WHERE Nationality = 'China';

-- 2. Retrieve details for a specific passenger by their ID
SELECT * FROM passengers
WHERE PassengerID = '00kDrw';

-- 3. List all passengers sorted by age in descending order
SELECT * FROM passengers
ORDER BY Age DESC;

-- 4. Search for passengers by partial name match
SELECT * FROM passengers
WHERE FirstName LIKE '%Ann%' OR LastName LIKE '%Ann%';

-- 5. Show the average age of passengers grouped by nationality
SELECT Nationality, AVG(Age) AS AverageAge
FROM passengers
GROUP BY Nationality;

-- 6. List passengers matching multiple conditions (e.g., females over 50 years old)
SELECT * FROM passengers
WHERE Gender = 'Female' AND Age > 50;

-- 7. Count the number of passengers per gender
SELECT Gender, COUNT(*) AS TotalPassengers
FROM passengers
GROUP BY Gender;

-- 8. Retrieve the youngest and oldest passenger in the system
SELECT MIN(Age) AS Youngest, MAX(Age) AS Oldest
FROM passengers;

-- 9. List passengers sorted by last name alphabetically
SELECT * FROM passengers
ORDER BY LastName ASC;

-- 10. Update a passenger's record (example: update the age for a specific passenger)
UPDATE passengers
SET Age = 35
WHERE PassengerID = '00kDrw';

-- 11. Delete a passenger record (for testing purposes -- use with caution)
DELETE FROM passengers
WHERE PassengerID = 'temporaryID';
