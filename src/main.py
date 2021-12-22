"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, make_response
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from functools import wraps
from utils import APIException, generate_sitemap
from admin import setup_admin
from werkzeug.security import generate_password_hash, check_password_hash
from models import (db, ma, User, usersSchema, favoriteSchema, favoritesSchema, planetsSchema, peopleSchema, peoplesSchema, People, Planet, Favorite)
#from models import Person
import uuid
import jwt
import datetime

SECRET_KEY = 'secreteKey'
PREFIX = 'Bearer'

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SECRET_KEY']=SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
ma.init_app(app)
CORS(app)
setup_admin(app)


def get_token(header):
    bearer, _, token = header.partition(' ')

    print(bearer)

    if bearer != PREFIX:
        raise ValueError('Invalid token')

    print(token)

    return token

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None
        if 'Authorization' in request.headers:
            token = get_token(request.headers['Authorization'])

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['public_id']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    return decorator

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/register', methods=['GET', 'POST'])
def signup_user():  
 data = request.get_json()  

 hashed_password = generate_password_hash(data['password'], method='sha256')
 
 new_user = User(email=data['email'], password=hashed_password, is_active=True) 
 db.session.add(new_user)  
 db.session.commit()    

 return jsonify({'message': 'registered successfully'})

@app.route('/login', methods=['POST'])  
def login_user(): 
 
  auth = request.get_json()  
  if not auth or not auth['email'] or not auth['password']:  
     return make_response('missing params', 401, {'WWW.Authentication': 'Basic realm: "login required"'})    

  user = User.query.filter_by(email=auth['email']).first()   
  print(user.password) 
  print(auth['password']) 
     
  if check_password_hash(user.password, auth['password']):  
     token = jwt.encode({'public_id': user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256") 
     print(jsonify(token)) 
     return jsonify({'token' : token}) 

  return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})

@app.route('/users', methods=['GET'])
@token_required
def handle_list_users(current_user):
    all_users = User.query.all()
    users = usersSchema.dump(all_users)

    return jsonify(users), 200

@app.route('/planets', methods=['GET'])
@token_required    
def handle_list_planets(current_user):
    all_planets = Planet.query.all()
    planets = planetsSchema.dump(all_planets)

    return jsonify(planets), 200

@app.route('/planet/<id>', methods=['GET'])
@token_required
def handle_get_planet(current_user, id):
    planet = Planet.query.get(id)
    planets = peopleSchema.dump(planet)

    return jsonify(planets), 200

@app.route('/people', methods=['GET'])
@token_required
def handle_list_people(current_user):
    all_people = People.query.all()
    people = peoplesSchema.dump(all_people)

    return jsonify(people), 200

@app.route('/people/<id>', methods=['GET'])
@token_required
def handle_get_people(current_user, id):
    people = People.query.get(id)
    peoples = peopleSchema.dump(people)

    return jsonify(peoples), 200

@app.route('/users/favorites', methods=['GET'])
@token_required
def handle_list_favorites(current_user):
    all_favorites = Favorite.query.filter( Favorite.user_id == current_user.id )
    favorites = favoritesSchema.dump(all_favorites)

    return jsonify(favorites), 200

@app.route('/favorite/planet/<id>', methods=['DELETE'])
@token_required
def delete_favorite_planet(current_user, id):
  user_id = current_user.id
  favorite = Favorite.query.filter(Favorite.planet_id == id, Favorite.user_id == user_id).delete(), 

  db.session.commit()
  return favoriteSchema.jsonify(favorite)

@app.route('/favorite/people/<id>', methods=['DELETE'])
@token_required
def delete_favorite_people(current_user, id):
  user_id = current_user.id
  favorite = Favorite.query.filter(Favorite.people_id == id, Favorite.user_id == user_id).delete(), 

  db.session.commit()
  return favoriteSchema.jsonify(favorite)

@app.route('/favorite/planet/<id>', methods=['POST'])
@token_required
def add_favorite_planet(current_user, id):
  user_id = current_user.id
  planet_id = id
  people_id = None

  new_favorite = Favorite(planet_id,people_id,user_id);

  db.session.add(new_favorite)
  db.session.commit()

  return favoriteSchema.jsonify(new_favorite)

@app.route('/favorite/people/<id>', methods=['POST'])
@token_required
def add_favorite_people(current_user, id):
  user_id = current_user.id
  planet_id = None
  people_id = id

  new_favorite = Favorite(planet_id,people_id,user_id);

  db.session.add(new_favorite)
  db.session.commit()

  return favoriteSchema.jsonify(new_favorite)

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
