CREATE TABLE data(
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL
    );

CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    login TEXT NOT NULL,
    password_hash BYTEA NOT NULL
    );
