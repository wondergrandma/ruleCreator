import gitlab
import config_user
import requests
from flask import request
import json
import base64
from datetime import date, datetime, timedelta
import time
from contextlib import contextmanager
import schedule

gl = gitlab.Gitlab(url = config_user.URL, private_token = config_user.PRIVATE_TOKEN)

users = gl.users.list()
users_ids = [user.id for user in users]
print(users_ids)



"""
arr_acc_tok = []

users = gl.users.list()
users_ids = [user.id for user in users]

today_date = date.today()
next_two_weeks = today_date + timedelta(days=14)


for i in users_ids:
    create_token = gl.users.get(i, lazy=True)
    access_token = create_token.personal_access_tokens.create({
        "name": "API access token for access to ruels test 3",
        "expires_at": str(next_two_weeks),
        "scopes": "api"
    })
    arr_acc_tok.append(access_token.token)

#print(arr_acc_tok[i])

for a in users_ids:
    print(a)


##access_tokens = gl.personal_access_tokens.list(user_id=19)
#print(access_tokens)
"""



"""

def createBranch(name, commit_hash, file_path):
    #Parser
    
    #json_data = json.loads(data)


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
        old_file["message"] = decoded_content

        return old_file


    except gitlab.exceptions.GitlabCreateError:
        #Zmazanie branchu aby nezahlťoval gitlab AK nastane error aby nebol vytvorený do nekonečna
        project.branches.delete(f'{name}')

        error_message = {
            "error_message": "Branch with this name is already created try another one!"
        }

        return  error_message



name = "zmazalo"
commit_hash = "147002c93419f7e261158758f66cc1d7b372ce61"
file_path = "QRADAR_RULES/QRADAR_7fd2387a-c659-11ed-9ce9-acde48001122.txt"

print(createBranch(name, commit_hash, file_path))


def show_name():
    print("Idem")
    print("Nejdzem")

schedule.every(4).seconds.do(show_name)

while 1:
    schedule.run_pending()
    time.sleep(1)

"""