CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

DROP TABLE IF EXISTS Tagged CASCADE;
DROP TABLE IF EXISTS Tags CASCADE;
DROP TABLE IF EXISTS Likes CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS Friends CASCADE;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Albums CASCADE;
DROP TABLE IF EXISTS Users CASCADE;


CREATE TABLE Users (
    user_id int4 AUTO_INCREMENT NOT NULL,
    email varchar(255) UNIQUE,
    password varchar(255),
    firstname varchar(100) DEFAULT '' NOT NULL,
    lastname varchar(100) DEFAULT '' NOT NULL,
    birthday date DEFAULT NULL,
    hometown VARCHAR(100) DEFAULT '' NOT NULL,
	gender VARCHAR(100) DEFAULT '' NOT NULL,
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Albums
(
    user_id int4,
    album_name VARCHAR(100),
    albumID int4 AUTO_INCREMENT UNIQUE,
    creation_date DATE,
    CONSTRAINT albums_pk PRIMARY KEY (albumID),
    CONSTRAINT albums_fk FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE
);

CREATE TABLE Pictures
(
    picture_id int4 AUTO_INCREMENT UNIQUE,
    user_id int4 NOT NULL,
    imgdata longblob NOT NULL,
    caption VARCHAR(255),
    albumID int4,
    INDEX upid_idx (user_id),
    CONSTRAINT pictures_pk PRIMARY KEY (picture_id),
    CONSTRAINT pictures_fk1 FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE,
    CONSTRAINT pictures_fk2 FOREIGN KEY (albumID) REFERENCES Albums (albumID) ON DELETE CASCADE
);


CREATE TABLE Friends
(
	user_id INTEGER NOT NULL,
	friend_id INTEGER NOT NULL, 
    CONSTRAINT friends_pk PRIMARY KEY (user_id, friend_id),
    CONSTRAINT friends_fk1 FOREIGN KEY (user_id) REFERENCES Users (user_id),
    CONSTRAINT friends_fk2 FOREIGN KEY (friend_id) REFERENCES Users (user_id)
);

CREATE TABLE Comments
(
	comment_id INTEGER AUTO_INCREMENT NOT NULL,
	user_id INTEGER NOT NULL,
	photo_id INTEGER NOT NULL,
	text VARCHAR(100) DEFAULT '' NOT NULL,
	date DATE,
    CONSTRAINT comments_pk PRIMARY KEY (comment_id),
    CONSTRAINT comments_fk1 FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE,
	CONSTRAINT comments_fk2 FOREIGN KEY (photo_id) REFERENCES Pictures (picture_id) ON DELETE CASCADE
);

CREATE TABLE Likes
(
	photo_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
    -- CONSTRAINT likes_pk PRIMARY KEY (photo_id, user_id),
    CONSTRAINT likes_fk1 FOREIGN KEY (photo_id) REFERENCES Pictures (picture_id) ON DELETE CASCADE,
    CONSTRAINT likes_fk2 FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE
);

CREATE TABLE Tags(
    tag_id INTEGER AUTO_INCREMENT,
    name VARCHAR(100) DEFAULT '' NOT NULL,
    CONSTRAINT tags_pk PRIMARY KEY (tag_id)
);

CREATE TABLE Tagged(
	photo_id int4 ,
	tag_id INTEGER ,
	-- CONSTRAINT tagged_pk PRIMARY KEY (photo_id, tag_id),
    CONSTRAINT tagged_fk1 FOREIGN KEY (photo_id) REFERENCES Pictures (picture_id) ON DELETE CASCADE,
    CONSTRAINT tagged_fk2 FOREIGN KEY (tag_id) REFERENCES Tags (tag_id) ON DELETE CASCADE
);


INSERT INTO Users (email, password,birthday,firstname,lastname) VALUES ('test@bu.edu', 'test','2001/11/11','firstname','lastname');
INSERT INTO Users (email, password,birthday,firstname,lastname) VALUES ('test1@bu.edu', 'test','2001/11/11','firstname1','lastname1');
INSERT INTO Users (email, password,birthday,firstname,lastname) VALUES ('test2@bu.edu', 'test','2001/11/11','firstname2','lastname2');
INSERT INTO Users (email, password,birthday,firstname,lastname) VALUES ('test3@bu.edu', 'test','2001/11/11','firstname3','lastname3');
INSERT INTO Users (email, password,birthday,firstname,lastname) VALUES ('test4@bu.edu', 'test','2001/11/11','firstname4','lastname4');
INSERT INTO Users (email, password,birthday,firstname,lastname) VALUES ('test5@bu.edu', 'test','2001/11/11','firstname5','lastname5');
INSERT INTO Users (user_id) VALUES ('-1');