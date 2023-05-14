from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import declarative_base
#from sqlalchemy.ext.declarative import declarative_base
import config

#Vytvorenie tabulky v databáze pomocou ORM
Base=declarative_base()
#Definovanie pripojenia na PostgreSQL databazu
engine = create_engine(config.POSTGRE_DIALECT+'+'+config.POSTGRE_DRIVER+'://'+config.POSTGRE_USERNAME+':'+config.POSTGRE_PASSWORD+'@'+config.POSTGRE_HOST+':'+config.POSTGRE_PORT+'/'+config.POSTGRE_DATABASE_NAME, echo = True)

class User(Base):

    __tablename__ = "users_flask"
    id = Column(Integer(), primary_key = True)
    username = Column(String(25), nullable = False, unique = True)
    password = Column(String(80), nullable = False)
    


#CREATE DATABASE
#Base.metadata.create_all(engine)

#CREATE USER
local_session = Session(bind=engine)

new_user=User(username="Postgre", repo_id = 789456)

local_session.add(new_user)

local_session.commit()


#UPDATE USER
"""
local_session = Session(bind=engine)

user_to_update = local_session.query(User).filter(User.username == 'shrek').first()

user_to_update.repo_id = 1010

local_session.commit()"""
