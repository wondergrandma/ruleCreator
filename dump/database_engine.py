from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from create_database import User, engine

#Engine pre tvorbu a pripojenie databázy

#Vytvorenie session potrebnej pre poslanie dát do databáze
Session = sessionmaker()

def createUserInDatabase(user_name, email):
    #Zapnutie session vo funkcii
    local_session = Session(bind=engine)

    #Vytvorenie dát noveho usera
    new_user = User(username=user_name, email=email, repo_id=None)

    #Pridanie noveho usera do session a následný commitm ktorý dáta odošle
    local_session.add(new_user)
    local_session.commit()


def insertRepoId(repod_id, user_name):
    #Zapnutie session
    local_session = Session(bind=engine)

    #Vytvorenie dát pre Update príkaz
    update_user_repo = local_session.query(User).filter(User.username == user_name).first()

    #Pridanie dát do session a následný komit odoslaný na databázový server
    update_user_repo.repo_id = repod_id
    local_session.commit()

def selectRepoId(user_name):

    local_session = Session(bind=engine)

    get_repo_id = local_session.execute(select(User.repo_id).where(User.username == user_name)).first().repo_id

    local_session.commit()

    return get_repo_id

    