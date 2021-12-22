from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import json

db = SQLAlchemy()
ma = Marshmallow()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    
    def __init__(self, email, password, is_active):
       self.email = email
       self.password = password
       self.is_active = is_active

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            # do not serialize the password, its a security breach
        }


class Planet(db.Model):
    __tablename__ = 'planet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    population = db.Column(db.String(100), unique=False, nullable=False)
    climate = db.Column(db.String(100), unique=False, nullable=False)

    def __init__(self, name, population, climate):
       self.name = name
       self.population = population
       self.climate = climate

    def __repr__(self):
        return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "climate": self.climate,
        }

class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    height = db.Column(db.String(100), unique=False, nullable=True)
    species = db.Column(db.String(150), unique=False, nullable=True)
    homeworld = db.Column(db.String(150), unique=False, nullable=True)

    def __init__(self, name, height, species, homeworld):
       self.name = name
       self.height = height
       self.species = species
       self.homeworld = homeworld

    def __repr__(self):
        return '<People %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "species": self.species,
            "homeworld": self.homeworld,
        }


class PlanetSchema(ma.Schema):
    class Meta:
            fields = ('id', 'name','population','climate')

planetSchema = PlanetSchema()
planetsSchema = PlanetSchema( many = True)


class UserSchema(ma.Schema):
    class Meta:
            fields = ('id', 'email', 'is_active')

userSchema = UserSchema()
usersSchema = UserSchema( many = True)



class PeopleSchema(ma.Schema):
    class Meta:
            fields = ('id','name','height','species','homeworld')

peopleSchema = PeopleSchema()
peoplesSchema = PeopleSchema( many = True)

class Favorite(db.Model):
    __tablename__ = 'favorite'
    id = db.Column(db.Integer, primary_key=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=True)
    planet = db.relationship("Planet", backref=db.backref("planet", uselist=False))
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=True)
    people = db.relationship("People", backref=db.backref("people", uselist=False))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", backref=db.backref("user", uselist=False))

    def __repr__(self):
        return '<Favorite %r>' % self.user_id

    def __init__(self, planet_id, people_id, user_id):
       self.planet_id = planet_id
       self.people_id = people_id
       self.user_id = user_id

    def serialize(self):
        return {
            "id": self.id,
            "planet_id": self.planet_id,
            "people_id": self.people_id,
            "user_id": self.user_id,
        }

class FavoriteSchema(ma.Schema):
    class Meta:
            fields = ('id','planet_id','people_id','user_id')

favoriteSchema = FavoriteSchema()
favoritesSchema = FavoriteSchema( many = True)