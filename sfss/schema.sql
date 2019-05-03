DROP table if exists users;
CREATE TABLE IF NOT EXISTS users (
	id SMALLINT unsigned primary key AUTO_INCREMENT,
	username VARCHAR(50) NOT NULL,
	password VARCHAR(41) NOT NULL,
	firstName VARCHAR(50),
	lastName VARCHAR(50),
	email VARCHAR(75) NOT NULL,
	groups TEXT,
	enabled boolean NOT NULL default true,
	UNIQUE (username),
	UNIQUE (email),
	INDEX (username),
	INDEX (email)) ENGINE=INNODB;

DROP table if exists groups;
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

DROP table if exists chats;
CREATE TABLE IF NOT EXISTS chats (
	id INT unsigned primary key AUTO_INCREMENT,
	name VARCHAR(30) NOT NULL,
	ctime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	atime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	mtime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	UID SMALLINT unsigned NOT NULL, #all rights
	readUsers VARCHAR(20), #chat visible
	readGroups VARCHAR(20),
	writeUsers VARCHAR(20), #write to chat
	writeGroups VARCHAR(20),
	uploadUsers VARCHAR(20), #send File
	uploadGroups VARCHAR(20),
	grantUsers VARCHAR(20), #grant permission
	grantGroups VARCHAR(20),
	OtherPermission TINYINT NOT NULL, #1 send #2 post #4 visible
	FOREIGN KEY (UID) REFERENCES users (id),
	UNIQUE(name),
	INDEX (name),
	INDEX (UID),
	INDEX(readUsers),
	INDEX(readGroups),
	INDEX(writeUsers),
	INDEX(writeGroups),
	INDEX(uploadUsers),
	INDEX(uploadGroups),
	INDEX(grantUsers),
	INDEX(grantGroups),
	INDEX (OtherPermission)) ENGINE=INNODB;

DROP table if exists files;
CREATE TABLE IF NOT EXISTS files (
	id INT unsigned primary key AUTO_INCREMENT,
	version SMALLINT unsigned, # rm NOT NULL -> trigger works around
	chatID INT unsigned NOT NULL,
	fileNO SMALLINT unsigned,
	owner SMALLINT unsigned NOT NULL,
	mtime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	compressed BOOLEAN DEFAULT FALSE NOT NULL,
	del BOOLEAN DEFAULT FALSE NOT NULL,
	url TEXT NOT NULL,
	FOREIGN KEY (chatID) REFERENCES chats (id),
	FOREIGN KEY (owner) REFERENCES users (id),
	INDEX (chatID),
	INDEX (fileNO),
	INDEX (version),
	INDEX (owner)) ENGINE=INNODB; #check if right index!!!

DROP table if exists chatEntries;
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

DROP table if exists TriggerLog;
create table TriggerLog (
	id int primary Key auto_increment,
    msg text);