PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS peers;
CREATE TABLE peers (
    session_id char(16) PRIMARY KEY,
    ip char(55) NOT NULL,
    port char(5) NOT NULL
);

DROP TABLE IF EXISTS files;
CREATE TABLE files (
    file_md5 char(32) PRIMARY KEY,
    file_name char(100) NOT NULL,
    session_id char(16) NOT NULL,
    part_list bytes NOT NULL,
    FOREIGN KEY (session_id) REFERENCES peers (session_id) ON DELETE CASCADE
);
