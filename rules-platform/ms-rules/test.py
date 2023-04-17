#from database_engine import selectRepoId
import gitlab
import config
import statistics
from collections import defaultdict
from sqlalchemy import create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker
import database.database_config
from database.create_database import User
import requests
#user_name = "Lobster"
# def getMongoId(pub_id):
#     Session = sessionmaker()
#     engine = create_engine(database.database_config.POSTGRE_DIALECT+'+'+database.database_config.POSTGRE_DRIVER+'://'+database.database_config.POSTGRE_USERNAME+':'+database.database_config.POSTGRE_PASSWORD+'@'+database.database_config.POSTGRE_HOST+':'+database.database_config.POSTGRE_PORT+'/'+database.database_config.POSTGRE_DATABASE_NAME, echo = True)
#     local_session = Session(bind=engine)

#     mongo_id = local_session.query(User.mongo_db_id).filter_by(public_id = pub_id).first()
#     return mongo_id
# print(str(getMongoId("50fbcac8-d114-4253-984a-d348291ee824")))

def getHash():
    req = requests.get("https://gitlab.com/api/v4/projects/38163703/repository/files/DEFAULT_RULES%2F1/blame?ref=main", 
                   headers = {"PRIVATE-TOKEN": "glpat-HuC3TE-3RYBWum2q3WjU"},)
    
    commit_hash = req.headers['X-Gitlab-Commit-Id']
    return commit_hash

print(getHash())

#selectRepoId(user_name)
#Rozparsovanie JSON suboru, vytiahnutie potrebných informácií a uloženie do premenných

# gl_user = gitlab.Gitlab(url = "https://gitlab.com", private_token = "glpat-HuC3TE-3RYBWum2q3WjU")
# project_id = 38163703

# project = gl_user.projects.get(project_id)
# commits = project.commits.list(all=True)
# file_path = json_data["file_path"]
# new_content = json_data["content"]
# message = json_data["commit_message"]

# file_path = "DEFAULT_RULES/DEFAULT_3a0e42dc-dac4-11ed-866d-acde48001122.txt"
# new_content = "SKUSAM CI TO IDE"
# message = "SKAP"

#     #Konfiguračná časť usera. Je vybratý jeho personal acces token + id repozitáru, ktorý používa.
# gl_user = gitlab.Gitlab(url = "https://gitlab.com", private_token = "glpat-HuC3TE-3RYBWum2q3WjU")
# project_id = 38163703

# req = requests.get("https://gitlab.com/api/v4/projects/38163703/repository/files/DEFAULT_RULES%2F1/blame?ref=main", 
#                    headers = {"PRIVATE-TOKEN": "glpat-HuC3TE-3RYBWum2q3WjU"},)
#     #Získanie suboru zo špecifického projektu ktorý chceme updatovať, a nasledne vykonanie updatu. 

# print(req.json())
#raw_content = project.files.raw(file_path='QRADAR_RULES/QRADAR_60639d56-aa09-11ed-91f5-acde48001122.txt', ref='main')
#print(raw_content.decode('utf-8'))

#project.upload("test.txt", filepath="xbieli10/test")

#commits = project.commits.list(get_all=True, all=True)


"""for commit in commits:
   print(commit.id)

   if commit == commits[-1]:
      print(commit.id)"""


print(dir())