## Tournament pairings
11/25/2015 Andrew Moore

These files create a database (called _tournament_) and API for registering players,
deleting players, pairing players and reporting scores in a Swiss-style
matched pairings tournament. There may be an even or odd number of players and players are matched randomly in an initial round, with subsequent pairings based on both wins (and if evenly matched, based on opponent matched wins). Scores may also be reported as ties.

### Build and use the database

Players are added to the database using their names, and each is assigned a unique and serial id. 
By using the algorithm for Swiss Pairing, players are matched amongst one another for the following round. The following tables are used in implementing the tournament:
- _players_, consisting of id, name, number of matches played, wins, ties and losses
- _matches_, consisting of round and match number, and the id's of the paired players (the outcome of each match reports the id of the winner or 0 for a tie)
- _opponentmw_, which keeps track of the OpponentMatchWins of each player

To begin using the database, within psql import the file _tournament.sql_.

`\i tournament.sql`

### Run and organize the tournament

The following functions are used to run and maintain the players and results within the tournament.
- `registerPlayer(name)`
This function adds the name of a new player to the database and assigns a unique id.
- `deletePlayer()` will remove (erase) a player from the tournament.
- `deleteMatches()` will remove all matches from the database.
- `countPlayers()` returns the total number of players registered.
- `playerStandings()` returns the most recent player standings.

Once all players have been registered, the following functions are used for setting up tournament play.
- `swissPairings()` will establish the matches for the next round of play, or if all rounds are completed, will provide the name of the winning player.
- `reportMatch(player1, player2, outcome)` is used to report the outcome of each match, given both player id's and the outcome (the id of the winner, or the value 0 if the match ended in a tie).

### Running test case

The file _tournament_test.py_ tests the integrity and functionality of the database, and includes the following checks:
- ensure that players and matches can be succesfully deleted
- ensures that player are counted and registered correctly
- provides a means for testing player standings
- allows for sample players to be registered, paired and for outcome reporting.

Modifications to the original _tournament_test.py_ file have been incorporated to account for ties - specifically the arguments for reporting match have been modified (see code instructions).

### Known issues

I have including the suggested functionality in tournament_test
to report match outcomes for players, even though they may have not been
previously paired. This is a fault in the tournament_test file, but
could be modified to prevent reporting outcomes until a match is in place.