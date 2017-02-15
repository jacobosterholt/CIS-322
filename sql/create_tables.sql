-- Uses a unique integer for the primary key.
-- Both the username and password are at most 16 characters.

CREATE TABLE users (
	user_pk integer PRIMARY KEY,
	username varchar(16),
	password varchar(16)
);

-- Uses a unique integer for the primary key.
-- The title is at most 50 characters.

CREATE TABLE roles (
	role_pk integer PRIMARY KEY,
	title varchar(50)
);

-- Both columns reference primary keys to match a user with a role. 

CREATE TABLE user_is (
	user_fk integer REFERENCES users(user_pk),
	role_fk integer REFERENCES roles(role_pk)
);

-- Uses a unique integer for the primary key.
-- Asset_tag is at most 16 characters.
-- Description is at most 50 characters.

CREATE TABLE assets (
	asset_pk integer PRIMARY KEY,
	asset_tag varchar(16),
    description varchar(50)
);

-- Uses a unique integer for the primary key.
-- Common_name is at most 32 characters.
-- Facility_code is at most 6 characters.

CREATE TABLE facilities (
	facility_pk integer PRIMARY KEY,
	common_name varchar(32),
    facility_code varchar(6)
);

-- asset_fk and facility_fk match an asset with a facility.
-- arrive_dt is the timestamp of when the asset arrived at the facility.
-- depart_dt is the timestamp of when the asset left the facility.

CREATE TABLE asset_at (
	asset_fk integer REFERENCES assets(asset_pk),
	facility_fk integer REFERENCES facilities(facility_pk),
    arrive_dt timestamp,
    depart_dt timestamp
);