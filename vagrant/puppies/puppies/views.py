from puppies import app
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, update, delete, asc, func, desc
from sqlalchemy.orm import sessionmaker
from werkzeug import secure_filename
from puppies_setup import Base, Shelter, Puppy, Stats, Adopter, PuppyAdopters, User, Admin
#from flask.ext.sqlalchemy import SQLAlchemy
from .models import Pagination
from forms import NewPuppyForm, TransferForm, DeletePuppyForm, NewShelterForm, DeleteShelterForm, UserForm, AdoptersForm
import datetime, random, bleach, re, os



engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

PUPPIES_PER_PAGE = 12
USERS_PER_PAGE = 12


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
    return render_template ('puppies.html', puppies=puppies, pagination=pagination)


@app.route('/puppies/shelter')
def addToShelter():
    shelter_id=request.args.get('shelter_id', '')
    shelters = session.query(Shelter).all()
    if shelter_id:
        shelter = session.query(Shelter).filter(Shelter.id==shelter_id).one()
        if shelter.occupancy >= shelter.capacity:
            least = session.query(Shelter).order_by(Shelter.occupancy.asc()).first()
            flash ("That shelter is full, please choose another.")
            flash("Shelter "+ str(least.id) + " has the most room.")
            shelter_ID=None
            return render_template('addToShelter.html', shelters=shelters, shelter_id=shelter_id)
        else:
            form = NewPuppyForm()
            return render_template('newPuppy.html', form=form, shelter_id=shelter_id)
    return render_template ('addToShelter.html', shelters=shelters, shelter_id=shelter_id)


@app.route('/puppies/new/<int:shelter_id>/', methods=['GET', 'POST'])
def newPuppy(shelter_id):
    form = NewPuppyForm()
    if form.validate_on_submit():
        newPuppy = Puppy(name=form.name.data, gender=form.gender.data, dateOfBirth=form.dateOfBirth.data, weight=form.weight.data, shelter_id=shelter_id)
        session.add(newPuppy)
        session.flush()
        if form.picture.data:
            filename = secure_filename(form.picture.data.filename)
            filename = str(newPuppy.id) + "_" + filename
            form.picture.data.save(os.path.join(app.config['UPLOAD_FOLDER'] + filename))
        else:
            filename="none.jpg"
        newStats = Stats(needs=form.needs.data, picture=filename, puppy_id=newPuppy.id)
        session.add(newStats)
        session.commit()
        flash ("Your puppy has been successfully added.")
        return redirect(url_for('puppies'))
    else:
        return render_template('newPuppy.html', form=form, shelter_id=shelter_id)


@app.route('/shelters/')
def shelters():
    shelters = session.query(Shelter).all()
    return render_template ('shelters.html', shelters=shelters)


@app.route('/shelters/<int:shelter>/', defaults={'page': 1})
@app.route('/shelters/<int:shelter>/<int:page>/')
def idShelters(shelter, page):
    count = session.query(Puppy).filter_by(shelter_id=shelter).count()
    a=((page-1)*PUPPIES_PER_PAGE)
    b=(page*PUPPIES_PER_PAGE)
    puppies = session.query(Puppy).filter_by(shelter_id=shelter).all()[a:b]
    pagination = Pagination(page, PUPPIES_PER_PAGE, count)
    for puppy in puppies:
        puppy.weight = int(puppy.weight)
    return render_template ('idPuppies.html', puppies=puppies, pagination=pagination, shelter=shelter)


