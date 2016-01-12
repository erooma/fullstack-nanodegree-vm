import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def asking():
    print "Any more to add?",
    answer = raw_input ()
    if (answer == "y"):
        addPlayers()
    else:
        print "ok"
        exit()
        
def addPlayers():
    print "Add the player stats (id, 'name', matches, wins): ", 
    response = raw_input()
        
    conn = connect()
    c=conn.cursor()
    query = "INSERT INTO players VALUES (" + response + ");"
    c.execute(query)
    conn.commit()
    conn.close()
    asking()
    

addPlayers()

    
