#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
# 11/25/2015 Andrew Moore

import psycopg2
import math
import bleach


def connect(database_name="tournament"):
    """Connect to the PostgreSQL database.  
    Returns a database connection and cursor if no exception.
    """

    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print("<error message>")


def deleteMatches():
    """Remove all the match records from the database."""

    db, cursor = connect()
    query1 = "DELETE FROM matches;"
    cursor.execute(query1)
    query2 = "DELETE FROM opponentmw;"
    cursor.execute(query2)
    query3 = "UPDATE players SET no_matches=0, wins=0, losses=0, ties=0;"
    cursor.execute(query3)
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""

    db, cursor = connect()
    query1 = "DELETE FROM opponentmw;"
    cursor.execute(query1)
    query2 = "DELETE FROM players;"
    cursor.execute(query2)   
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""

    db, cursor = connect()
    query = "SELECT count(*) FROM players;"
    cursor.execute(query)
    row = cursor.fetchone()
    count = row[0]
    db.close()
    return count


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    
    name = bleach.clean(name)
    db, cursor = connect()
    query1 = """
           INSERT INTO players (name) VALUES (%s);
             """
    cursor.execute(query1, [name])
    db.commit()
    query2 = """
           INSERT INTO opponentmw (id) VALUES ((SELECT id FROM players
           WHERE name=%s));"""
    cursor.execute(query2, [name])
    db.commit()
    db.close()
    

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a 
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    db, cursor = connect()
    query = "SELECT * FROM standings;"
    cursor.execute(query)
    rows = cursor.fetchall()
    db.close()
    return rows


def totalWins():
    """Returns the total number of wins to date in the tournament"""

    db, cursor = connect()
    query = "SELECT SUM(wins)FROM players;"
    cursor.execute(query)
    result = cursor.fetchone()
    db.close()
    return result[0]


def opponentMatchWins(player):
    """Returns the OMW score for each player (the total number of wins by 
    players they have played
    against).

    Args:
      the player-id
    """
    
    player = bleach.clean(player)
    db, cursor = connect()
    query = """
          SELECT SUM(players.wins) FROM players, matches WHERE 
          (matches.id_1=%s and players.id=matches.id_2) or 
          (matches.id_2=%s and players.id=matches.id_1);"""
    cursor.execute(query, [player, player])
    result = cursor.fetchone()
    db.close()
    return result[0]


def totalMatches():
    """Returns the total number of matches played in the tournament
    (counted twice per participant and including single 'bye's.)"""

    db, cursor = connect()
    query = "SELECT SUM(no_matches) FROM players;"
    cursor.execute(query)
    result = cursor.fetchone()
    db.close()
    return result[0]


def checkMatch(player1, player2):
    """Determines if the two players have been previously matched"""
    
    player1 = bleach.clean(player1)
    player2 = bleach.clean(player2)
    db, cursor = connect()
    query = """
          SELECT * FROM matches WHERE (id_1 = %s and id_2= %s) or (id_1 = %s
          and id_2 = %s);"""
    cursor.execute(query, [player1, player2, player2, player1])
    result = cursor.fetchall()
    db.close()
    return result


def checkOne(player1, level):
    """Determines if the player has been scheduled this round/level"""

    player1 = bleach.clean(player1)
    level = bleach.clean(level)
    db, cursor = connect()
    query = """
          SELECT * FROM matches WHERE (id_1 = %s or id_2 = %s) 
          and (round = %s);"""
    cursor.execute(query, [player1, player1, level])
    result = cursor.fetchall()
    db.close()
    return result  


