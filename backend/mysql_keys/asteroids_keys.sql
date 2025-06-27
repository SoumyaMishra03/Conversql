use asteroids_db;
# select * from neo_reference;
# select `name` , count(`name`) from `neo_reference` group by `name` having count(`name`)>1;
alter table neo_reference drop `neo reference id`;
alter table neo_reference add primary key(`name`);
alter table orbit_data add primary key(`neo reference id`);
alter table close_approach add primary key(`neo reference id`);
alter table neo_reference add foreign key(`name`) references orbit_data(`neo reference id`);
alter table neo_reference add foreign key(`name`) references close_approach(`neo reference id`);