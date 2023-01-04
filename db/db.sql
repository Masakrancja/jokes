DROP TABLE IF EXISTS "user_arts_content";
DROP TABLE IF EXISTS "user_arts";
DROP TABLE IF EXISTS "arts_content";
DROP TABLE IF EXISTS "arts";
DROP TABLE IF EXISTS "users";
DROP TABLE IF EXISTS "departments";

PRAGMA foreign_keys = ON;

CREATE TABLE "departments" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "department_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "name_uri"  TEXT NOT NULL,
    "updated_at"   TEXT NOT NULL
);
CREATE UNIQUE INDEX "index_departments_department_id" ON departments(department_id);

CREATE TABLE "arts" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "art_id"  INTEGER NOT NULL,
    "department_id"  INTEGER NOT NULL,
    "hash"  TEXT NOT NULL,
    "updated_at"    TEXT NOT NULL
);
CREATE UNIQUE INDEX "index_arts_art_id" ON arts(art_id);
CREATE INDEX "index_arts_department_id" ON arts(department_id);
CREATE INDEX "index_arts_hash" ON arts(hash);

CREATE TABLE "users" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "login" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "updated_at"    TEXT NOT NULL
);

CREATE TABLE "arts_content" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "art_id" INTEGER NOT NULL,
    "isHighlight"   BOOLEAN,
    "accessionYear" INTEGER,
    "primaryImage"  TEXT,
    "primaryImageSmall" TEXT,
    "additionalImages"  TEXT,
    "objectName"    TEXT,
    "title" TEXT,
    "culture"   TEXT,
    "period"    TEXT,
    "dynasty"   TEXT,
    "reign" TEXT,
    "portfolio" TEXT,
    "artistRole"    TEXT,
    "artistDisplayName" TEXT,
    "artistDisplayBio"  TEXT,
    "artistNationality" TEXT,
    "artistBeginDate"   INTEGER,
    "artistEndDate" INTEGER,
    "artistGender"  TEXT,
    "artistWikidata_URL"    TEXT,
    "artistULAN_URL"    TEXT,
    "medium"    TEXT,
    "dimensions"    TEXT,
    "creditLine"    TEXT,
    "city"  TEXT,
    "state" TEXT,
    "county"    TEXT,
    "country"   TEXT,
    "classification"    TEXT,
    "linkResource"  TEXT,
    "metadataDate"  TEXT,
    "repository"    TEXT,
    "objectURL"   TEXT,
    "department_id"  INTEGER,
    "updated_at"    TEXT NOT NULL,
    FOREIGN KEY (art_id) REFERENCES arts(art_id),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);
CREATE INDEX "index_arts_content_art_id" ON arts_content(art_id);

CREATE TABLE "user_arts" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "user_id"   INTEGER NOT NULL,
    "art_id"    INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (art_id) REFERENCES arts(art_id)
);
CREATE INDEX "index_user_arts_user_id" ON user_arts(user_id);
CREATE INDEX "index_user_arts_art_id" ON user_arts(art_id);

CREATE TABLE "user_arts_content" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "user_arts_id" INTEGER NOT NULL,
    "info" TEXT,
    "note"  INTEGER,
    "updated_at"    TEXT NOT NULL,
    FOREIGN KEY (user_arts_id) REFERENCES user_arts(id)
);
CREATE INDEX "index_user_arts_content_user_arts_id" ON user_arts_content(user_arts_id);