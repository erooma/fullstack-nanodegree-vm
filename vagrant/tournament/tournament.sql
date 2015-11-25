-- Table and view definitions for the tournament project
-- 25/11/2015 Andrew Moore

-- remove any duplicate database
DROP DATABASE IF EXISTS tournament;

-- create a database called tournament
CREATE DATABASE tournament;

--connect to the database
\c tournament;

-- create a table of players with serial additions
CREATE TABLE players (
	id SERIAL,
	name TEXT NOT NULL, 
	no_matches INT DEFAULT 0, 
	wins INT DEFAULT 0, 
	losses INT DEFAULT 0, 
	ties INT DEFAULT 0, 
	PRIMARY KEY(id)
	);

-- create a table of matches including results
CREATE TABLE matches (
	round INT, 
	match INT, 
	id_1 INT REFERENCES players(id) ON DELETE CASCADE,
	id_2 INT REFERENCES players(id) ON DELETE CASCADE, 
	result INT, 
	CHECK (id_1 <> id_2),
	CONSTRAINT competitors PRIMARY KEY (id_1, id_2, round)
	);

CREATE TABLE opponentMW (
	id INT REFERENCES players(id), 
	omw INT DEFAULT 0, PRIMARY KEY(id)
	);

CREATE VIEW standings AS
    SELECT players.id, name, wins, no_matches FROM players, opponentmw
    WHERE opponentmw.id = players.id ORDER BY wins DESC, omw DESC;