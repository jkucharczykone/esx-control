#Create database
from sqlalchemy import create_engine
import getpass
login=input("Login db: ")
password=getpass.getpass("Password db: ")
db=input("DB: ")
engine=create_engine("postgres://{0}:{1}@127.0.0.1:5432/{2}".format(login,password,db))
from models import *
Base.metadata.create_all(engine)
engine.dispose()