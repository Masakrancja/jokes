DROP TABLE IF EXISTS "arts";
DROP TABLE IF EXISTS "users";
DROP TABLE IF EXISTS "departments";
DROP TABLE IF EXISTS "art_department";

PRAGMA foreign_keys = ON;

CREATE TABLE "art_department" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "department_id"   INTEGER NOT NULL,
    "art_id"   INTEGER NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (art_id) REFERENCES arts(id)
);

CREATE TABLE "arts" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "user_id"   INTEGER NOT NULL,
    "objectID"  INTEGER NOT NULL,
    "isHighlight"   BOOLEAN,
    "accessionYear" INTEGER
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
    "content"   TEXT,
    "rate"  INTEGER,
    "department"  INTEGER,
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
    FOREIGN KEY (id) REFERENCES arts(user_id)
);

CREATE TABLE "departments" (
    "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
    "department_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "name_uri"  TEXT NOT NULL,
    "created_at"   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


