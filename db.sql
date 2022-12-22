DROP TABLE IF EXISTS "users";
DROP TABLE IF EXISTS "jokes";
DROP TABLE IF EXISTS "categories";

CREATE TABLE "jokes" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "user_id"   INTEGER NOT NULL,
    "category_id"   INTEGER NOT NULL,
    "content"   TEXT NOT NULL,
    "rate"  INTEGER,
    "category"  INTEGER,
    "created_at"    TEXT,
    "updated_at"    TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "users" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "user_id"   INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "created_at"    TEXT,
    "updated_at"   TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES jokes(id)
);

CREATE TABLE "categories" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "category_id"   INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "created_at"    TEXT,
    "updated_at"   TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES jokes(id)
);
