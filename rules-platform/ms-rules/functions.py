from flask import request
from sqlalchemy import create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker
import database.database_config
from database.create_database import User
from pymongo import MongoClient
import gitlab
import config
import uuid
import config
import json
import base64
import requests



#Jednotlivé funkcie voláne zo súboru view.py

gl = gitlab.Gitlab(url = config.URL, private_token = config.PRIVATE_TOKEN)

#Porovnanie prichádzauceho názvu pravidla s tým ktoré sa nachádza v konfiguračnom súbore.
def compareRule(type):
    if type in config.DIR_NAMES:
        return type.upper()
    else:
        return config.DEFAULT_DIR.upper()

#Poslanie súboru do repozitáru na GitLab server.
def pushFile(type, text, name):
    compared_type = compareRule(type)
    #encoded_text = base64.b64decode(text)

    #treba špecifikovať ID repozitáru do ktorého sa bude vkladať súbor
    project_id = config.REPO_ID
    project = gl.projects.get(project_id)

    #Generovanie zatial náhodného ID pre každý typ pravidla     
    uni_id = uuid.uuid1()

    f = project.files.create({'file_path': f'{compared_type}'+'_RULES/'+f'{name}'+'_'+f'{uni_id}'+'.txt',
                            'branch': 'main',
                            'content': f'{text}',
                            'author_email': 'test@example.com',
                            'author_name': 'yourname',
                            'commit_message': 'Create testfile'})

    commits = project.commits.list(get_all=True, all=True)

    stamp = None

    for commit in commits:
        if commit == commits[-1]:
            stamp = commit.id
            
            value = {
                "hash_id": stamp
            }

            return value
    
def showMyFiles(data):

    #Načítanie prichádzajúcich dát, a rozparsovanie JSON suboru, z ktorého je vytiahnutý element "rule_dir"
    data = request.data
    json_data = json.loads(data)
    dir_name = json_data['rule_dir']

    #Konfiguračná časť usera. Je vybratý jeho personal acces token + id repozitáru, ktorý používa.
    gl_user = gitlab.Gitlab(url = "https://gitlab.com", private_token = "glpat-HuC3TE-3RYBWum2q3WjU")
    project_id = 38163703

    #Samotné vytiahnutie informácii o danom subore v danom repozitáry, nasledne sú tieto dáta vrátené cez return v JSON formáte
    project = gl_user.projects.get(project_id)
    items = project.repository_tree(path=str(dir_name.upper()), get_all=True)

    return items

def getMongoId(pub_id):
    Session = sessionmaker()
    engine = create_engine(database.database_config.POSTGRE_DIALECT+'+'+database.database_config.POSTGRE_DRIVER+'://'+database.database_config.POSTGRE_USERNAME+':'+database.database_config.POSTGRE_PASSWORD+'@'+database.database_config.POSTGRE_HOST+':'+database.database_config.POSTGRE_PORT+'/'+database.database_config.POSTGRE_DATABASE_NAME, echo = True)
    local_session = Session(bind=engine)

    mongo_id = local_session.query(User.mongo_db_id).filter_by(public_id = pub_id).first()
    return mongo_id.mongo_db_id

def getCommitHash():
    req = requests.get("https://gitlab.com/api/v4/projects/38163703/repository/files/DEFAULT_RULES%2F1/blame?ref=main", 
                   headers = {"PRIVATE-TOKEN": "glpat-HuC3TE-3RYBWum2q3WjU"},)
    
    commit_hash = req.headers['X-Gitlab-Commit-Id']
    return commit_hash

def updateMongo(id, hash):
    from bson.objectid import ObjectId

    client = MongoClient(config.URI)
    db = client.users_commit_hashes
    collection = db.users
    _id = ObjectId(id)

    all_updates = {
        "$push" : {"commit_hashes": {"hash": f"{hash}", "date": "12/03/19"}}
    }

    collection.update_one({"_id": _id}, all_updates)

