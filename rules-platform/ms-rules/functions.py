from flask import request
import gitlab
import config
import uuid
import config
import json
import base64


#Jednotlivé funkcie voláne zo súboru view.py

gl = gitlab.Gitlab(url = config.URL, private_token = config.PRIVATE_TOKEN)

#Porovnanie prichádzauceho názvu pravidla s tým ktoré sa nachádza v konfiguračnom súbore.
def compareRule(type):
    if type in config.DIR_NAMES:
        return type.upper()
    else:
        return config.DEFAULT_DIR.upper()

#Poslanie súboru do repozitáru na GitLab server.
def pushFile(type, text):
    compared_type = compareRule(type)
    #encoded_text = base64.b64decode(text)

    #treba špecifikovať ID repozitáru do ktorého sa bude vkladať súbor
    project_id = config.REPO_ID
    project = gl.projects.get(project_id)

    #Generovanie zatial náhodného ID pre každý typ pravidla     
    uni_id = uuid.uuid1()

    f = project.files.create({'file_path': f'{compared_type}'+'_RULES/'+f'{compared_type}'+'_'+f'{uni_id}'+'.txt',
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
    items = project.repository_tree(path=str(dir_name))

    return items

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
        #Deódovanie z bas64 do utf-8
        decoded_content = base64.b64decode(hisotry_file.content).decode("utf-8")

        #Zmazanie branchu aby nezahlťoval gitlab
        project.branches.delete(f'{name}')

        #Vrátenie starej verzei pravidla
        old_file = {}
        old_file['message'] = decoded_content

        print(old_file)
        return old_file


    except gitlab.exceptions.GitlabCreateError:
        #Zmazanie branchu aby nezahlťoval gitlab AK nastane error aby nebol vytvorený do nekonečna
        project.branches.delete(f'{name}')

        error_message = {
            "error_message": "Branch with this name is already created try another one!"
        }

        return  error_message
    
