#
# Database access functions for the web forum.
# 

import time
import psycopg2
import bleach

## Database connection


## Get posts from database.
def GetAllPosts():
    '''Get all the posts from the database, sorted with the newest first.

    Returns:
      A list of dictionaries, where each dictionary has a 'content' key
      pointing to the post content, and 'time' key pointing to the time
      it was posted.
    '''
    DB = psycopg2.connect("dbname=forum")
    c = DB.cursor()
    query = "SELECT content, time FROM posts ORDER BY time DESC"
    c.execute(query)
    allPosts = c.fetchall()

    posts = [{bleach.clean('content'): str(row[1]), 'time': str(row[0])} for row in allPosts]
   # posts.sort(key=lambda row: row['time'], reverse=True)
    
    DB.close()
    return posts

## Add a post to the database.
def AddPost(content):
    '''Add a new post to the database.

    Args:
      content: The text content of the new post.
    '''
    #t = time.strftime('%c', time.localtime())
    #DB.append((t, content))
    
    DB = psycopg2.connect("dbname=forum")
    c=DB.cursor()
    c.execute("INSERT INTO posts (content) VALUES (%s)", (bleach.clean(content),))
    DB.commit()
    DB.close()

    
