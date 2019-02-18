DROP TABLE IF NOT EXISTS users;
CREATE TABLE users (
	id int primary key autoincrement,
	username char(50) not null,
	password
