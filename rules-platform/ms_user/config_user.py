#Konfiguračný súbor, konfigurácia serverou, IP adreis portov + súbor s pravidlami. 

#-------- GIT SERVER CONNECTION ---------
URL = "http://10.50.64.5"
PRIVATE_TOKEN = "glpat-FQL3DhtfyYgezo8sesu4"

#URL = "https://gitlab.com"
#PRIVATE_TOKEN = "glpat-HuC3TE-3RYBWum2q3WjU"

#-------- API SERVER CONFIG ----------


#-------- API SERVER CONFIG TEST ----------
HOST_API_URL_TEST = "127.0.0.1"
HOST_API_PORT_TEST = "5115"

#HOST_API_URL_TEST = "10.50.0.2"
#HOST_API_PORT_TEST = "5101"

REPO_ID = "38163703"
#6

#-------- POSTGRESQL URL -------------
#engine = create_engine('postgresql+psycopg2://oliverbielik:test@localhost:5433/flask', echo = True)
POSTGRE_URLS = "postgresql://localhost"
POSTGRE_DIALECT = "postgresql"
POSTGRE_DRIVER = "psycopg2"
POSTGRE_USERNAME = "oliverbielik"
POSTGRE_PASSWORD = "test"
POSTGRE_HOST = "localhost"
POSTGRE_PORT = "5433"
POSTGRE_DATABASE_NAME = "flask"

#-------- SUPPORTED RULES FOR DIRECTORIES ------
DIR_NAMES = ["RSA", "QRADAR", "SOLARWINDS", "DEFAULT"]
#Dir for not matched rules
DEFAULT_DIR = "DEFAULT"


#-------- MONGO DB CONNECTION ----------
URI = "mongodb://127.0.0.1:27017"

#-------- URL FOR CREATING EMPTY DIRS ----------