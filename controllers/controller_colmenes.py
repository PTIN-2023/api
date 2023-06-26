from flask import jsonify, request
from models.models import *
from utils.utils import checktoken
import json

OK = 'ok'
NOT_AVAILABLE_AT_CLOUD = { 'result': 'error, funcio no disponible al cloud' }

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
            'url_beehive': url,
        }for doc in colmenitas]
    else:
        response = value
    return jsonify(response)    

def beehives_local():

    if is_local == 0:
        return jsonify(NOT_AVAILABLE_AT_CLOUD)

    data = request.get_json()
    value = checktoken(data['session_token'])
    response = { 'value' : value['valid'] }

    if value['valid'] == OK:
        colmenitas = colmenas.find()

        beehives = []
        for colmena in colmenitas:
            beehives.append({
                'id_beehive'    : colmena['id_beehive'],
                'latitude'      : colmena['location_end']['latitude'],
                'longitude'     : colmena['location_end']['longitude'],
            })
        response['beehives'] = beehives
    else:
        response = value
        
    return jsonify(response) 
