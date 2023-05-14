from flask import request
from sqlalchemy import create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker
import database.database_config
from database.create_database import User
from pymongo import MongoClient
from bson import json_util
from datetime import date
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

def getMongoId(pub_id):
    Session = sessionmaker()
    engine = create_engine(database.database_config.POSTGRE_DIALECT+'+'+database.database_config.POSTGRE_DRIVER+'://'+database.database_config.POSTGRE_USERNAME+':'+database.database_config.POSTGRE_PASSWORD+'@'+database.database_config.POSTGRE_HOST+':'+database.database_config.POSTGRE_PORT+'/'+database.database_config.POSTGRE_DATABASE_NAME, echo = True)
    local_session = Session(bind=engine)

    mongo_id = local_session.query(User.mongo_db_id).filter_by(public_id = pub_id).first()
    return mongo_id.mongo_db_id

def getRepoId(pub_id):
    Session = sessionmaker()
    engine = create_engine(database.database_config.POSTGRE_DIALECT+'+'+database.database_config.POSTGRE_DRIVER+'://'+database.database_config.POSTGRE_USERNAME+':'+database.database_config.POSTGRE_PASSWORD+'@'+database.database_config.POSTGRE_HOST+':'+database.database_config.POSTGRE_PORT+'/'+database.database_config.POSTGRE_DATABASE_NAME, echo = True)
    local_session = Session(bind=engine)

    repo_id = local_session.query(User.repository_id).filter_by(public_id = pub_id).first()
    return repo_id.repository_id

def getAccessToken(pub_id):
    Session = sessionmaker()
    engine = create_engine(database.database_config.POSTGRE_DIALECT+'+'+database.database_config.POSTGRE_DRIVER+'://'+database.database_config.POSTGRE_USERNAME+':'+database.database_config.POSTGRE_PASSWORD+'@'+database.database_config.POSTGRE_HOST+':'+database.database_config.POSTGRE_PORT+'/'+database.database_config.POSTGRE_DATABASE_NAME, echo = True)
    local_session = Session(bind=engine)

    access_token = local_session.query(User.access_token).filter_by(public_id = pub_id).first()
    return access_token.access_token

#Poslanie súboru do repozitáru na GitLab server.
def pushFile(type, text, name, pub_id):
    from bson.objectid import ObjectId

    #MongoDB conector
    client = MongoClient(config.URI)
    db = client.users_commit_hashes
    collection = db.users

    compared_type = compareRule(type)
    #encoded_text = base64.b64decode(text)

    #treba špecifikovať ID repozitáru do ktorého sa bude vkladať súbor
    #Pripojenie ku GitLab serveru
    acc_token = getAccessToken(pub_id)
    project_id = getRepoId(pub_id)
    
    gl_user = gitlab.Gitlab(url = "http://10.50.64.5", private_token = f"{acc_token}", keep_base_url= True)
    project = gl_user.projects.get(project_id)

    #Generovanie zatial náhodného ID pre každý typ pravidla     
    uni_id = uuid.uuid1()

    f = project.files.create({'file_path': f'{compared_type}'+'_RULES/'+f'{name}'+'_'+f'{uni_id}'+'.txt',
                            'branch': 'main',
                            'content': f'{text}',
                            'author_email': 'test@example.com',
                            'author_name': 'yourname',
                            'commit_message': 'Create testfile'})

    project.commits.list(get_all=True, all=True)

    today = date.today()
    today_date = today.strftime("%d/%m/%Y")

    complete_file_name = name +"_"+ str(uni_id) + ".txt"
    hash = getCommitHash(pub_id, compared_type, complete_file_name)

    id = getMongoId(pub_id)
    _id = ObjectId(id)

    all_updates = {
        #   "$push" : {"rules": {f"{name}": [{"hash": f"{hash}", "date": "27/89/90"}]}}
        "$push": {"rules": {"name": f"{name}"+"_"+f"{uni_id}", "commit_hashes": [{"hash": f"{hash}", "date": f"{str(today_date)}", "status": "CREATED"}]}}
    }

    collection.update_one({"_id": _id}, all_updates)
    
def showMyFiles(data):

    #Načítanie prichádzajúcich dát, a rozparsovanie JSON suboru, z ktorého je vytiahnutý element "rule_dir"
    data = request.data
    json_data = json.loads(data)
    dir_name = json_data['rule_dir']
    public_id = json_data['public_id']

    acc_token = getAccessToken(public_id)
    repo_id = getRepoId(public_id)

    #Konfiguračná časť usera. Je vybratý jeho personal acces token + id repozitáru, ktorý používa.
    gl_user = gitlab.Gitlab(url = "http://10.50.64.5", private_token = acc_token)
    project_id = repo_id

    #Samotné vytiahnutie informácii o danom subore v danom repozitáry, nasledne sú tieto dáta vrátené cez return v JSON formáte
    project = gl_user.projects.get(project_id)
    items = project.repository_tree(path=str(dir_name.upper()), get_all=True)

    return items

