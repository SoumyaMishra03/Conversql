use spacenews_db;
#show tables;
#select * from news_articles_table;
#select * from publishing_info;
alter table news_articles_table add foreign key(id) references publishing_info(id);