from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from puppies_setup import Base, Shelter, Puppy, Stats
#from flask.ext.sqlalchemy import SQLAlchemy
from random import randint
import datetime
import random, decimal


engine = create_engine('sqlite:///puppyshelter.db')

Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)

session = DBSession()


#Add Shelters
shelter1 = Shelter(name = "Oakland Animal Services", address = "1101 29th Ave", city = "Oakland", state = "CA", zipCode = "94601", website = "http://oaklandanimalservices.org", capacity = 25)
session.add(shelter1)

shelter2 = Shelter(name = "San Francisco SPCA Mission Adoption Center", address="250 Florida St", city="San Francisco", state="CA", zipCode = "94103", website = "http://sfspca.org", capacity = 25)
session.add(shelter2)

shelter3 = Shelter(name = "Wonder Dog Rescue", address= "2926 16th Street", city = "San Francisco", state = "CA" , zipCode = "94103", website = "http://wonderdogrescue.org", capacity = 25)
session.add(shelter3)

shelter4 = Shelter(name = "Humane Society of Alameda", address = "PO Box 1571" ,city = "Alameda" ,state = "CA", zipCode = "94501", website = "http://hsalameda.org", capacity = 25)
session.add(shelter4)

shelter5 = Shelter(name = "Palo Alto Humane Society" ,address = "1149 Chestnut St." ,city = "Menlo Park", state = "CA" ,zipCode = "94025", website = "http://paloaltohumane.org", capacity = 25)
session.add(shelter5)


#Add Puppies and Profiles

male_names = ["Bailey", "Max", "Charlie", "Buddy","Rocky","Jake", "Jack", "Toby", "Cody", "Buster", "Duke", "Cooper", "Riley", "Harley", "Bear", "Tucker", "Murphy", "Lucky", "Oliver", "Sam", "Oscar", "Teddy", "Winston", "Sammy", "Rusty", "Shadow", "Gizmo", "Bentley", "Zeus", "Jackson", "Baxter", "Bandit", "Gus", "Samson", "Milo", "Rudy"]

female_names = ['Bella', 'Lucy', 'Molly', 'Daisy', 'Maggie', 'Sophie', 'Sadie', 'Chloe', 'Bailey', 'Lola', 'Zoe', 'Abby', 'Ginger', 'Roxy', 'Gracie', 'Coco', 'Sasha', 'Lily', 'Angel', 'Princess','Emma', 'Annie', 'Rosie', 'Ruby', 'Lady', 'Missy', 'Lilly', 'Mia', 'Katie', 'Zoey', 'Madison', 'Stella', 'Penny', 'Belle']

puppy_images = ["beagle-puppy-2681__340.jpg", "bordeaux-869032__340.jpg","chihuahua-621112__340.jpg", "chihuahua-624924__340.jpg", "dog-1022329__340.jpg", "dog-1033140__340.jpg", "dog-168815__340.jpg", "dog-187817__340.jpg", "dog-279698__340.jpg", "dog-918625__340.jpg", "dog-992431__340.jpg", "dogue-de-bordeaux-1047522__340.jpg", "french-bulldog-1016912__340.jpg", "labrador-805861__340.jpg", "painting-287403__340.jpg", "puppy-1047722__340.jpg", "puppy-1056124__340.jpg", "none.jpg"]

#This method will make a random age for each puppy between 0-18 months(approx.) old from the day the algorithm was run.
def CreateRandomAge():
	today = datetime.date.today()
	days_old = randint(0,540)
	birthday = today - datetime.timedelta(days = days_old)
	return birthday

#This method will create a random weight between 1.0-40.0 pounds (or whatever unit of measure you prefer)
def CreateRandomWeight():
	x = random.uniform(1.0, 40.0)
	x = decimal.Decimal(str(x))
	decimal.getcontext().prec=2
	x = x*1
	return x

for i,x in enumerate(male_names):
	new_puppy = Puppy(name = x, gender = "male", dateOfBirth = CreateRandomAge(), shelter_id=randint(1,5), weight= CreateRandomWeight())
	session.add(new_puppy)
	session.commit()

for i,x in enumerate(female_names):
	new_puppy = Puppy(name = x, gender = "female", dateOfBirth = CreateRandomAge(), shelter_id=randint(1,5), weight= CreateRandomWeight())
	session.add(new_puppy)
	session.commit()

puppies = session.query(Puppy).all()

p=1

for puppy in puppies:
	puppy_image = Stats(picture=random.choice(puppy_images), puppy_id=puppy.id)
	session.add(puppy_image)
	session.commit()
	p=p+1



