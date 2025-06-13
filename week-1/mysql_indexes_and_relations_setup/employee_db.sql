use employee_db;
show tables;
select * from employee_employment;
select * from employee_personal;
select * from employee_termination;

alter table employee_employment add primary key(empid);
alter table employee_personal add primary key(empid);
alter table employee_termination add primary key(empid);

alter table employee_employment add foreign key(empid) references employee_personal(empid);
alter table employee_employment add foreign key(empid) references employee_termination(empid);