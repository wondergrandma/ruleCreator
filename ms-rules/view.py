from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
import gitlab
import config
import json 
from functions import pushFile, showMyFiles, updateFiles, createBranch, getCertainFile, getRulesFromMongo, deletRule

#Definovanie API endpointov, volanie funkcií pod každým, ktorý je definovaný.

app = Flask("GitLabManagerAPI")
api = Api(app)
gl = gitlab.Gitlab(url = config.URL, private_token = config.PRIVATE_TOKEN)

#Konfigurácia CORS suboru (asi pre sfunkčenie API calls z JS suboru)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#---------------  MAIN PART OF CODE ----------------
#Triedenie prichádzajúcich pravidiel do zložiek na GitLabe
class SortRules(Resource):
    def post(self):

        data = request.data
        json_data = json.loads(data)
        
        type = json_data['type']
        type = type.upper()
        text = json_data['data']
        name = json_data['name']
        pub_id = json_data['public_id']

        match type:
            case "RSA":
                stemp = pushFile(type, text, name, pub_id)
                return stemp

            case "QRADAR":
                stemp = pushFile(type, text, name, pub_id)
                return stemp
                
            case "SOLARWINDS":
                stemp = pushFile(type, text, name, pub_id)
                return stemp

            case _:
                stemp = pushFile(type, text, name, pub_id)
                return stemp

class ShowFiles(Resource):
    def post(self):
        data = request.data

        file = showMyFiles(data)

        return file

#Endpoint pre update obsahu existujúceho súboru. 
class Update(Resource):
    def patch(self):
        data = request.data

        update = updateFiles(data)

        return update
    
class OldVersion(Resource):
    def post(self):
        data = request.data

        version = createBranch(data)
        return version

class FileContent(Resource):
    def post(self):
        data = request.data

        content = getCertainFile(data)
        return content
    
class GetMongoHashes(Resource):
    def post(self):
        data = request.data

        content = getRulesFromMongo(data)
        return content
    
class DeleteFile(Resource):
    def post(self):
        data = request.data

        result = deletRule(data)
        return result

#---------------- MAIN RESOURCES ------------------
#definovanie endpointov
api.add_resource(SortRules, '/data')
api.add_resource(ShowFiles, '/show')
api.add_resource(Update, "/update")
api.add_resource(OldVersion, "/old")
api.add_resource(FileContent, "/content")
api.add_resource(GetMongoHashes, "/mongodat")
api.add_resource(DeleteFile, '/delete')

if __name__ == '__main__':
    #Konfigurácia API, url a port
    app.run(host = config.HOST_API_URL_TEST, port = config.HOST_API_PORT_TEST, use_reloader=True)