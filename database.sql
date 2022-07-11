Create database spirit;

Use spirit;
DROP TABLE IF EXISTS hosuser;
CREATE TABLE hosuser (
	UID INT auto_increment NOT NULL,
	user_name varchar(100) NOT NULL,
	Password varchar(100) NOT NULL,
	access varchar(100) NOT NULL,
	CONSTRAINT user_PK PRIMARY KEY (UID),
	CONSTRAINT user_UN UNIQUE KEY (user_name)
);

Commit;

DROP TABLE IF EXISTS setting;
CREATE TABLE setting (
	min varchar(100) NOT NULL,
	hour varchar(100) NOT NULL,
	day varchar(100) NOT NULL,
	month varchar(100) NOT NULL,
	week varchar(100) NOT NULL,
	UID INT NOT NULL,
	timeID INT auto_increment NOT NULL,
	CONSTRAINT setting_PK PRIMARY KEY (timeID),
	CONSTRAINT setting_FK FOREIGN KEY (UID) REFERENCES hosuser(UID) ON DELETE CASCADE ON UPDATE CASCADE
);

Commit;


DROP TABLE IF EXISTS patience;
CREATE TABLE patience (
	Pid INT auto_increment NOT NULL,
	Pcid varchar(100) NOT NULL,
	Result varchar(100) DEFAULT NULL,
	CONSTRAINT patience_PK PRIMARY KEY (Pid),
	CONSTRAINT patience_UN UNIQUE KEY (Pcid)
);
Commit;

INSERT INTO hosuser (UID, user_name, Password, access) VALUES(1, 'admin', 'admin', '3');


INSERT INTO patience (Pid, Pcid, Result) VALUES(1, '321088199703180036', NULL);

commit;