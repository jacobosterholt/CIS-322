-- Uses a unique integer for the primary key.
-- Both the username and password are at most 16 characters.

CREATE TABLE users (
	user_pk integer PRIMARY KEY,
	username varchar(16),
	password varchar(16)
);
