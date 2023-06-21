from flask import Flask, jsonify, request, abort, redirect, url_for, render_template
import pymongo
import datetime
import jwt
import json
from bson import ObjectId

app = Flask(__name__, template_folder='/opt/templates/')

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


@app.route("/api/list_available_medicines", methods=['POST']) #list_available_medicines", methods=['POST'])
def search_farmacs():
    #data = request.get_json()
    data = {
  "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImxhdXJhLnNhbmNoZXpAZ21haWwuY29tIn0.fxd5qO7A0yqMzwuoXUTW4Ubh8CtcGcjrk0I8R4zzCt8",
  "filter": {
    "meds_per_page": "4",
    "page": "3"
#    "med_name": "par",
#    "pvp_min": "0",
#    "pvp_max": "12",
#    "prescription_needed": [
#      "true"
#    ],
#    "form": [
#      "pill",
#      "cream",
#      "powder",
#      "liquid"
#    ],
#    "type_of_administration": [
#      "oral",
#      "topical",
#      "inhalation",
#      "ophthalmic"
#    ]
  }
}
    query = {}
    if 'filter' in data:
        try:
            filter_data = data['filter']

            if 'med_name' in filter_data:
                query['med_name'] = {'$regex': filter_data['med_name']}

            if 'pvp_min' in filter_data:
                query['price'] = {'$gte': float(filter_data['pvp_min'])}

            if 'pvp_max' in filter_data:
                if 'price' in query:
                    query['price']['$lte'] = float(filter_data['pvp_max'])
                else:
                    query['price'] = {'$lte': float(filter_data['pvp_max'])}

#            if 'prescription_needed' in filter_data:
#                if True in filter_data['prescription_needed']:
#                    query['detalles'] = {'$regex': 'Receta necesaria'}
#                if False in filter_data['receta']:
#                    query['detalles'] = {'$regex': 'Receta no necesaria'}
#
#            if 'form' in filter_data:
#                query['form'] = {'$in': filter_data['form']}

#            if 'via' in filter_data:
#                query['via'] = {'$in': filter_data['via']}

         # Determinem el número de medicaments per pàgina i la pàgina que es vol obtenir
            medNum = int(filter_data.get('medNum', '10'))
            page = int(filter_data.get('page', '1'))

         # Calculem el límit inferior i superior de medicaments a obtenir segons la pàgina i el número de medicaments per pàgina
            limit_inf = (page - 1) * medNum
            limit_sup = limit_inf + medNum

    #     # Executem la query amb els límits especificats
            results = farmacs.find(query).limit(medNum).skip(limit_inf)
        except Exception as e:
            results = str(e)
# Si no es proporciona un filtre, es retornen tots els medicaments
    else:
        results = farmacs.find()
    # results = farmacs.find()
    print([{
        'med_name': doc['med_name'],
        'codi_nacional': doc['national_code'],
        'tipus_us': str(doc['use_type']) + '€',
        'administracio': doc['type_of_administration'],
        'req_recepta': doc['prescription_needed'],
        'preu': doc['pvp'],
        'presentacio': doc['form'],
        'prospecto': doc['excipients'],
    } for doc in results])

 

search_farmacs()
