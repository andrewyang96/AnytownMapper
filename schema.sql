CREATE TABLE credentials(
    provider    TEXT UNIQUE NOT NULL,
    api_key     TEXT NOT NULL
);

CREATE TABLE users(
    user_id     INT PRIMARY KEY NOT NULL,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL
);
