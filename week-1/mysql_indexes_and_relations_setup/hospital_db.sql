use hospital_db;
show tables;
select * from patients;
select * from hospital_encounters;

alter table patients add primary key(patient_id);
alter table hospital_encounters add primary key(patient_id);

alter table patients add foreign key (patient_id) references hospital_encounters(patient_id)

