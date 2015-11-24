Tournament pairings

These files create a database and API for registering players,
deleting players, pairing players and reporting scores in a Swiss-style
matched pairings tournament. There may be an even or odd number of players
and players are matched randomly in an initial round, with subsequent 
pairings based on both wins (and if evenly matched, based on opponent matched
wins). Scores may be reported as ties.

Modifications to the tournament_test file have been incorporated to
account for ties - specifically the arguments for reporting match have
been modified (see code instructions).

In addition, I have including the suggested functionality in tournament_test
to report match outcomes for players, even though they may have not been 
previously paired. This is perhaps a fault in the tournament_test file, but
could be modified to prevent reporting outcomes until a match is in place.

The files include:
tournament.sql which includes database schema and tables
tournament.py the functions related to match play.
