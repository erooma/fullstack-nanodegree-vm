from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed 
from wtforms import BooleanField, StringField, DateTimeField, TextAreaField, IntegerField, validators, DateField, DecimalField
from wtforms.validators import InputRequired, DataRequired, Length, URL, Email

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
    name        = StringField('Name', [InputRequired("Please enter your name.")])
    email       = StringField('Email Address', [InputRequired("Please enter your email address."), Email("This field requires a valid email address")])
    #accept_rules = BooleanField('I accept the site rules', [validators.InputRequired()])
    level       = IntegerField('User Level', [validators.NumberRange(min=0, max=3, message="The user level is 0 (computer), 1(normal), 2(admin), 3(admin+).")])
    # level 0   = computer assigned
    # level 1   = routine adopter, no privileges, can manage own puppies
    # level 2   = shelter administrator, can manage shelters, puppies but not users
    # level 3   = user administrator, can manage users, shelters and puppies

class AdoptersForm(Form):
    adoptID    = IntegerField('Puppy')
    userID     = IntegerField('User')

