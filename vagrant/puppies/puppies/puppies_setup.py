from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, column_property
from sqlalchemy import create_engine, select, func

Base = declarative_base()

class Stats(Base):
    __tablename__ = 'stats'
    id = Column(Integer, primary_key=True)
    needs = Column(String(500))
    picture = Column(String)
    puppy_id = Column(Integer, ForeignKey('puppy.id'))

class Puppy(Base):
    __tablename__ = 'puppy'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    gender = Column(String(6), nullable = False)
    dateOfBirth = Column(Date)
    weight = Column(Numeric(10))
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
    stats = relationship('Stats', uselist=False, backref='puppy')
    adopters = relationship('Adopter', secondary = 'puppy_adopters')

class Shelter(Base):
    __tablename__ = 'shelter'

    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    address = Column(String(250))
    city = Column(String(80))
    state = Column(String(20))
    zipCode = Column(String(10))
    website = Column(String)
    capacity = Column(Integer)
    occupancy = Column(Integer, default = 0)
    puppy = relationship('Puppy', backref='shelter')
    __table_args__ = (CheckConstraint(capacity >= occupancy, name='check_capacity'),)


class Adopter(Base):
    __tablename__= 'adopter'
    id = Column(Integer, primary_key = True)
    family_name = Column(String(80), nullable = False)
    ## members and names as serialized(array) string using SQLITE
    members = Column(String(250))
    names = Column(String(250))
    puppies = relationship('Puppy', secondary = 'puppy_adopters')

class PuppyAdopters(Base):
    __tablename__ = 'puppy_adopters'
    puppy_id = Column(Integer, ForeignKey('puppy.id'), primary_key=True)
    adopter_id = Column(Integer, ForeignKey('adopter.id'), primary_key=True)


Shelter.occupancy = column_property(
        select([func.count(Puppy.id)]).\
            where(Puppy.shelter_id==Shelter.id)
    )

engine = create_engine('sqlite:///puppyshelter.db')
 

Base.metadata.create_all(engine)