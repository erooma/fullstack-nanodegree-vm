from flask import Flask

UPLOAD_FOLDER = 'puppies/static/images/'

app = Flask(__name__)
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

from puppies import views


