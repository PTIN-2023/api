import pymongo
import os
import requests

cloud_api = os.environ.get('CLOUD_API')
mongo_host = os.environ.get('DB_HOST')
mongo_port = os.environ.get('DB_PORT')
is_local = int(os.environ.get('IS_LOCAL'))

config = {
    "username": "root",
    "password": "root",
    "host": mongo_host,
    "port": mongo_port
}

connector = "mongodb://{username}:{password}@{host}:{port}/?authSource=admin".format(**config)
client = pymongo.MongoClient(connector)
db = client["PTIN"]
colmenas = db['colmena']
routes = db['Routes']
orders = db['Orders']
sessio = db["sessio"]
camions = users = farmacs = recipies = drons = None
if is_local == 0:
    camions = db['Camions']
    users = db["UsersA4"]
    farmacs = db["MedsA4"]
    recipes = db['Recipes']
else:
    drons = db['Drones']