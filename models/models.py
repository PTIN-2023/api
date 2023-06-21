import pymongo

config = {
    "username": "root",
    "password": "root",
    "host": "mongo",
    "port": 27017
}

connector = "mongodb://{username}:{password}@{host}:{port}/?authSource=admin".format(**config)
client = pymongo.MongoClient(connector)
db = client["PTIN"]
users = db["UsersA4"]
farmacs = db["MedsA4"]
sessio = db["sessio"]
camions = db['Camions']
orders = db['Orders']
drons = db['Drones']
routes = db['Routes']
recipes = db['Recipes']
colmenas = db['colmena']