@app.route('/adopt/<int:puppy_id>/', methods=['GET', 'POST'])
def adopt(puppy_id):
    form = AdoptersForm()
    puppy = session.query(Puppy).filter(Puppy.id==puppy_id).one()
    puppy.weight = int(puppy.weight)
    if form.validate_on_submit():
        user_ID = form.userID.data
        try:
            user = session.query(User).filter(User.id==user_ID).one()
            newPuppyAdopter = PuppyAdopters(puppy_id=form.adoptID.data, adopter_id=user_ID)
            session.add(newPuppyAdopter)
            session.query(Puppy).filter(Puppy.id==form.adoptID.data).update({'shelter_id' : '0'})
            session.commit()            
            flash("You successfully adopted your puppy.")
            return redirect(url_for('shelters'))
        except:
            flash("That user does not exist. Please try again.")
            return render_template ('adopt.html', form=form, puppy=puppy)
    else:
        return render_template ('adopt.html', form=form, puppy=puppy)


@app.route('/users/<int:user_ID>/adoptions/', defaults={'page': 1})
@app.route('/users/<int:user_ID>/adoptions/page/<int:page>/')
def adoptions(user_ID, page):
    count = session.query(Adopter).filter(Adopter.id==user_ID).one().adoptions
    a=((page-1)*PUPPIES_PER_PAGE)
    b=(page*PUPPIES_PER_PAGE)
    pagination = Pagination(page, PUPPIES_PER_PAGE, count)
    puppies = session.query(Adopter).filter(Adopter.id==user_ID).one().puppies
    for puppy in puppies:
        puppy.weight = int(puppy.weight)
    user = session.query(User).filter(User.id==user_ID).one()
    return render_template ('adoptedPuppies.html', puppies=puppies, user=user, pagination=pagination)


@app.route('/transfer/<int:puppy_id>', methods=['GET', 'POST'])
def transfer(puppy_id):
    form = TransferForm()
    puppy = session.query(Puppy).filter(Puppy.id==puppy_id).one()
    shelters = session.query(Shelter).filter(Shelter.occupancy<Shelter.capacity, Shelter.id != puppy.shelter_id).all()
    if form.validate_on_submit():
        session.query(Puppy).filter(Puppy.id==puppy_id).update({'shelter_id' : form.newShelter.data})
        session.commit()
        flash("You successfully transferred your puppy.")
        return redirect(url_for('shelters'))
    else:
        return render_template ('transfer.html', form=form, puppy=puppy, shelters=shelters)


@app.route('/editPuppy/<int:puppy_id>/', methods=['GET', 'POST'])
def editPuppy(puppy_id):
    editedPuppy=session.query(Puppy).filter_by(id=puppy_id).one()
    editedPuppy.weight = int(editedPuppy.weight)
    form = NewPuppyForm()
    if form.validate_on_submit():
        session.query(Puppy).filter(Puppy.id == puppy_id).update({'name' : form.name.data, 'gender' : form.gender.data, 'dateOfBirth' : form.dateOfBirth.data, 'weight' : form.weight.data})
        session.flush()
        if form.picture.data:
            filename = secure_filename(form.picture.data.filename)
            filename = str(puppy_id) + "_" + filename
            form.picture.data.save(os.path.join(app.config['UPLOAD_FOLDER'] + filename))
            if form.oldPicture.data and form.oldPicture.data != "none.jpg":
                os.remove(app.config['UPLOAD_FOLDER'] + form.oldPicture.data)
        else:
            filename = form.oldPicture.data           
        session.query(Stats).filter(Stats.puppy_id == puppy_id).update({'needs': form.needs.data, 'picture' : filename})
        session.commit()
        flash("You successfully edited your puppy information.")
        return redirect(url_for('idShelters', shelter=editedPuppy.shelter_id))
    else:
        return render_template('editPuppy.html', form=form, puppy=editedPuppy)

@app.route('/deletePuppy/<int:puppy_id>/', methods=['GET', 'POST'])
def deletePuppy(puppy_id):
    form=DeletePuppyForm()
    deletedPuppy=session.query(Puppy).filter_by(id=puppy_id).one()
    deletedPuppy.weight = int(deletedPuppy.weight)
    if form.validate_on_submit():
        shelter_id = session.query(Puppy).filter_by(id=form.deleteID.data).one().shelter_id
        session.query(Puppy).filter_by(id=form.deleteID.data).delete()
        session.query(Stats).filter_by(puppy_id=form.deleteID.data).delete()
        session.commit()
        if form.deletePicture.data and form.deletePicture.data != "none.jpg":
            os.remove(app.config['UPLOAD_FOLDER'] + form.deletePicture.data)
        flash("You successfully removed your puppy from the database.")
        return redirect(url_for('idShelters', shelter=shelter_id))
    else:
        return render_template('deletePuppy.html', form=form, puppy=deletedPuppy)

