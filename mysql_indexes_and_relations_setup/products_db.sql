use products_db;
show tables;

select * from availability;
select * from pricing;
select * from products;

alter table availability add primary key(uniqid);
alter table pricing add primary key(uniqid);
alter table products add primary key(uniqid);

alter table products add foreign key(uniqid) references pricing(uniqid);
alter table products add foreign key(uniqid) references availability(uniqid);