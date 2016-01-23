# views file for application
# AdoptUsDogs - -- implementation of a catalog system
# 23/01/2016 Andrew Moore

from puppies import app

from flask import render_template, request, jsonify, redirect
from flask import url_for, flash, make_response
from flask import session as login_session
from sqlalchemy import create_engine, update, delete, asc, func, desc
from sqlalchemy.orm import sessionmaker
from werkzeug import secure_filename
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from puppies_setup import Base, Shelter, Puppy, Stats, Adopter, PuppyAdopters 
from puppies_setup import User, Admin
from .models import Pagination
from forms import NewPuppyForm, TransferForm, DeletePuppyForm, NewShelterForm
from forms import DeleteShelterForm, UserForm, AdoptersForm

import datetime, random, string, re, os
import httplib2, json, requests

# Open secrets file for google developer's console
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "AdoptUsDogs"

# Connect to Database and create database session
engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Set paramaters for pagination
PUPPIES_PER_PAGE = 12
USERS_PER_PAGE = 12

# User helper functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.flush()
    newAdmin = Admin(level=1, id=newUser.id)
    session.add(newAdmin)
    session.flush()
    newAdopter = Adopter(id=newUser.id)
    session.add(newAdopter)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('A user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # determine if user exists, and if not, add them
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    admin = session.query(Admin).filter_by(id=user_id).one()
    login_session['admin'] = admin.level

    output = ''
    output += '<h2>Welcome<br /> '
    output += login_session['username']
    output += '!</h2>'
    flash("You are now logged in as %s." % login_session['username'])
    return output


# Disconnect - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke current token.
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['credentials'] 
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['admin']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("You have been successfully logged out.")
        return redirect(url_for('puppies'))
    else:
        response = make_response(json.dumps('Failed to revoke token for user.',
            400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Set routing for splashpage
@app.route('/', defaults={'page': 1})
@app.route('/puppies/', defaults={'page': 1})
@app.route('/puppies/page/<int:page>/')
def puppies(page):
    count = session.query(Puppy).count()
    a=((page-1)*PUPPIES_PER_PAGE)
    b=(page*PUPPIES_PER_PAGE)
    puppies = session.query(Puppy).all()[a:b]
    if not puppies and page !=1:
        abort(404)
    pagination = Pagination(page, PUPPIES_PER_PAGE, count)
    for puppy in puppies:
        puppy.weight = int(puppy.weight)
    return render_template ('puppies.html', puppies=puppies, 
        pagination=pagination, login_session=login_session)


# Set routing for choosing a shelter
@app.route('/puppies/shelter')
def addToShelter():
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    shelter_id=request.args.get('shelter_id', '')
    shelters = session.query(Shelter).all()
    if shelter_id:
        shelter = session.query(Shelter).filter(Shelter.id==shelter_id).one()
        if shelter.occupancy >= shelter.capacity:
            least = session.query(Shelter).order_by(Shelter.occupancy.asc()).\
                first()
            flash ("That shelter is full, please choose another.")
            flash("Shelter "+ str(least.id) + " has the most room.")
            shelter_ID=None
            return render_template('addToShelter.html', shelters=shelters, 
                shelter_id=shelter_id)
        else:
            form = NewPuppyForm()
            return render_template('newPuppy.html', form=form, 
                shelter_id=shelter_id)
    return render_template ('addToShelter.html', shelters=shelters, 
        shelter_id=shelter_id)


# Set routing for adding a puppy to a shelter including secure image upload
@app.route('/puppies/new/<int:shelter_id>/', methods=['GET', 'POST'])
def newPuppy(shelter_id):
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    form = NewPuppyForm()
    if form.validate_on_submit():
        newPuppy = Puppy(name=form.name.data, gender=form.gender.data,
            dateOfBirth=form.dateOfBirth.data, weight=form.weight.data,
            shelter_id=shelter_id, user_id=login_session['user_id'])
        session.add(newPuppy)
        session.flush()
        # Allows for secure image viewing and upload
        if form.picture.data:
            filename = secure_filename(form.picture.data.filename)
            filename = str(newPuppy.id) + "_" + filename
            form.picture.data.save(os.path.join(app.config['UPLOAD_FOLDER']\
             + filename))
        # If no image available, generic image is used
        else:
            filename="none.jpg"
        newStats = Stats(needs=form.needs.data, picture=filename,
            puppy_id=newPuppy.id)
        session.add(newStats)
        session.commit()
        flash ("Your puppy has been successfully added.")
        return redirect(url_for('puppies'))
    else:
        return render_template('newPuppy.html', form=form,
            shelter_id=shelter_id)


# Set routing for modifying shelters (admin restricted)
@app.route('/shelters/')
def shelters():
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    if login_session['admin'] < 2 :
        flash ("You do not have the authority to access that page.")
        return redirect ('/puppies')
    shelters = session.query(Shelter).all()
    return render_template ('shelters.html', shelters=shelters,
        login_session=login_session)


# Set routing for viewing puppies in a given shelter
@app.route('/puppies_by_shelter/')
def puppiesByShelter():
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    shelters = session.query(Shelter).all()
    return render_template ('puppies_by_shelter.html',\
        shelters=shelters, login_session=login_session)


# Set routing for viewing puppies in a given shelter
@app.route('/shelters/<int:shelter>/', defaults={'page': 1})
@app.route('/shelters/<int:shelter>/<int:page>/')
def idShelters(shelter, page):
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    count = session.query(Puppy).filter_by(shelter_id=shelter).count()
    a=((page-1)*PUPPIES_PER_PAGE)
    b=(page*PUPPIES_PER_PAGE)
    puppies = session.query(Puppy).filter_by(shelter_id=shelter).all()[a:b]
    pagination = Pagination(page, PUPPIES_PER_PAGE, count)
    for puppy in puppies:
        puppy.weight = int(puppy.weight)
    user_id = getUserID(login_session['email'])
    return render_template ('idPuppies.html', puppies=puppies,\
        pagination=pagination, shelter=shelter, admin=login_session['admin'],\
        user_id=user_id)


# Set routing for adopting a puppy
@app.route('/adopt/<int:puppy_id>/', methods=['GET', 'POST'])
def adopt(puppy_id):
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    form = AdoptersForm()
    puppy = session.query(Puppy).filter(Puppy.id==puppy_id).one()
    puppy.weight = int(puppy.weight)
    if form.validate_on_submit():
        user_id = getUserID(login_session['email'])
        user = session.query(User).filter(User.id==user_id).one()
        newPuppyAdopter = PuppyAdopters(puppy_id=form.adoptID.data,\
            adopter_id=user_id)
        session.add(newPuppyAdopter)
        session.query(Puppy).filter(Puppy.id==form.adoptID.data).\
            update({'shelter_id' : '0'})
        session.commit()            
        flash("You successfully adopted your puppy.")
        return redirect(url_for('puppies'))
    else:
        return render_template ('adopt.html', form=form, puppy=puppy)


# Set routing for users (or administrators) to view adopted puppies
@app.route('/users/<int:user_ID>/adoptions/', defaults={'page': 1})
@app.route('/users/<int:user_ID>/adoptions/page/<int:page>/')
def adoptions(user_ID, page):
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    if login_session['admin'] < 2 and login_session['user_id'] != user_ID:
        flash ("You do not have the authority to access that page.")
        return redirect ('/puppies')
    count = session.query(Adopter).filter(Adopter.id==user_ID).one().adoptions
    a=((page-1)*PUPPIES_PER_PAGE)
    b=(page*PUPPIES_PER_PAGE)
    pagination = Pagination(page, PUPPIES_PER_PAGE, count)
    puppies = session.query(Adopter).filter(Adopter.id==user_ID).one().puppies
    for puppy in puppies:
        puppy.weight = int(puppy.weight)
    user = session.query(User).filter(User.id==user_ID).one()
    return render_template ('adoptedPuppies.html', puppies=puppies,\
        user=user, pagination=pagination)


# Set routing for transferring puppies between shelters (admin restricted)
@app.route('/transfer/<int:puppy_id>', methods=['GET', 'POST'])
def transfer(puppy_id):
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    puppy = session.query(Puppy).filter(Puppy.id==puppy_id).one()
    if login_session['admin'] < 2 and puppy.user_id != login_session['user_id']:
        flash ("You do not have the authority to access that page.")
        return redirect ('/puppies')
    form = TransferForm()
    shelters = session.query(Shelter).filter(Shelter.occupancy<Shelter.capacity\
        , Shelter.id != puppy.shelter_id).all()
    if form.validate_on_submit():
        session.query(Puppy).filter(Puppy.id==puppy_id).update({'shelter_id' :\
            form.newShelter.data})
        session.commit()
        flash("You successfully transferred your puppy.")
        return redirect(url_for('shelters'))
    else:
        return render_template ('transfer.html', form=form, puppy=puppy,\
            shelters=shelters)


# Set routing for editing puppies including images (user or admin restricted) 
@app.route('/editPuppy/<int:puppy_id>/', methods=['GET', 'POST'])
def editPuppy(puppy_id):
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    editedPuppy=session.query(Puppy).filter_by(id=puppy_id).one()
    if login_session['admin'] < 2 and editedPuppy.user_id != \
        login_session['user_id'] :
        flash ("You do not have the authority to access that page.")
        return redirect ('/puppies')
    editedPuppy.weight = int(editedPuppy.weight)
    form = NewPuppyForm()
    if form.validate_on_submit():
        session.query(Puppy).filter(Puppy.id == puppy_id).update({'name' : \
            form.name.data, 'gender' : form.gender.data, 'dateOfBirth' : \
            form.dateOfBirth.data, 'weight' : form.weight.data, 'user_id' : \
            login_session['user_id']})
        session.flush()
        # Allows for secure image viewing and upload
        # Deletes old image from storage
        if form.picture.data:
            filename = secure_filename(form.picture.data.filename)
            filename = str(puppy_id) + "_" + filename
            form.picture.data.save(os.path.join(app.config['UPLOAD_FOLDER'] +\
                filename))
            if form.oldPicture.data and form.oldPicture.data[0].isdigit():
                os.remove(app.config['UPLOAD_FOLDER'] + form.oldPicture.data)
        # If no image is available, uses a generic image
        else:
            filename = form.oldPicture.data        
        session.query(Stats).filter(Stats.puppy_id == puppy_id).update\
            ({'needs': form.needs.data, 'picture' : filename})
        session.commit()
        flash ("You successfully edited your puppy information.")
        return redirect(url_for('idShelters', shelter=editedPuppy.shelter_id))
    else:
        return render_template('editPuppy.html', form=form, puppy=editedPuppy)


# Set routing for deleting puppies from a shelter (user or admin restricted)
@app.route('/deletePuppy/<int:puppy_id>/', methods=['GET', 'POST'])
def deletePuppy(puppy_id):
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    deletedPuppy=session.query(Puppy).filter_by(id=puppy_id).one()
    if login_session['admin'] < 2 and deletedPuppy.user_id != \
        login_session['user_id'] :
        flash ("You do not have the authority to access that page.")
        return redirect ('/puppies')
    form=DeletePuppyForm()
    deletedPuppy.weight = int(deletedPuppy.weight)
    if form.validate_on_submit():
        shelter_id = session.query(Puppy).filter_by(id=form.deleteID.data).\
            one().shelter_id
        session.query(Puppy).filter_by(id=form.deleteID.data).delete()
        session.query(Stats).filter_by(puppy_id=form.deleteID.data).delete()
        session.commit()
        if form.deletePicture.data and form.deletePicture.data[0].isdigit():
            os.remove(app.config['UPLOAD_FOLDER'] + form.deletePicture.data)
        flash("You successfully removed your puppy from the database.")
        return redirect(url_for('idShelters', shelter=shelter_id))
    else:
        return render_template('deletePuppy.html', form=form,\
            puppy=deletedPuppy)


# Set routing for adding a shelter to the database (admin restricted)
@app.route('/shelters/new/', methods=['GET', 'POST'])
def addShelter():
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    if login_session['admin'] < 2:
        flash ("You do not have the authority to access that page.")
        return redirect ('/puppies')
    form=NewShelterForm()
    if form.validate_on_submit():
        newShelter = Shelter(name=form.name.data, address=form.address.data,\
            city=form.city.data, state=form.state.data, \
            zipCode=form.zipcode.data, website=form.website.data, \
            occupancy=form.occupancy.data, capacity=form.capacity.data, \
            user_id=login_session['user_id'])
        session.add(newShelter)
        session.commit()
        flash("You successfully added a shelter.")
        return redirect(url_for('shelters'))
    else:
        return render_template('addShelter.html', form=form)


# Set routing for editing a shelter in the database (admin restricted)
@app.route('/shelters/edit/<int:shelter_id>', methods=['GET', 'POST'])
def editShelter(shelter_id):
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    if login_session['admin'] < 2:
        flash ("You do not have the authority to access that page.")
        return redirect ('/puppies')
    form=NewShelterForm()
    editedShelter = session.query(Shelter).filter_by(id=shelter_id).one()
    if form.validate_on_submit():
        session.query(Shelter).filter(Shelter.id==shelter_id).update({'name' :\
            form.name.data, 'address' : form.address.data, 'city' : \
            form.city.data, 'state' : form.state.data, 'zipCode' : \
            form.zipcode.data, 'website' : form.website.data, 'capacity' :\
            form.capacity.data, 'user_id' : login_session['user_id']})
        session.commit()
        flash("Shelter edited successfully!")
        return redirect(url_for('shelters'))
    else:
        return render_template('editShelter.html', form=form,\
            shelter=editedShelter)


# Set routing for deleting a shelter in the database (admin restricted)
@app.route('/shelters/delete/<int:shelter_id>', methods=['GET', 'POST'])
def deleteShelter(shelter_id):
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    if login_session['admin'] < 2:
        flash ("You do not have the authority to access that page.")
        return redirect ('/puppies')
    form=DeleteShelterForm()
    shelterToDelete = session.query(Shelter).filter_by(id=shelter_id).one()
    if form.validate_on_submit(): 
        shelterToDelete.id = form.deleteID.data
        shelterToDelete = session.query(Shelter).filter_by\
            (id=shelterToDelete.id).one()
        if shelterToDelete.occupancy != 0:
            flash("That shelter requires a transfer of its occupants.")  
            return redirect(url_for('shelters'))        
        else:
            session.delete(shelterToDelete)
            session.commit()
            flash("That shelter has been deleted.")
        return redirect(url_for('shelters'))
    else:
        return render_template('deleteShelter.html', form=form,\
            shelter=shelterToDelete)


# Set routing for adding a new user to the database (admin restricted)
# This is a beta feature for administrators (not fully implemented)
@app.route('/users/new/', methods=['GET', 'POST'])
def newUser():
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    if login_session['admin'] < 3:
        flash ("You do not have the authority to access that page.")
        return redirect ('/puppies')
    form = UserForm()
    if form.validate_on_submit():
        newUser = User(name=form.name.data, email=form.email.data)
        session.add(newUser)
        session.flush()
        newAdmin = Admin(level=form.level.data, id=newUser.id)
        session.add(newAdmin)
        session.flush()
        newAdopter = Adopter(id=newUser.id)
        session.add(newAdopter)
        session.commit()
        flash ("You have added " + newUser.email + " as a new user.")
        return redirect(url_for('puppies'))
    else:
        return render_template('newUser.html', form=form)


''' Set routing for a user changes his administrator privileges
    This is only for the submission version for evaluation purposes.
    User levels grant the following access privilegs:
        level 0 = computer assigned (default)
        level 1 = routine adopter - no privileges, can manage own puppies
        level 2 = shelter administrator - manage shelters, puppies but not users
        level 3 = user administrator - manage users, shelters and puppies
'''

@app.route('/admin/<int:level>/')
def changeAdmin(level):
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    login_session['admin'] = level
    flash ("Your admin level has been temporarily set to " + str(level) +".")
    return redirect ('/puppies')


# Set routing for viewing the users in the database (admin restricted)
@app.route('/users/', defaults={'page': 1})
@app.route('/users/page/<int:page>/')
def users(page):
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    if login_session['admin'] < 3:
        flash ("You do not have the authority to access that page.")
        return redirect ('/puppies')
    count = session.query(User).count()
    a=((page-1)*USERS_PER_PAGE)
    b=(page*USERS_PER_PAGE)
    users = session.query(User).all()[a:b]
    if not users and page !=1:
        abort(404)
    pagination = Pagination(page, USERS_PER_PAGE, count)
    return render_template ('users.html', users=users, pagination=pagination,\
        login_session=login_session)


# Set initial routing for viewing shelter and puppy information as JSON/XML data
@app.route('/sheltersInfo')
def sheltersInfo():
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    shelters = session.query(Shelter).all()
    return render_template ('sheltersInfo.html', shelters=shelters,\
        login_session=login_session)


# Set routing for viewing puppy information as JSON data
@app.route('/shelters/<int:shelter_id>/JSON/')
def puppyJSON(shelter_id):
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    puppies = session.query(Puppy).filter_by(shelter_id=shelter_id).all()
    return jsonify(Puppies=[puppy.serialize for puppy in puppies])
 

# Set routing for viewing shelter information as JSON data
@app.route('/allShelters/JSON/')
def shelterJSON():
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    shelters = session.query(Shelter).all()
    return jsonify(Shelters=[i.serialize for i in shelters])


# Set routing for viewing puppy information as XML data
@app.route('/shelter/<int:shelter_id>/XML/')
def puppyXML(shelter_id):
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    puppies = session.query(Puppy).filter_by(shelter_id=shelter_id).all()
    for puppy in puppies:
        puppy.weight = int(puppy.weight)
    result = make_response(render_template('puppies_xml.html', puppies=puppies))
    result.headers['Content-type'] = 'text/xml; charset=utf-8'
    return result


# Set routing for viewing shelter information as XML data
@app.route('/allShelters/XML/')
def shelterXML():
    if 'username' not in login_session:
        flash ("Please login for more complete access to our puppies.")
        return redirect ('/puppies')
    shelters = session.query(Shelter).all()
    result = make_response(render_template('shelters_xml.html',\
        shelters=shelters))
    result.headers['Content-type'] = 'text/xml; charset=utf-8'
    return result