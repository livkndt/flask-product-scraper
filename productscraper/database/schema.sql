drop table if exists category;
create table category (
	catId integer primary key,
	parentCatId integer not null,
	catTitle varchar(255) not null,
	catUrl varchar(255) not null
);

drop table if exists product;
create table product (
	prodId integer primary key autoincrement,
	prodCode varchar(255) not null,
	prodUrl varchar(255) not null,
	prodImg varchar(255) not null,
	prodName varchar(255) not null,
	prodPrice varchar(255) not null,
	catId integer not null
);
