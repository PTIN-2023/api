import pymongo
import os
import requests

cloud_api = os.environ.get('CLOUD_API')
mongo_host = os.environ.get('DB_HOST')
mongo_port = os.environ.get('DB_PORT')
is_local = int(os.environ.get('IS_LOCAL'))
topic_city = os.environ.get('TOPIC_CITY')

edge0_api = os.environ.get('EDGE0')
edge1_api = os.environ.get('EDGE1')
edge2_api = os.environ.get('EDGE2')

BEEHIVES_EDGE0 = [1]
BEEHIVES_EDGE1 = [3, 4]
BEEHIVES_EDGE2 = [2]

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
doctor = db["DoctorAssigns"]
camions = users = farmacs = recipies = drons = None
if is_local == 0:
    camions = db['Camions']
    users = db["UsersA4"]
    farmacs = db["MedsA4"]
    recipes = db['Recipes']
else:
    drons = db['Drones']