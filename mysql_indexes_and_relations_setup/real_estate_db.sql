use real_estate_db;
show tables;
select * from features;
select * from locations;
select * from properties;

alter table properties add primary key(name);
alter table features add primary key(name);
alter table locations add primary key(name);

alter table properties add foreign key(name) references locations(name);
alter table properties add foreign key(name) references features(name);