def reportMatch(player1, player2, outcome):
    """Records the outcome of a single match between two players and updates
    all tables.

    Args:
      player1:  the id number of the first player
      player2:  the id number of the second player
      (note that the player id's can be in any order)
      A player id of 0 represents a 'bye' round.
      outcome: the id number of the winner of the round OR a 0 if the round 
      ended in a tie
    """

    player1 = bleach.clean(player1)
    player2 = bleach.clean(player2)
    outcome = bleach.clean(outcome)
    if player1 == outcome:
        winner = player1
        loser = player2
    else:
        winner = player2
        loser = player1    
    result = checkMatch(player1, player2)
    db, cursor = connect()
    if result == []:
        query1 = """
               INSERT INTO matches (round, match, id_1, id_2, result) VALUES
               (%s, %s, %s, %s, %s);"""
        cursor.execute (query1, [0,0, player1, player2, outcome])
    else:
        query1 = """
               UPDATE matches SET id_1=%s, id_2=%s, result=%s WHERE 
               (id_1 = %s and id_2= %s) or (id_1 = %s and id_2 = %s);"""
        cursor.execute(query1, [player1, player2, outcome, player1, player2,
                  player2, player1])
    db.commit()
    db.close()
    
     
    if outcome != 0:
        db, cursor = connect()
        query2 = "UPDATE players SET wins=wins+1 WHERE id=%s;"
        cursor.execute(query2, [outcome])
        query3 = "UPDATE players SET no_matches=no_matches+1 WHERE id=%s;"
        cursor.execute(query3, [outcome])
        db.commit()
        db.close()
        if loser !=0:
            db, cursor = connect()
            cursor.execute(query3, [loser])
            query4 = "UPDATE players SET losses=losses+1 WHERE id=%s;"
            cursor.execute(query4, [loser])
            w_omw = opponentMatchWins(winner)
            l_omw = opponentMatchWins(loser)
            query5 = "UPDATE opponentmw SET omw=%s WHERE id=%s;"
            cursor.execute(query5, [w_omw, winner])
            cursor.execute(query5, [l_omw, loser])
            db.commit()
            db.close()
    else:
        db, cursor = connect()
        query6 = "UPDATE players SET ties=ties+1 WHERE id=%s or id=%s;"
        cursor.execute(query6, [player1, player2])
        query7 = """
               UPDATE players SET no_matches=no_matches+1 WHERE id=%s or 
               id=%s;"""
        cursor.execute(query7, [player1, player2])
        db.commit()
        db.close()
    

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  If there is an odd number of players
    then an odd player is assigned a 'bye' only once per tournament.
    A 'bye' is reported as an id of 0, with name 'bye'.
    
    Each player is paired with another player with an equal or nearly-equal
    win record, that is, a player adjacent to him or her in the standings. If
    players have equal wins, they are rated by Opponent Match Wins.
    
    For the first round, players are matched randomly.

    Function prevents rematches between players during a given round.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    count = countPlayers()
    odd_player = count % 2
    adjust = count-odd_player
    total_matches = totalMatches()
    matches_count = (total_matches + (total_matches*odd_player)/count)/2
    total_rounds = int(math.log(adjust,2))
    round_no = int(total_matches/count) + 1

    if round_no > total_rounds:
        result = playerStandings()
        print """
              The tournament is finished! The winner is " + str(result[0][1])
               + ", id# " + str(result[0][0]) + " with " + str(result[0][2])
               + " wins."""
        return

    elif (round_no == total_rounds) and (matches_count != 
         ((adjust/2)+odd_player)*(round_no-1)):
        print "The last round is currently in play."
        return
                
    elif matches_count != ((adjust/2)+odd_player)*(round_no-1):
        print "The current round needs to finish before pairing players."
        return

    else:
        matched_players = []
        if round_no != 1:
            result = playerStandings()
        else:
            db, cursor = connect()
            query = """
                  SELECT id, name, wins, no_matches FROM players ORDER BY 
                  RANDOM() LIMIT " + str(count) + ";"""
            cursor.execute(query)
            result = cursor.fetchall()
            db.close()
        x=0
        m=1
        for row in result:
            while checkOne(row[0], round_no) == []:
                if odd_player == 1:
                    bye_player = checkMatch(row[0], 0)
                    bye = checkOne(0, round_no)
                    if bye_player == [] and bye == []:
                        matched_players.append((row[0], row[1], 0, 'bye'))
                        db, cursor = connect()
                        query = """
                              INSERT INTO matches (round, match, id_1, id_2,
                              result) VALUES (%s, %s, %s, %s, null);"""
                        cursor.execute(query, [round_no, m, row[0], 0])
                        db.commit()
                        db.close()
                        m = m+1
                        reportMatch(row[0], 0, row[0])
                if (row[0] != result[x][0]) and (checkOne(result[x][0], 
                        round_no) == []):             
                    matched_players.append((row[0], row[1], result[x][0], 
                        result[x][1]))
                    db, cursor = connect()
                    query = """
                          INSERT INTO matches (round, match, id_1, id_2, 
                          result) VALUES (%s, %s, %s, %s, null);"""
                    cursor.execute(query, [round_no, m, row[0], result[x][0]])
                    db.commit()
                    db.close()
                    m = m+1
                else:
                    x = x+1    
        return matched_players