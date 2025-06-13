use airline_db;
show tables;
select * from airports;
select * from flights;
select * from passengers;

SELECT AirportName, CountryCode,CountryName,Continent, COUNT(*) as count
FROM airports
GROUP BY AirportName, CountryCode,CountryName,Continent
HAVING count > 1;

set sql_safe_updates=0;

select * from airports where AirportName='Tucumã Airport';

delete from airports where AirportName='Tucumã Airport';

alter table airports add primary key(AirportName,CountryCode);

describe airports;

select count(PassengerID) from flights;
select count(distinct PassengerID) from flights;

SELECT PassengerID, COUNT(*) as count
FROM FLIGHTS
GROUP BY PassengerID
HAVING count > 1;

delete from flights where passengerid="mzwjgo" limit 1;

delete from flights where passengerid="pqvgsy" limit 1;

alter table flights add primary key(passengerid);

SELECT PassengerID, COUNT(*) as count
FROM passengers
GROUP BY PassengerID
HAVING count > 1;

delete from passengers where passengerid="mzwjgo" limit 1;

delete from passengers where passengerid="pqvgsy" limit 1;

alter table passengers add primary key(passengerid);

alter table flights add foreign key(passengerid) references passengers(passengerid);