from flask import jsonify, request
from models.models import *
from utils.utils import checktoken
import json


def beehives_global():
    data = request.get_json()
    value = checktoken(data['session_token'])
    if value['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/beehives_global"
            return requests.post(url, json=data).json()
        colmenitas = colmenas.find()
        response['beehives'] = [{
            'id_beehive': doc['id_beehive'],
            'latitude': doc['location_end']['latitude'],
            'longitude': doc['location_end']['longitude'],
        }for doc in colmenitas]
    else:
        response = value
    return jsonify(response)    

def beehives_local():
    data = request.get_json()
    value = checktoken(data['session_token'])
    if value['valid'] == 'ok':
        if is_local == 0:
            return jsonify({'result':'error, funcio no disponible al cloud'})
        colmenitas = colmenas.find()
        response['beehives'] = [{
            'id_beehive': doc['id_beehive'],
            'latitude': doc['location_end']['latitude'],
            'longitude': doc['location_end']['longitude'],
        }for doc in colmenitas]
    else:
        response = value
    return jsonify(response) 
