DROP TABLE IF EXISTS user_groups;

DROP TABLE IF EXISTS subject_diagnosis;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS consents;
DROP TABLE IF EXISTS diagnosis;

DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	username VARCHAR(255) UNIQUE NOT NULL,
	fullname VARCHAR(1024) NOT NULL,
	password VARCHAR(1024) NOT NULL,
	is_global_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE projects (
	id SERIAL PRIMARY KEY,
	parent_id INTEGER REFERENCES projects(id),	-- This may or may not be needed - 
	name VARCHAR(255) UNIQUE NOT NULL,
 	UNIQUE (parent_id, name)
 );

CREATE TABLE groups (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL REFERENCES projects(id),
	name VARCHAR(255) UNIQUE NOT NULL,
	is_admin BOOLEAN DEFAULT FALSE,
	is_readonly BOOLEAN DEFAULT FALSE,
	UNIQUE (project_id, name)
);

CREATE TABLE user_groups (
	user_id INTEGER NOT NULL REFERENCES users(id),
	group_id INTEGER NOT NULL REFERENCES groups(id),
	PRIMARY KEY (user_id, group_id)
);


-- default root password is 'password' - you should chnage that.
INSERT INTO users (id, username, fullname, password, is_global_admin) VALUES (1, 'root', 'Global Admin', 'pbkdf2$42e34a6e0e22ad2bb256b69768761e67$c1b40e85590b87bc93f1a56374c67aaf8487537799f9a534bf0baa6b556e17d8', TRUE);

