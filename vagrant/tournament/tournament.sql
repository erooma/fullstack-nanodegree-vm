-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- create a database called tournament
CREATE DATABASE tournament;

--connect to the database
\c tournament;

-- create a table of players with serial additions
CREATE TABLE PLAYERS (id SERIAL, name TEXT, no_matches INT DEFAULT 0, wins INT DEFAULT 0, PRIMARY KEY(id));

-- create a table of matches including results
CREATE TABLE MATCHES (round INT, match INT, id_1 INT,id_2 INT, result INT, CONSTRAINT competitors PRIMARY KEY (id_1, id_2, round));