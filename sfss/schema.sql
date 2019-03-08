CREATE TABLE IF NOT EXISTS users (
	id SMALLINT unsigned primary key AUTO_INCREMENT,
	username VARCHAR(50) NOT NULL,
	password VARCHAR(41) NOT NULL,
	firstName VARCHAR(50),
	lastName VARCHAR(50),
	email VARCHAR(75) NOT NULL,
	enabled boolean NOT NULL default true,
	UNIQUE (username),
	UNIQUE (email),
	INDEX (username),
	INDEX (email)) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS groups (
	id SMALLINT unsigned primary key AUTO_INCREMENT,
	groupname VARCHAR(50) NOT NULL,	
	owner SMALLINT unsigned REFERENCES users(id),
	ctime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	mtime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	members TEXT NOT NULL,
	admins TEXT NOT NULL,
	enabled boolean default true,
	UNIQUE(groupname),
	INDEX (groupname)) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS chats (
	id INT unsigned primary key AUTO_INCREMENT,
	name VARCHAR(30) NOT NULL,
	ctime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	atime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	mtime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	UID SMALLINT unsigned NOT NULL,
	GID SMALLINT unsigned NOT NULL,
	OwnerPermission TINYINT NOT NULL,
	GroupPermission TINYINT NOT NULL,
	OtherPermission TINYINT NOT NULL,
	admins TEXT NOT NULL,	
	FOREIGN KEY (UID) REFERENCES users (id),
	FOREIGN KEY (GID) REFERENCES groups (id),
	UNIQUE(name),
	INDEX (name),
	INDEX (UID),
	INDEX (GID),
	INDEX (OwnerPermission),
	INDEX (GroupPermission),
	INDEX (OtherPermission)) ENGINE=INNODB;
	
CREATE TABLE IF NOT EXISTS files (
	id INT unsigned primary key AUTO_INCREMENT,
	fileNO TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	chatID INT unsigned NOT NULL,
	position TINYINT unsigned DEFAULT NULL,
	owner SMALLINT unsigned NOT NULL,
	mtime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	compressed BOOLEAN DEFAULT FALSE NOT NULL,
	del BOOLEAN DEFAULT FALSE NOT NULL,
	url varchar(50) NOT NULL,
	FOREIGN KEY (chatID) REFERENCES chats (id),
	FOREIGN KEY (owner) REFERENCES users (id),
	INDEX (chatID),
	INDEX (position),
	INDEX (owner)) ENGINE=INNODB; #check if right index!!!

CREATE TABLE IF NOT EXISTS chatEntries (
	id INT unsigned primary key AUTO_INCREMENT,
	author SMALLINT unsigned NOT NULL,
	ChatID INT unsigned NOT NULL,
	ctime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	file INT unsigned DEFAULT NULL,
	content TEXT NOT NULL,
	FOREIGN KEY (author) REFERENCES users(id),
	FOREIGN KEY (chatID) REFERENCES chats(id),
	FOREIGN KEY (file) REFERENCES files(id),
	INDEX (chatID)) ENGINE=INNODB;
	