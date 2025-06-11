use financial_transaction;
show tables;
select * from customers;
select * from transactions;

select count(customerid) from customers;
select count(distinct customerid) from customers;

select count(customerid) from transactions;
select count(distinct customerid) from transactions;

alter table transactions add primary key(transactionid);

alter table customers add primary key(customerid);
