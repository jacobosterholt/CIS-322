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

-- Insert the roles we need into the roles table.

INSERT INTO roles VALUES (1, 'Logistics Officer');
INSERT INTO roles VALUES (2, 'Facilities Officer');

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

-- Keeps track of the user that requested and approved the transfer,
-- the time of the request and approval, the facilities the asset is
-- going to and coming from, as well as the asset that is being moved.

CREATE TABLE transfers (
    transfer_pk integer PRIMARY KEY,
    request_user_fk integer REFERENCES users(user_pk),
    approve_user_fk integer REFERENCES users(user_pk),
    request_dt timestamp,
    approve_dt timestamp,
    source_facility_fk integer REFERENCES facilities(facility_pk),
    destination_facility_fk integer REFERENCES facilities(facility_pk),
    asset_fk integer REFERENCES assets(asset_pk)
);

-- Keeps track of the assets that are in transit as well as the
-- facilities they are going to and coming from and the depart time
-- and arrival time.

CREATE TABLE in_transit (
    asset_fk integer REFERENCES assets(asset_pk),
    source_facility_fk integer REFERENCES facilities(facility_pk),
    destination_facility_fk integer REFERENCES facilities(facility_pk),
    load_dt timestamp,
    unload_dt timestamp
);