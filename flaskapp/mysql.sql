-- mysql.sql
DROP TABLE IF EXISTS players;
CREATE TABLE players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    total_balance INTEGER NOT NULL
);

INSERT INTO players (username, total_balance) VALUES ('testuser', 1000);