def getCommitHash(pub_id, rule_dir, file_name):
    repo_id = getRepoId(pub_id)
    acc_token = getAccessToken(pub_id)

    print(rule_dir)
    print(repo_id)
    print(file_name)
    print(acc_token)
    req = requests.get("http://10.50.64.5/api/v4/projects/"+f"{repo_id}"+"/repository/files/"+f"{rule_dir}"+"_RULES"+"%2F"+f"{file_name}"+"/blame?ref=main", 
                     headers = {"PRIVATE-TOKEN": f"{acc_token}"})
    
    # req = requests.get("http://10.50.64.5/api/v4/projects/"+f'{repo_id}'+"/repository/files/"+f'{rule_dir}'+"_RULES%2F"+f'{file_name}'+"/blame?ref=main", 
    #                headers = {"PRIVATE-TOKEN": f"{acc_token}"},)
    print(req)
    commit_hash = req.headers['X-Gitlab-Commit-Id']
    return commit_hash

def updateMongo(id, hash, rule_name):
    from bson.objectid import ObjectId

    today = date.today()
    today_date = today.strftime("%d/%m/%Y")

    client = MongoClient(config.URI)
    db = client.users_commit_hashes
    collection = db.users
    _id = ObjectId(id)

    all_updates = {
        "$push": {"rules.$[rule].commit_hashes": {"hash": f"{hash}", "date": f"{str(today_date)}", "status": "UPDATED"}}
    }

    collection.update_one({"_id": _id}, all_updates, array_filters=[{ "rule.name": f"{rule_name}" }], upsert=True)

def updateFiles(data):

    #Rozparsovanie JSON suboru, vytiahnutie potrebných informácií a uloženie do premenných
    data = request.data
    json_data = json.loads(data)

    file_path = json_data["file_path"]
    new_content = json_data["content"]
    message = json_data["commit_message"]
    public_id = json_data["public_id"]

    acces_token = getAccessToken(public_id)
    repo_id = getRepoId(public_id)

    #Konfiguračná časť usera. Je vybratý jeho personal acces token + id repozitáru, ktorý používa.
    gl_user = gitlab.Gitlab(url = "http://10.50.64.5", private_token = acces_token)
    project_id = repo_id

    #Získanie suboru zo špecifického projektu ktorý chceme updatovať, a nasledne vykonanie updatu. 
    project = gl_user.projects.get(project_id)
    print(file_path)
    file = project.files.get(file_path=file_path, ref="main")
    file.content = new_content

    #Uloženie zmien vykonaných v súbore
    file.save(branch="main", commit_message=message)

    #Vytvorenie nazvu pravidla extrahovaním časti "file_path" -> vyberá nazov za "/"
    file_name = file_path.partition("/")[-1]
    file_dir = file_path.partition("_")[0]

    #Uloženie comit hashu do MongoDB
    commit_hash = getCommitHash(public_id, file_dir, file_name)
    mong_id = getMongoId(public_id)
    file_name_mongo = file_name.partition(".")[0]
    updateMongo(mong_id, commit_hash, file_name_mongo)

    #Vytvorenie správy ktora sa posiela v returne
    message = {
        "message": "File: " + f"{file_name} " + "was successfully updated!"
    }

    return message

#Funkcia, ktorá umožnuje vratenie sa k starej verzii suboru, pomocou tvorby branchu z commit hashu suboru, ktorý chcem získať
def createBranch(data):
    #Parser
    data = request.data
    json_data = json.loads(data)

    name = json_data["name"]
    commit_hash = json_data["commit_hash"]
    file_path = json_data["file_path"]
    public_id = json_data['public_id']

    acc_token = getAccessToken(public_id)
    repo_id = getRepoId(public_id)

    gl_user = gitlab.Gitlab(url = "http://10.50.64.5", private_token = acc_token)
    project_id = repo_id
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
    public_id = json_data['public_id']

    acc_token = getAccessToken(public_id)
    repo_id = getRepoId(public_id)

    gl_user = gitlab.Gitlab(url = "http://10.50.64.5", private_token = acc_token)
    project_id = repo_id
    project = gl_user.projects.get(project_id)

    raw_content = project.files.raw(file_path=f'{file_folder.upper()}/{file_name}', ref='main')

    file_content = {
        "content": raw_content.decode('utf-8'),
        "rule_path": f'{file_folder.upper()}/{file_name}'
    }

    return file_content

#Funkcia ktorá vráti obsah mongo DB, na zaklade dát je mozné získať hashe pravidiel.
def getRulesFromMongo(data):
    from bson.objectid import ObjectId

    data = request.data
    print(data)
    json_data = json.loads(data)
    public_id = json_data["public_id"]

    mong_id = getMongoId(f"{public_id}")    

    client = MongoClient(config.URI)
    db = client.users_commit_hashes
    collection = db.users
    _id = ObjectId(f"{mong_id}")

    mong_data = collection.find_one({"_id": _id}, {'_id': False})
    # return json.loads(json_util.dumps(mong_data))
    return json.dumps(mong_data)

def deletRule(data):
    data = request.data
    json_data = json.loads(data)

    file_path = json_data['file_path']
    message = json_data['message']
    public_id = json_data['public_id']

    acc_token = getAccessToken(public_id)
    repo_id = getRepoId(public_id)

    gl_user = gitlab.Gitlab(url = "http://10.50.64.5", private_token = acc_token)
    project = gl_user.projects.get(repo_id)

    project.files.delete(file_path=file_path, commit_message=message, branch="main")
