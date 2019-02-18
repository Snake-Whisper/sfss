DROP TABLE IF NOT EXISTS users;
CREATE TABLE users (
	id INT primary key AUTO_INCREMENT,
	username VARCHAR(50) not null,
	password VARCHAR(41) not null,
	firstName VARCHAR(50),
	lastName VARCHAR(50),
	email VARCHAR(75),
	enabled boolean default true) ENGINE=INNODB;
