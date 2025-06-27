use space_missions_db;
#show tables;
#select * from missions ;
#select * from organizations;
#select * from rockets;
alter table organizations add foreign key(id) references missions(id);
alter table organizations add foreign key(id) references rockets(id);