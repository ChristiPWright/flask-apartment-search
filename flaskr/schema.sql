DROP TABLE IF EXISTS app_users;

CREATE TABLE app_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    profile_picture TEXT,
    email TEXT UNIQUE NOT NULL
);