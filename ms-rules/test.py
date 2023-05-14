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

file_path = "QRADAR_RULES/MojePravidlo_d559f7d8-e279-11ed-b57e-acde48001122"

file_dir = file_path.partition("_")[0]
print(file_dir)

# req = requests.get("https://gitlab.com/api/v4/projects/38163703/repository/files/QRADAR_RULES%2FQRADAR_0cc3fa90-a9f7-11ed-a8fe-acde48001122.txt/blame?ref=main", 
#                    headers = {"PRIVATE-TOKEN": "glpat-rxpsseea6tWigSyb2f8J"})
# print(req.headers)

# req = requests.get("http://10.50.64.5/api/v4/projects/39/repository/files/QRADAR_RULES%2FMojePravidlo_0aad2d5c-e279-11ed-8203-acde48001122.txt/blame?ref=main", 
#                      headers = {"PRIVATE-TOKEN": "glpat-yqTABaL3kE4z6Wr8PjTw"},)

# print(req.headers)

# get the project and file objects
# project = gl.projects.get(project_id)
# file = project.files.get(file_path, ref='main')

# get the commit hash for the file






















#user_name = "Lobster"
# def getMongoId(pub_id):
#     Session = sessionmaker()
#     engine = create_engine(database.database_config.POSTGRE_DIALECT+'+'+database.database_config.POSTGRE_DRIVER+'://'+database.database_config.POSTGRE_USERNAME+':'+database.database_config.POSTGRE_PASSWORD+'@'+database.database_config.POSTGRE_HOST+':'+database.database_config.POSTGRE_PORT+'/'+database.database_config.POSTGRE_DATABASE_NAME, echo = True)
#     local_session = Session(bind=engine)

#     mongo_id = local_session.query(User.mongo_db_id).filter_by(public_id = pub_id).first()
#     return mongo_id
# print(str(getMongoId("50fbcac8-d114-4253-984a-d348291ee824")))

# def getCommitHash():
#     repo_id = 37
#     acc_token = "glpat-F8NnQGzt94mHxKcHJ6H9"
#     rule_dir = 

#     req = requests.get("http://10.50.64.5/api/v4/projects/"+f"{repo_id}"+"/repository/files/"+f"{rule_dir}"+"_RULES"+"%2F1/blame?ref=main", 
#                    headers = {"PRIVATE-TOKEN": f"{acc_token}"},)
    
#     print(req)
#     #commit_hash = req.headers['X-Gitlab-Commit-Id']
#     #commit_hash = req.headers['X-Request-Id']
#     return "commit_hash"





# def getHash():
#     req = requests.get("https://gitlab.com/api/v4/projects/38163703/repository/files/DEFAULT_RULES%2F1/blame?ref=main", 
#                    headers = {"PRIVATE-TOKEN": "glpat-HuC3TE-3RYBWum2q3WjU"},)
    
#     commit_hash = req.headers['X-Gitlab-Commit-Id']
#     return commit_hash

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