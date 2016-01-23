# __init__ file for application 
# AdoptUsDogs - -- implementation of a catalog system
# 23/01/2016 Andrew Moore

from flask import Flask

UPLOAD_FOLDER = 'puppies/static/images/'

app = Flask(__name__)
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from puppies import views


