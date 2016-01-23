# database setup file for application
# AdoptUsDogs - -- implementation of a catalog system
# 23/01/2016 Andrew Moore

from sqlalchemy import Column, ForeignKey, Integer, String, Date 
from sqlalchemy import create_engine, select, func, Numeric, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, column_property

Base = declarative_base()


# Used for additional puppy information including image and needs
class Stats(Base):
    __tablename__ = 'stats'
    id          = Column(Integer, primary_key=True)
    needs       = Column(String(500), default='None')
    picture     = Column(String)
    puppy_id    = Column(Integer, ForeignKey('puppy.id'), nullable=False)
    puppy       = relationship("Puppy", backref=backref("stats", uselist=False))

# Main puppy class, identifying both users and adopters related to the puppy
class Puppy(Base):
    __tablename__ = 'puppy'
    id          = Column(Integer, primary_key=True)
    name        = Column(String(50), nullable=False)
    gender      = Column(String(6), nullable = False)
    dateOfBirth = Column(Date)
    weight      = Column(Numeric(10))
    shelter_id  = Column(Integer, ForeignKey('shelter.id'))
    user_id     = Column(Integer, ForeignKey('user.id'), default = 0)
    adopters    = relationship('Adopter', secondary = 'puppy_adopters')
    user        = relationship('User')

    @property
    def serialize(self):
    #Returns object data in manageable form for JSON download
    
        return {
            'id'            : self.id,
            'name'          : self.name,
            'gender'        : self.gender,
            'dateOfBirth'   : str(self.dateOfBirth),
            'weight'        : int(self.weight),
            'needs'         : self.stats.needs,
            'picture'       : self.stats.picture,
        }


# Main shelter class, identifying both users and puppies
# Shelter id of '0' refers to puppies that have been adopted
class Shelter(Base):
    __tablename__ = 'shelter'

    id          = Column(Integer, primary_key = True)
    name        = Column(String(80), nullable = False)
    address     = Column(String(250))
    city        = Column(String(80))
    state       = Column(String(2))
    zipCode     = Column(String(5))
    website     = Column(String)
    capacity    = Column(Integer)
    occupancy   = Column(Integer, default = 0)
    user_id     = Column(Integer, ForeignKey('user.id'), default = 0)
    user        = relationship('User')
    puppy       = relationship('Puppy', backref='shelter')
    # Table constraint ensures that occupancy does not exceed capacity
    __table_args__ = (CheckConstraint(capacity >= occupancy, \
        name='check_capacity'),)

    @property
    def serialize(self):
    #Returns object data in manageable form for JSON downlaod

        return {
            'id'            : self.id,
            'name'          : self.name,
            'address'       : self.address,
            'city'          : self.city,
            'state'         : self.state,
            'zipCode'       : self.zipCode,
            'website'       : self.website,
            'capacity'      : self.capacity,
            'occupancy'     : self.occupancy,
        }


# Main adopter class, identifying adopters and their puppies
class Adopter(Base):
    __tablename__= 'adopter'
    id          = Column(Integer, ForeignKey('user.id'), primary_key=True)
    adoptions   = Column(Integer, default = 0)
    puppies     = relationship('Puppy', secondary = 'puppy_adopters')
    user        = relationship("User", backref=backref("adopter", uselist=False))

# Secondary table, referring users to adopters in a many to many relationship
class PuppyAdopters(Base):
    __tablename__ = 'puppy_adopters'
    puppy_id    = Column(Integer, ForeignKey('puppy.id'), primary_key=True)
    adopter_id  = Column(Integer, ForeignKey('adopter.id'), primary_key=True)


# Main user class
class User(Base):
    __tablename__ = 'user'
    id          = Column(Integer, primary_key = True)
    name        = Column(String(80), nullable = False)
    email       = Column(String(250), nullable = False)
    picture     = Column(String(250))


# Main admin class, identifying administration levels for all users
class Admin(Base):
    __tablename__ = 'admin'
    id          = Column(Integer, ForeignKey('user.id'), primary_key = True)
    level       = Column(Integer, primary_key = True)
    user        = relationship("User", backref=backref("admin", uselist=False))        

# Calculates shelter occupancy based on number of puppies per shelter
Shelter.occupancy = column_property(
        select([func.count(Puppy.id)]).\
            where(Puppy.shelter_id==Shelter.id)
    )


# Calculates number of adoptions per user
Adopter.adoptions = column_property(
        select([func.count(PuppyAdopters.puppy_id)]).\
            where(PuppyAdopters.adopter_id==Adopter.id)
    )


engine = create_engine('sqlite:///puppyshelter.db')
 
Base.metadata.create_all(engine)