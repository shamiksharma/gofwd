create table if not exists gofwd (alias char(50) primary key, link varchar(1024));
insert into gofwd (alias, link) values ("google", "http://www.google.com");
