from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
import gitlab
import config_user
import _thread
import schedule
import time
from functions_user import create, renewAllTokens

#Definovanie API endpointov, volanie funkcií pod každým, ktorý je definovaný.

app = Flask("UserManager")
api = Api(app)
gl = gitlab.Gitlab(url = config_user.URL, private_token = config_user.PRIVATE_TOKEN)

#Konfigurácia CORS suboru (asi pre sfunkčenie API calls z JS suboru)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#---------------  MAIN PART OF CODE ----------------

#Funkcia vytvarajuca endpoint ktorý počáva na request POST, tento endpoint slúži na tvorbu userov
class CreteUser(Resource):
    def post(self):
        data = request.data

        status = create(data)

        return status

#---------------- MAIN RESOURCES ------------------
#Definovanie endpointov
api.add_resource(CreteUser, '/user')

#----------- FUNCTIONS FOR NEW THREADS ------------
def timer():
    #Funkcia Timer slúži k pravidelnemu obnovovanieu tokenov,
    #táto funkcia zabezpečuje, že funkcia, kotrá tvorí tokeny
    #je zavoláná pravidelne podla toho ako je špecifikované v 
    # every("číslo"). špecifikacia sekund, minut, hodin alebo dní.
    schedule.every(2).weeks.do(renewAllTokens)

    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    #Tvorba nového vlákna, ktoré spšťa príslušnú funkciu
    #_thread.start_new_thread(timer, ())

    #Konfigurácia API, url a port
    app.run(host = config_user.HOST_API_URL_TEST, port = config_user.HOST_API_PORT_TEST, use_reloader=True)