@app.route('/shelters/new/', methods=['GET', 'POST'])
def addShelter():
    form=NewShelterForm()
    if form.validate_on_submit():
        newShelter = Shelter(name=form.name.data, address=form.address.data, city=form.city.data, state=form.state.data, zipCode=form.zipcode.data, website=form.website.data, occupancy=form.occupancy.data, capacity=form.capacity.data)
        session.add(newShelter)
        session.commit()
        flash("You successfully added a shelter.")
        return redirect(url_for('shelters'))
    else:
        return render_template('addShelter.html', form=form)


@app.route('/shelters/edit/<int:shelter_id>', methods=['GET', 'POST'])
def editShelter(shelter_id):
    form=NewShelterForm()
    editedShelter = session.query(Shelter).filter_by(id=shelter_id).one()
    if form.validate_on_submit():
        session.query(Shelter).filter(Shelter.id==shelter_id).update({'name' : form.name.data, 'address' : form.address.data, 'city' : form.city.data, 'state' : form.state.data, 'zipCode' : form.zipcode.data, 'website' : form.website.data, 'capacity' :form.capacity.data})
        session.commit()
        flash("Shelter edited successfully!")
        return redirect(url_for('shelters'))
    else:
        return render_template('editShelter.html', form=form, shelter=editedShelter)


@app.route('/shelters/delete/<int:shelter_id>', methods=['GET', 'POST'])
def deleteShelter(shelter_id):
    form=DeleteShelterForm()
    shelterToDelete = session.query(Shelter).filter_by(id=shelter_id).one()
    if form.validate_on_submit(): 
        shelterToDelete.id = form.deleteID.data
        shelterToDelete = session.query(Shelter).filter_by(id=shelterToDelete.id).one()
        if shelterToDelete.occupancy != 0:
            flash("That shelter requires a transfer of its occupants.")  
            return redirect(url_for('shelters'))        
        else:
            session.delete(shelterToDelete)
            session.commit()
            flash("That shelter has been deleted.")
        return redirect(url_for('shelters'))
    else:
        return render_template('deleteShelter.html', form=form, shelter=shelterToDelete)


@app.route('/users/new/', methods=['GET', 'POST'])
def newUser():
    form = UserForm()
    if form.validate_on_submit():
        newUser = User(name=form.name.data, address=form.address.data, city=form.city.data, state=form.state.data, zipcode=form.zipcode.data, phone=form.phone.data, email=form.email.data, password=form.password.data )
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


@app.route('/users/', defaults={'page': 1})
@app.route('/users/page/<int:page>/')
def Users(page):
    count = session.query(User).count()
    a=((page-1)*USERS_PER_PAGE)
    b=(page*USERS_PER_PAGE)
    users = session.query(User).all()[a:b]
    if not users and page !=1:
        abort(404)
    pagination = Pagination(page, USERS_PER_PAGE, count)
    return render_template ('users.html', users=users, pagination=pagination)



# @app.route('/dogsforall/<int:puppy_id>/menu/JSON/')
# def restaurantMenuJSON(restaurant_id):
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     items = session.query(MenuItem).filter_by(
#         restaurant_id=restaurant_id).all()
#     return jsonify(MenuItems=[i.serialize for i in items])


# @app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
# def menuItemJSON(restaurant_id, menu_id):
#     item = session.query(MenuItem).filter_by(
#         id=menu_id).one()
#     return jsonify(MenuItem=item.serialize)        

