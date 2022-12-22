DROP TABLE IF EXISTS "jokes";
DROP TABLE IF EXISTS "users";
DROP TABLE IF EXISTS "categories";
DROP TABLE IF EXISTS "joke_categories";

PRAGMA foreign_keys = ON;

CREATE TABLE "joke_categories" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "category_id"   INTEGER NOT NULL,
    "joke_id"   INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (joke_id) REFERENCES jokes(id)
);

CREATE TABLE "jokes" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "user_id"   INTEGER NOT NULL,
    "content"   TEXT NOT NULL,
    "rate"  INTEGER,
    "category"  INTEGER,
    "created_at"    TEXT,
    "updated_at"    TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "users" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "login" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "created_at"    TEXT,
    "updated_at"   TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id) REFERENCES jokes(user_id)
);

CREATE TABLE "categories" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "created_at"   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO "categories" ("name") VALUES
    ('Clean'),
    ('Animal'),
    ('Food'),
    ('Sexual'),
    ('Knock Knock'),
    ('Sport'),
    ('Blondes'),
    ('Law'),
    ('Nerdy'),
    ('Relationship'),
    ('Deep Thougths'),
    ('Dark'),
    ('One Liner'),
    ('Political'),
    ('Chuck Norris'),
    ('Yo Momma'),
    ('NSFW'),
    ('Religious'),
    ('School'),
    ('Jewish'),
    ('Racist'),
    ('Insults'),
    ('Sexist'),
    ('Holiday'),
    ('Analogy'),
    ('Christmas'),
    ('Kids');







