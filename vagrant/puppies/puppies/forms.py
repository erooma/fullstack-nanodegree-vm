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

class RegistrationForm(Form):
    username     = StringField('Username', [validators.Length(min=4, max=25)])
    email        = StringField('Email Address', [validators.Length(min=6, max=35)])
    accept_rules = BooleanField('I accept the site rules', [validators.InputRequired()])

class ProfileForm(Form):
    birthday  = DateTimeField('Your Birthday', format='%m/%d/%y')
    signature = TextAreaField('Forum Signature')

class AdminProfileForm(ProfileForm):
    username = StringField('Username', [validators.Length(max=40)])
    level    = IntegerField('User Level', [validators.NumberRange(min=0, max=10)])