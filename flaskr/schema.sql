-- TODO need to add this table to postgres + add script to ensure db properly configured.
 TABLE IF EXISTS app_users;

CREATE TABLE app_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password TEXT NOT NULL,
    name TEXT,
    phone_number TEXT,
    profile_picture TEXT,
    email TEXT UNIQUE NOT NULL
);