from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from puppies_setup import Base, Shelter, Puppy, Stats, Adopter, PuppyAdopters, User, Admin
engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind = engine
DBSession = sessionmaker (bind = engine)
session = DBSession()

