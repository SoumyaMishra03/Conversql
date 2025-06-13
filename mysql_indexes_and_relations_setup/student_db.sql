use student_db;
show tables;
select * from student_academic;
select * from student_courses;
select * from student_personal;

alter table student_academic add primary key(roll_no);
alter table student_courses add primary key(roll_no);
alter table student_personal add primary key(roll_no);

alter table student_courses add foreign key(roll_no) references student_academic(roll_no);
alter table student_courses add foreign key(roll_no) references student_personal(roll_no);


