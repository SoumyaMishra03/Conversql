use rockets_db;
#show tables;
#select * from rocket_general_info;
#select * from rocket_technical_specs;
alter table rocket_general_info add primary key(name);
alter table rocket_technical_specs add primary key(name);
alter table rocket_general_info add foreign key(name) references rocket_technical_specs(name);