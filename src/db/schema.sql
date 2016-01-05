DROP TABLE IF EXISTS meta;
DROP TABLE IF EXISTS audit;

DROP TABLE IF EXISTS user_groups;
DROP TABLE IF EXISTS location;

DROP TABLE IF EXISTS subject_diagnoses;
DROP TABLE IF EXISTS subject_study;
DROP TABLE IF EXISTS subject_status;
DROP TABLE IF EXISTS subject_status_values;

DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS subject_types;

DROP TABLE IF EXISTS diagnoses;
DROP TABLE IF EXISTS research_studies;

DROP TABLE IF EXISTS groups;

DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;

DROP TABLE IF EXISTS meta_kv;
DROP TABLE IF EXISTS logger;
DROP TYPE IF EXISTS LOGGER_LEVEL;

DROP TABLE  IF EXISTS  location CASCADE;

-- meta
-- Random information about this database e.g. schema version
-- Also used to verify DB connection
CREATE TABLE meta_kv (
	key VARCHAR(255) PRIMARY KEY,
	value TEXT
);

-- logger
-- Stores log information that would ordinarily be written to stderr
CREATE TYPE LOGGER_LEVEL AS ENUM ('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL');	

CREATE TABLE logger (
	id BIGSERIAL PRIMARY KEY,
	msg_ts TIMESTAMP NOT NULL DEFAULT (now() at time zone 'UTC'),
	level LOGGER_LEVEL NOT NULL,
	filename VARCHAR(1024),
	funcname VARCHAR(1024),
	lineno INT,
	msg TEXT
);

INSERT INTO meta_kv (key, value) VALUES ('ping', 'pong');

-- users
-- users who can log into the application
-- passwords are stored as a PBDKF2_HMAC or Kerberos.
CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	username VARCHAR(255) UNIQUE NOT NULL,
	fullname VARCHAR(1024) NOT NULL,
	password VARCHAR(1024) NOT NULL,
	is_global_admin BOOLEAN DEFAULT FALSE,
	is_active BOOLEAN DEFAULT TRUE,
	allow_password_change BOOLEAN DEFAULT TRUE
);


-- projects
-- projects are the primary unit of organization.
-- every other entity (aside from users) belong to a parent project
CREATE TABLE projects (
	id SERIAL PRIMARY KEY,
	parent_id INTEGER REFERENCES projects(id),	-- This may or may not be needed, I really want to get rid of it - 
	name VARCHAR(1024) NOT NULL,
	code VARCHAR(255) NOT NULL,
	is_active BOOLEAN DEFAULT TRUE,
    data JSON, -- arbitrary configuration values
	UNIQUE (parent_id, name)
 );

-- groups
-- groups are the primary unit of authorization
-- a user can belong to more than one group (in a project)
-- there are three permissions levels:
--   admin, readonly, readwrite (default)
CREATE TABLE groups (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL REFERENCES projects(id),
	name VARCHAR(255) UNIQUE NOT NULL,
	is_admin BOOLEAN DEFAULT FALSE,
	is_view BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
	UNIQUE (project_id, name)
);

-- user_groups
-- assigns users to groups
CREATE TABLE user_groups (
	user_id INTEGER NOT NULL REFERENCES users(id),
	group_id INTEGER NOT NULL REFERENCES groups(id),
	PRIMARY KEY (user_id, group_id)
);


-- subject_types
-- type of subject (patient, cell line, etc)
CREATE TABLE subject_types (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL REFERENCES projects(id),
	name VARCHAR(255) NOT NULL,
	fields TEXT -- what data can be stored (or needs to be) for this subject type
);


-- subjects
-- subjects could be a cell line or a patient
-- data stores information about the subject in a JSON block
-- this way we can store arbitrary information in a single field.

CREATE TABLE subjects (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL REFERENCES projects(id),
	subject_type_id INTEGER NOT NULL REFERENCES subject_types(id),
	name VARCHAR(255) NOT NULL,
	data TEXT, -- age, sex, etc...
	notes TEXT,
	UNIQUE (project_id, name)
);

-- subject_status_values
-- Each subject can have certain status values: enrolled, plasma collected, dna collected, sequenced, etc...
-- this will let us track the progress for each subject in the project.
CREATE TABLE subject_status_values (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL REFERENCES projects(id),
	name VARCHAR(255) UNIQUE NOT NULL,
	UNIQUE (project_id, name)
);

