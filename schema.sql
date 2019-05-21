DROP DATABASE IF EXISTS blog;
CREATE DATABASE IF NOT EXISTS blog;
USE blog;

DROP TABLE IF EXISTS members, users_facebook, users_google, entries;

-- CREATE TABLE users (
--       id INTEGER PRIMARY KEY AUTOINCREMENT,
--       username VARCHAR(50) UNIQUE NOT NULL,
--       password VARCHAR(50) NOT NULL
-- );

CREATE TABLE members (
       id INTEGER PRIMARY KEY AUTO_INCREMENT,
       username VARCHAR(50) NOT NULL,
       password VARCHAR(256) NOT NULL,
       email VARCHAR(50) UNIQUE,
       registered_by VARCHAR(50)
);

CREATE TABLE users_facebook (
       id INTEGER PRIMARY KEY AUTO_INCREMENT,
--       username VARCHAR(50) NOT NULL,
       email VARCHAR(50) UNIQUE NOT NULL,
       FOREIGN KEY (email) REFERENCES members (email),
       firstname VARCHAR(50) NOT NULL,
       lastname VARCHAR(50) NOT NULL,
       telephone VARCHAR(50) NOT NULL
);

CREATE TABLE users_google (
       id INTEGER PRIMARY KEY AUTO_INCREMENT,
--       username VARCHAR(50) NOT NULL,
--       FOREIGN KEY (username) REFERENCES members (username),
	email VARCHAR(50) UNIQUE NOT NULL,	
       FOREIGN KEY (email) REFERENCES members (email),
       firstname VARCHAR(50) NOT NULL,
       lastname VARCHAR(50) NOT NULL,
       career VARCHAR(50) NOT NULL     
);

CREATE TABLE entries (
       id INTEGER PRIMARY KEY AUTO_INCREMENT,
       author_id INTEGER NOT NULL,
       username VARCHAR(50),
       created TIMESTAMP NOT NULL DEFAULT CURRENT_TIME,
       title TEXT NOT NULL,
       body TEXT NOT NULL,
       FOREIGN KEY (author_id) REFERENCES members (id)
);