def updateFiles(data):

    #Rozparsovanie JSON suboru, vytiahnutie potrebných informácií a uloženie do premenných
    data = request.data
    json_data = json.loads(data)

    file_path = json_data["file_path"]
    new_content = json_data["content"]
    message = json_data["commit_message"]

    #Konfiguračná časť usera. Je vybratý jeho personal acces token + id repozitáru, ktorý používa.
    gl_user = gitlab.Gitlab(url = "https://gitlab.com", private_token = "glpat-HuC3TE-3RYBWum2q3WjU")
    project_id = 38163703

    #Získanie suboru zo špecifického projektu ktorý chceme updatovať, a nasledne vykonanie updatu. 
    project = gl_user.projects.get(project_id)
    file = project.files.get(file_path=file_path, ref="main")
    file.content = new_content

    #Uloženie zmien vykonaných v súbore
    file.save(branch="main", commit_message=message)

    #Uloženie comit hashu do MongoDB
    commit_hash = getCommitHash()
    mong_id = getMongoId("50fbcac8-d114-4253-984a-d348291ee824")
    updateMongo(mong_id, commit_hash)

    #Vytvorenie nazvu pravidla extrahovaním časti "file_path" -> vyberá nazov za "/"
    file_name = file_path.partition("/")[-1]

    message = {
        "message": "File: " + f"{file_name} " + "was successfully updated!"
    }

    return message

#Funkcia, ktorá umožnuje vratenie sa k starej verzii suboru, pomocou tvorby branchu z commit hashu suboru, ktorý chcem získať
def createBranch(data):
    #Parser
    data = request.data
    json_data = json.loads(data)

    name = json_data["branch_name"]
    commit_hash = json_data["commit_hash"]
    file_path = json_data["file_path"]

    gl_user = gitlab.Gitlab(url = "https://gitlab.com", private_token = "glpat-HuC3TE-3RYBWum2q3WjU")
    project_id = 38163703
    project = gl_user.projects.get(project_id)

    try:
        #Tvorba branchu na zaklade commit hashu
        project.branches.create({'branch': f'{name}',
                                        'ref': f'{commit_hash}'})
        #Získanie staršej verzie súboru z branchu
        hisotry_file = project.files.get(file_path=file_path, ref=f'{name}')
        #Dekódovanie z bas64 do utf-8
        decoded_content = base64.b64decode(hisotry_file.content).decode("utf-8")

        #Vrátenie starej verzei pravidla
        old_file = {}
        old_file['message'] = decoded_content

        #Zmazanie branchu aby nezahlťoval gitlab
        project.branches.delete(f'{name}')

        print(old_file)
        return old_file


    except gitlab.exceptions.GitlabCreateError:
        #Zmazanie branchu aby nezahlťoval gitlab AK nastane error aby nebol vytvorený do nekonečna
        project.branches.delete(f'{name}')

        error_message = {
            "error_message": "Branch with this name is already created try another one!"
        }

        return  error_message
    
#Funkcia pre získanie jedneho konkrétneho obsahu súboru
def getCertainFile(data):
    data = request.data
    json_data = json.loads(data)

    file_folder = json_data["file_folder"]
    file_name = json_data["file_name"]
    # file_name = "QRADAR_60639d56-aa09-11ed-91f5-acde48001122.txt"
    # file_folder = "QRADAR_RULES"

    gl_user = gitlab.Gitlab(url = "https://gitlab.com", private_token = "glpat-HuC3TE-3RYBWum2q3WjU")
    project_id = 38163703
    project = gl_user.projects.get(project_id)

    raw_content = project.files.raw(file_path=f'{file_folder.upper()}/{file_name}', ref='main')

    file_content = {
        "content": raw_content.decode('utf-8'),
        "rule_path": f'{file_folder.upper()}/{file_name}'
    }

    return file_content

#print(getCertainFile())