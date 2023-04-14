from flask import request
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import json, gitlab, requests, uuid, bcrypt, config_user
import database.database_config
from database.create_database import User

Base=declarative_base()
Session = sessionmaker()

gl = gitlab.Gitlab(url = config_user.URL, private_token = config_user.PRIVATE_TOKEN)
engine = create_engine(database.database_config.POSTGRE_DIALECT+'+'+database.database_config.POSTGRE_DRIVER+'://'+database.database_config.POSTGRE_USERNAME+':'+database.database_config.POSTGRE_PASSWORD+'@'+database.database_config.POSTGRE_HOST+':'+database.database_config.POSTGRE_PORT+'/'+database.database_config.POSTGRE_DATABASE_NAME, echo = True)

#Tvorba repozitáru
def createRepo(name, token):

    #Definovanie userovho tokenu pre API
    gl_user = gitlab.Gitlab(url = config_user.URL, private_token = str(token))
    
    #Projektom vytvoríme vlastne repozitár. 
    gl_user.projects.create({'name': f'{name}_rules'})
    
    #Definovanie premennej pre listnutie všetkých userových projektov
    projects = gl_user.projects.list(owned = True, search = f'{name}_rules')

    #For cyklus ktorý získa ID repozitáru, ktorý sa vyššie vytvára
    for project in projects:
        repo_id = project.id
    return repo_id

#Funkcia pre tvorbu základných zložiek, každá zložka bude naplnená inicializačným súborom
def createEmptyDir(token, repo_id):
  
    #Tvorba inicializačného súboru pre každý názov pravidla, ktorý sa nachádza v DIR_NAMES
    for rules in config_user.DIR_NAMES:
        requests.post("https://gitlab.com/api/v4/projects/"+f'{repo_id}'+"/repository/files/"+f'{rules}'+"_RULES%2Finicialize.txt?ref=main",
            headers = {"PRIVATE-TOKEN": str(token)},
            data={      "start_branch": "main",
                        "branch": "main",
                        "content": "I am an initialization file, don't worry about me. :)",
                        "commit_message": "Initialization file"})

#Tvorba používateľa na základe informácii z POST requestu
def create(data):

    #Prijatie JSON suboru a jeho načítanie
    data = request.data
    json_data = json.loads(data)

    #Rozparsovanie JSON suboru na jednotlivé časti + uloženie do premenných
    user_email = json_data['user_email']
    user_name = json_data['user_name']
    user_surname = json_data['user_surname']
    user_nick = json_data ['user_nick']
    user_password = json_data['user_password']
    
    #Vytvorenie dictionary a jeho naplnenie udajmi pre tvorbu nového usera
    user_data = {
        'email': user_email,
        'password': user_password,
        'username': user_nick,
        'name': user_name + " " + user_surname,
        'skip_confirmation': 'true'
    }

    #Samotná tvorba nového usera
    new_user = gl.users.create(user_data)
    gitlab_user_id = new_user.id

    #Získanie ID userov na zaklade for cyklusu s podmienkou vraciame usera na pozícii 0 čo predstavuje najnovšie pridaneho usera
    users = gl.users.list()

    for user in users:
        if user == users[0]:
            user_id = user.id
    
    #Pripočítanie dvoch dni k aktualnemu datumu, po uplynutí dvoch dní vyprší platnosť tokenu
    today_date = date.today()
    next_day = today_date + timedelta(days=2)

    #Tvroba personal acces tokenu, ktorý bude využitý pri tvorbe repozitáru pre usera
    get_user = gl.users.get(user_id, lazy=True)
    create_token = get_user.personal_access_tokens.create({
        'name': "Create initial repository",
        'expires_at': str(next_day),
        'scopes': "api"
    })

    user_token = create_token.token

    #If else, ak je user vytvorený vráti príslušné info ak nie vrati príslušné info viď. funkcia
    if new_user:
        new_repo = createRepo(user_nick, user_token)
        createEmptyDir(user_token, new_repo)

        #Zapnutie session, ktorou sa pripojí na server s databazou
        local_session = Session(bind=engine)

        #Hashovanie pwd, solenie a nasledna tvorba hashu
        bytePwd = user_password.encode('utf-8')
        mySalt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(bytePwd, mySalt)

        #Vytvorenie usera v databazovom subore
        new_user = User(public_id=str(uuid.uuid4()), repository_id=new_repo, gitlab_id=gitlab_user_id, email=user_email, name=user_name, surname=user_surname, nick=user_nick, password=hashed_password.decode('utf-8'))
        local_session.add(new_user)
        local_session.commit()

        return {
            'user': user_nick,
            'repo_id': new_repo,
            'status': "Created"
        }
    else:
        return {
            'user': user_nick,
            'status': "Not created"
        }

#Funkcia, ktora sa volá na znovu vytvorenie access tokenov
def renewAllTokens():
    #Tvorba lokálnej session, umožnenie pripojenie pri update
    local_session = Session(bind=engine)

    #Vylistovanie všetkých userov a získanie ich ID
    users = gl.users.list()
    users_ids = [user.id for user in users]

    #Nastavenie ako dlho bude token aktívny
    today_date = date.today()
    next_two_weeks = today_date + timedelta(days=14)

    #Samotné vytvorenie tokenov pre každého usera
    for i in users_ids:
        create_token = gl.users.get(i, lazy=True)
        new_access_token = create_token.personal_access_tokens.create({
            "name": "API access token for your weekly work.",
            "expires_at": str(next_two_weeks),
            "scopes": "api"
        })

        #IF statement sluzi na to aby sa neposielali updaty pre userov ktorý sa nenachádzajú v databazovom súbore
        if i > 12:
            token_to_update = local_session.query(User).filter(User.gitlab_id == i).first()
            token_to_update.access_token = new_access_token.token
            local_session.commit()
        else:
            return