-- subject_status
-- Assign each subject a status. M:N, so that a subject can have more than status (not a strict directed graph)
CREATE TABLE subject_status (
	subject_id INTEGER NOT NULL REFERENCES subjects(id),
	status_id INTEGER NOT NULL REFERENCES subject_status_values(id),
	recorded_by INTEGER NOT NULL REFERENCES users(id),
	recorded_date DATE,
	PRIMARY KEY (subject_id, status_id)
);

-- diagnoses
-- possbile diagnoses in the project
-- could be project specific...
CREATE TABLE diagnoses (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL REFERENCES projects(id),
	name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
	UNIQUE (project_id, name)
);

-- subject_diagnoses
-- assign a diagnosis to a patient
CREATE TABLE subject_diagnoses (
	subject_id INTEGER NOT NULL REFERENCES subjects(id),
	diagnosis_id INTEGER NOT NULL REFERENCES diagnoses(id),
	days_from_primary DATE, -- the number of days since their primary diagnosis - this isn't PHI since it's a relative number
	recorded_by INTEGER NOT NULL REFERENCES users(id),
	recorded_date DATE, -- not sure about this, we might not be able to collect this.
	is_primary BOOLEAN DEFAULT FALSE,
	PRIMARY KEY (subject_id, diagnosis_id)
);


-- research_studies
-- for patients, these are informed consents/IRB protocols. for animals, IACUC protocols
CREATE TABLE research_studies (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL REFERENCES projects(id),
	name VARCHAR(255) NOT NULL,
	description TEXT,
	date_active DATE, -- date the protocol was entered?
    is_active BOOLEAN DEFAULT TRUE,
	UNIQUE (project_id, name)
);


-- subject_study
-- assign subjects to studies
CREATE TABLE subject_study (
	subject_id INTEGER NOT NULL REFERENCES subjects(id),
	study_id INTEGER NOT NULL REFERENCES research_studies(id),
	recorded_by INTEGER NOT NULL REFERENCES users(id),
	recorded_date DATE, -- not sure about this, we might not be able to collect this. this date is close to a treatment date.
	PRIMARY KEY (subject_id, study_id)
);



-- audit
-- monitor views and changes to entities
-- examples: user signed in, user viewed a subject, user added a diagnosis to subject
CREATE TABLE audit (
	id BIGSERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL REFERENCES projects(id),
	user_id INTEGER NOT NULL REFERENCES users(id),
	tstamp TIMESTAMP NOT NULL DEFAULT now(),
	entity VARCHAR(255),
	entity_id INTEGER,
	key VARCHAR(255) NOT NULL,
	msg TEXT
);

-- locations are nested
-- not specific to any type
-- owned by a project (top-level)
-- can be nested to a specific row/column in a parent (shelf, rack position, etc...)
CREATE TABLE location (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER REFERENCES location(id),
    parent_row INTEGER,
    parent_col INTEGER,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    my_rows INTEGER DEFAULT 0,
    my_cols INTEGER DEFAULT 0,
    name VARCHAR(255) NOT NULL,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- default root password is 'password' - you should chnage that.
INSERT INTO users (username, fullname, password, is_global_admin) VALUES ('root', 'Global Admin', 'pbkdf2$42e34a6e0e22ad2bb256b69768761e67$c1b40e85590b87bc93f1a56374c67aaf8487537799f9a534bf0baa6b556e17d8', TRUE);
-- for demo only 
INSERT INTO projects (name,code) VALUES ('test_p1', 't1'); 
INSERT INTO location (project_id,name) VALUES ('1','Building1');
INSERT INTO location (parent_id,project_id,name) VALUES ('1','1','SIM1');
INSERT INTO location (parent_id,project_id,name) VALUES ('2','1','Fridge1');
-- create a shelf with split into 2 rows and 4 columns
INSERT INTO location (parent_id,project_id,name,my_rows,my_cols) VALUES ('3','1','Shelf1','2','4');
-- create a box in row1, col1
-- box is a 8x8 
INSERT INTO location (parent_id,project_id,name,parent_row,parent_col,my_rows,my_cols) VALUES ('4','1','box123','1','1','8','8');
-- insert 2 tubes
INSERT INTO location (parent_id,project_id,name,parent_row,parent_col) VALUES ('5','1','barcode1','1','1');
INSERT INTO location (parent_id,project_id,name,parent_row,parent_col) VALUES ('5','1','barcode2','1','2');

-- insert a test diagnosis
INSERT INTO diagnoses (project_id,name) VALUES (1,'normal');
-- insert a test diagnosis
INSERT INTO research_studies (project_id,name,description,date_active) VALUES (1,'universal','test insert please replace','01/01/1990');
