from create_database import User, engine, Base

#Príkaz, ktorý vytvorí tabulku definovanú v súbore "create_database.py"
Base.metadata.create_all(engine)