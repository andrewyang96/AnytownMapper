CREATE TABLE credentials(
    provider    TEXT UNIQUE NOT NULL,
    api_key     TEXT NOT NULL
);

CREATE TABLE users(
    user_id     BIGINT PRIMARY KEY UNIQUE NOT NULL,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL
);

CREATE TABLE map_cache(
    place_id        TEXT PRIMARY KEY UNIQUE NOT NULL,
    lat             REAL NOT NULL,
    lng             REAL NOT NULL,
    city            TEXT NOT NULL,
    region          TEXT,
    country_name    TEXT NOT NULL,
    country_code    TEXT NOT NULL
);

CREATE TABLE location_history(
    user_id     BIGINT NOT NULL,
    place_id    TEXT NOT NULL,
    timestamp   REAL NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(place_id) REFERENCES map_cache(place_id),
    PRIMARY KEY (user_id, place_id)
);
