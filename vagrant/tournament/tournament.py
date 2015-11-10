#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import math
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""

    conn = connect()
    c=conn.cursor()
    query = "DELETE FROM matches;"
    c.execute(query)
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""

    conn = connect()
    c=conn.cursor()
    query = "DELETE FROM players;"
    c.execute(query)
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""

    conn = connect()
    c = conn.cursor()
    query = "SELECT count(*) FROM players;"
    c.execute(query)
    row = c.fetchone()
    count = row[0]
    conn.close()
    return count


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """

    conn = connect()
    c = conn.cursor()
    query = "INSERT INTO players (name, no_matches, wins) VALUES (%s, %s, %s);"
    c.execute(query, [name, 0, 0,])
    conn.commit()
    conn.close()
    

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    conn = connect()
    c = conn.cursor()
    query = "SELECT id, name, wins, no_matches FROM players ORDER BY wins DESC;"
    c.execute(query)
    rows = c.fetchall()
    conn.close()
    return rows


def totalWins():
    """Returns the total number of wins to date in the tournament"""

    conn = connect()
    c = conn.cursor()
    query = "SELECT SUM(wins)FROM players;"
    c.execute(query)
    result = c.fetchone()
    conn.close()
    return result[0]


def checkMatch(player1, player2):
    """Determines if the two players have been previously matched"""

    conn = connect()
    c = conn.cursor()
    query = "SELECT * FROM matches WHERE ((id_1 = %s and id_2= %s) or (id_1 = %s and id_2 = %s));"
    c.execute(query, [player1, player2, player2, player1])
    result = c.fetchall()
    conn.close()
    return result


def checkOne(player1, level):
    """Determines if the player has been scheduled this round/level"""

    conn = connect()
    c = conn.cursor()
    query = "SELECT * FROM matches WHERE ((id_1 = %s or id_2= %s) and (round=%s));"
    c.execute(query, [player1, player1, level])
    result = c.fetchall()
    conn.close()
    return result  


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    
    result = checkMatch(winner, loser)
    if result==[]:
        conn = connect()
        c = conn.cursor()
        query1 = "INSERT INTO matches (round, match, id_1, id_2, result) VALUES (%s, %s, %s, %s, %s);"
        c.execute (query1, [0,0, winner, loser, winner])
    else:
        conn = connect()
        c = conn.cursor()
        query1 = "UPDATE matches SET result=%s WHERE ((id_1 = %s and id_2= %s) or (id_1 = %s and id_2 = %s));"
        c.execute(query1, [winner, winner, loser, loser, winner])
                  
    query2 = "UPDATE players SET wins=(SELECT count(matches.result) FROM matches WHERE result=%s) WHERE id=%s;"
    c.execute(query2, [winner, winner])
    query3 = "UPDATE players SET no_matches=(SELECT SUM(no_matches+1) FROM players WHERE id=%s) WHERE id=%s;"
    c.execute(query3, [winner, winner])
    if loser!=0:
        c.execute(query3, [loser, loser])
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Function prevents rematches between players during a given round.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    count = countPlayers()
    total_wins = totalWins()
    odd_player = count % 2
    total_rounds = int(math.log(count-odd_player,2))
    round_no = int(((total_wins+odd_player+(count/2))/((count/2)+odd_player)))

    if (round_no > total_rounds):
        conn = connect()
        c = conn.cursor()
        query = "SELECT id, name, wins, no_matches FROM players ORDER BY wins DESC LIMIT 1;"
        c.execute(query)
        result = c.fetchone()
        conn.close()
        print "The tournament is finished! The winner is " + str(result[1]) + ", id# " + str(result[0]) + " with " + str(result[2]) + " wins."
        return

    elif (round_no == total_rounds) and (total_wins > (((count/2.0)+odd_player)*(total_rounds-1))):
        print "The last round is currently in play."
        return
                
    elif total_wins != ((count/2)+odd_player)*(round_no-1):
        print "The current round needs to finish before pairing players."
        return

    else:
        matched_players = []
        result = playerStandings()
        x=0
        m=1
        for row in result:
            while checkOne(row[0], round_no)==[]:
                if odd_player==1:
                    bye_player = checkMatch(row[0], 0)
                    bye = checkOne(0, round_no)
                    if bye_player==[] and bye==[]:
                        matched_players.append((row[0], row[1], 0, 'bye'))
                        conn = connect() 
                        c = conn.cursor()
                        query = "INSERT INTO matches (round, match, id_1, id_2, result) VALUES (%s, %s, %s, %s, null);"
                        c.execute(query, [round_no, m, row[0], 0])
                        conn.commit()
                        m=m+1
                        reportMatch(row[0],0)
                if (row[0]!= result[x][0]) and (checkOne(result[x][0], round_no)==[]) and (row[2]==result[x][2]):             
                    matched_players.append((row[0], row[1], result[x][0], result[x][1]))
                    conn = connect() 
                    c = conn.cursor()
                    query = "INSERT INTO matches (round, match, id_1, id_2, result) VALUES (%s, %s, %s, %s, null);"
                    c.execute(query, [round_no, m, row[0], result[x][0]])
                    conn.commit()
                    m=m+1
                else:
                    x=x+1
           
        conn.close()
        return matched_players











        
        
        
        
