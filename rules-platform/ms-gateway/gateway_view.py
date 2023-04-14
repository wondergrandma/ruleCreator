from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import config_gateway
import requests
import database.database_config
from database.create_database import User
import bcrypt
import jwt
import datetime
from functools import wraps
from sqlalchemy.ext.declarative import DeclarativeMeta
import json


#Definovanie API endpointov, volanie funkcií pod každým, ktorý je definovaný.

app = Flask("Gateway")
api = Api(app)
app.config['SECRET_KEY'] = 'shahahaha'

#Konfigurácia CORS suboru (asi pre sfunkčenie API calls z JS suboru)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#Konfigurácia URL adries pre jednotlivé mikroservisy
ms_rule_url = config_gateway.MS_RULE_IP + config_gateway.MS_RULE_PORT
ms_user_url = config_gateway.MS_USER_IP + config_gateway.MS_USER_PORT

#Konfigurácia pripojenia databázy
Base=declarative_base()
Session = sessionmaker()
engine = create_engine(database.database_config.POSTGRE_DIALECT+'+'+database.database_config.POSTGRE_DRIVER+'://'+database.database_config.POSTGRE_USERNAME+':'+database.database_config.POSTGRE_PASSWORD+'@'+database.database_config.POSTGRE_HOST+':'+database.database_config.POSTGRE_PORT+'/'+database.database_config.POSTGRE_DATABASE_NAME, echo = True)

user = User

#Ostatne funkcie potrebne pre fungovanie endpointov
class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)

class MyEncoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__ 


#Vytvorenie dekorátoru ktorý spracuje priložený JWT token a ak je validný vráti usera, ktorý je momentálne prihlásený s tokenom.
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        local_session = Session(bind=engine)

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'message': 'Token is missing!'})
        
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        create_users = local_session.query(User).filter_by(public_id=data['public_id']).first()

        #return jsonify({'message': 'Token is invalid!'}), 401

        return f(create_users, *args, **kwargs)
    
    return decorated

#---------------  MAIN PART OF CODE ----------------
#Zaslanie requestu cez WEB API GATEWAY na backend server a vrátenie odpovede

#Funkcia Loginu s vytvorením JWT tokenu a overením existencie užívateľa
class UserLogin(Resource):
    def get(self):
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response('Could not verify', 404, {'WWW-Authenticate': 'Basic realm="Login required!"'})
        
        local_session = Session(bind=engine)
        user = local_session.query(User).filter_by(email=auth.username).first()

        if not user: 
            return make_response('Could not verify', 404, {'WWW-Authenticate': 'Basic realm="User dos not exist!"'})
        
        if bcrypt.checkpw(auth.password.encode('utf-8'), user.password.encode('utf-8')):
            token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])

            return jsonify({'token': token})
        
        return make_response('Could not verify', 404, {'WWW-Authenticate': 'Basic realm="Wrong password!"'})

#Funkcia umoznujúca tvorbu pravidla
class SortRules(Resource):
    #@token_required
    def post(self):
        #add_pub_id = {'public_id': u.convertDict(str(current_user))}
        data = request.data
        #data.update(add_pub_id)
        #local_session = Session(bind=engine)
        #cu= local_session.query(User).filter_by(public_id=current_user).first()
        
        #json.dumps(current_user, cls=AlchemyEncoder)
        #MyEncoder().encode(current_user)
        #s = json(current_user ,cls=MyEncoder)
        #return current_user

        
        req = requests.post(ms_rule_url + config_gateway.MS_RULES_API_ENDPOINT_DAT, data)
        return req.json()

#Funkcia pre získanie súborov
class ShowFiles(Resource):
    def post(self):
        data = request.data
        req = requests.post(ms_rule_url + config_gateway.MS_RULES_API_ENDPOINT_SHO, data)
        return req.json()

#Funkcia pre upload súborov
class UpdateFiles(Resource):
    def patch(self):
        data = request.data
        req = requests.patch(ms_rule_url + config_gateway.MS_RULES_API_ENDPOINT_UPD, data)
        return req.json()

#Funkcia pre tvorbu užívateľa
class CreateUser(Resource):
    def post(self):
        data = request.data
        req = requests.post(ms_user_url + config_gateway.MS_USER_API_ENDPOINT_CRU, data)
        return req.json()

#Funkcia na získanie starej verzie súboru
class GetOldVersion(Resource):
    def post(self):
        data = request.data
        req = requests.post(ms_rule_url + config_gateway.MS_RULES_API_ENDPOINT_OLD, data)
        print(req)
        print(req.json())
        return req.json()
#---------------- MAIN RESOURCES ------------------

#Definovanie endpointov
api.add_resource(UserLogin, '/v1/login')
api.add_resource(SortRules, '/v1/postRule')
api.add_resource(ShowFiles, '/v1/showFiles')
api.add_resource(UpdateFiles, '/v1/updateFile')
api.add_resource(CreateUser, '/v1/createUser')
api.add_resource(GetOldVersion, '/v1/oldVersion')

if __name__ == '__main__':
    #Konfigurácia API, url a port
    app.run(host = config_gateway.HOST_API_URL_TEST, port = config_gateway.HOST_API_PORT_TEST, use_reloader=True)