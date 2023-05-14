from sqlalchemy import Column, String, Integer, create_engine, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
import database.database_config

Base=declarative_base()
Session = sessionmaker()
engine = create_engine(database.database_config.POSTGRE_DIALECT+'+'+database.database_config.POSTGRE_DRIVER+'://'+database.database_config.POSTGRE_USERNAME+':'+database.database_config.POSTGRE_PASSWORD+'@'+database.database_config.POSTGRE_HOST+':'+database.database_config.POSTGRE_PORT+'/'+database.database_config.POSTGRE_DATABASE_NAME, echo = True)

#Wrapper, ktorý slúži k zjednodušenému nastaveniu argumentu "nullable=False", pre riadky, ktoré si to vyžadujú.
def NullColumn(*args,**kwargs):
    kwargs["nullable"] = kwargs.get("nullable",False)
    return Column(*args,**kwargs)

#Definovanie "users" tabulky pomocou ORM
class User(Base):
    __tablename__ = "users"
    id = Column(Integer(), primary_key=True)
    public_id = NullColumn(String(50), unique=True)
    repository_id = NullColumn(Integer(), unique=True)
    gitlab_id = NullColumn(Integer(), unique=True)
    access_token = Column(String(50))
    email = NullColumn(String(50))
    name = NullColumn(String(50))
    surname = NullColumn(String(50))
    nick = NullColumn(String(50))
    password = NullColumn(String(100))
    mongo_db_id = NullColumn(String(50))
    
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    def convertDict(current_user):
        return current_user.toDict()['public_id']



#Prákaz, kotrý vytvorí tabulku/ky na základe predefinovaných tried 
Base.metadata.create_all(engine)