from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed 
from wtforms import BooleanField, StringField, DateTimeField, TextAreaField, IntegerField, validators, DateField, DecimalField
from wtforms.validators import InputRequired, DataRequired, Length, URL

class NewPuppyForm(Form):
    name        = StringField('Name', validators=[DataRequired()])
    gender      = StringField('Gender', [validators.Length(4, 6)])
    dateOfBirth = DateField('Date of birth (YYYY-MM-DD)', format='%Y-%m-%d')
    weight      = DecimalField('Weight (lbs)', places=2)
    needs       = TextAreaField('Particular needs', [validators.Length(max=500)])
    picture     = FileField('Puppy picture', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    oldPicture  = StringField('Old Picture')
    
class TransferForm(Form):
    newShelter  = IntegerField('Shelter')

class DeletePuppyForm(Form):
    deleteID    = IntegerField('Puppy')
    deletePicture = StringField('Delete Picture')
   
class NewShelterForm(Form):
    name        = StringField('Name', validators=[DataRequired()])
    address     = TextAreaField('Address', [validators.Length(10, 250)])
    city        = StringField('City', [validators.Length(2, 250)])
    state       = StringField('State', [validators.Length(2, 2, message="The state must be 2 letters.")])
    zipcode     = StringField('Zipcode', [validators.Length(5, 5, message="The zipcode must be 5 digits.")])
    website     = StringField('Website', [validators.URL(message="A valid URL is required.")])
    occupancy   = IntegerField('Occupancy')
    capacity    = IntegerField('Capacity', [validators. DataRequired(message="Please enter a number.")])

class DeleteShelterForm(Form):
    deleteID    = IntegerField('Shelter')

class UserForm(Form):
    name        = StringField('Name', validators=[DataRequired()])
    address     = TextAreaField('Address', [validators.Length(10, 250)])
    city        = StringField('City', [validators.Length(2, 250)])
    state       = StringField('State', [validators.Length(2, 2, message="The state must be 2 letters.")])
    zipcode     = StringField('Zipcode', [validators.Length(5, 5, message="The zipcode must be 5 digits.")])    
    phone       = StringField('Phone', [validators.Length(10, 10, message="Please enter 10 digits without spaces or other characters.")])
    email       = StringField('Email Address', [validators.Length(min=6, max=35)])
    password    = StringField('Password', [validators.Length(5, 100, message="Your password must be at least 5 characters long.")])
    #accept_rules = BooleanField('I accept the site rules', [validators.InputRequired()])
    level       = IntegerField('User Level', [validators.NumberRange(min=0, max=2)])
    # level 0   = routine adopter, no privileges
    # level 1   = shelter administrator, can manage shelters but not users
    # level 2   = user administrator, can manage users and shelters

class AdoptersForm(Form):
    adoptID    = IntegerField('Puppy')
    userID     = IntegerField('User')

