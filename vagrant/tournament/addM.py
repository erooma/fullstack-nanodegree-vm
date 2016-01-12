import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def asking():
    print "Any more to add?",
    answer = raw_input ()
    if (answer == "y"):
        addMatches()
    else:
        print "ok"
        exit()
        
def addMatches():
    print "Add the matches stats (round, match, id_1, id_2, result): ", 
    response = raw_input()
        
    conn = connect()
    c=conn.cursor()
    query = "INSERT INTO matches VALUES (" + response + ");"
    c.execute(query)
    conn.commit()
    conn.close()
    asking()
    

addMatches()

    
