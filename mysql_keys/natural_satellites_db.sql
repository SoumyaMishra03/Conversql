use natural_satellites_db;
#show tables;
#select * from satellite_identity;
#select * from satellite_physical;

alter table satellite_identity add primary key(name);
alter table satellite_physical add primary key(name);

alter table satellite_identity add foreign key(name) references satellite_physical(name);