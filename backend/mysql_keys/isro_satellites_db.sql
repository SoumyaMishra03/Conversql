
use isro_satellites_db;
#show tables;
#select * from basic_info;
#select * from launch_info;
#select * from orbital_info;

alter table basic_info add primary key(`satellite id(fake)`);
alter table launch_info add primary key(`satellite id(fake)`);
alter table orbital_info add primary key(`satellite id(fake)`);

alter table basic_info add foreign key(`satellite id(fake)`) references launch_info(`satellite id(fake)`);
alter table basic_info add foreign key(`satellite id(fake)`) references orbital_info(`satellite id(fake)`);