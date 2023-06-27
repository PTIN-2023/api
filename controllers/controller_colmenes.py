from flask import jsonify, request
from models.models import *
from utils.utils import checktoken
import json

import logging

OK = 'ok'
NOT_AVAILABLE_AT_CLOUD  = { 'result': 'error, funcio no disponible al cloud' }
NOT_AVAILABLE_AT_EDGE   = { 'result': "error, funcio no disponible a l'edge" }

def beehives_global():

    if is_local == 1:
        return jsonify(NOT_AVAILABLE_AT_EDGE)

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
                'url_beehive'   : colmena['url_beehive'],
            })
        response['beehives'] = beehives
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

def unload_car():

    if is_local == 0:
        return jsonify(NOT_AVAILABLE_AT_CLOUD)

    logging.info(request.get_json())

    data = request.get_json()
    value = checktoken(data['session_token'])
    response = { 'value' : value['valid'] }

    if value['valid'] == OK:

        full_orders = data['orders']
        id_beehive  = data['id_beehive']

        for order in full_orders:
            orders.insert_one(order)

        for order in full_orders:
            colmenas.update_one(
                { 'id_beehive' : int(id_beehive) },
                { "$push" : { "packages" : {
                    'order_identifier' : order['order_identifier']
                }}}
            )

        response['value'] = OK
        return jsonify(response), 200
    
    else:
        response = value
        return jsonify(response), 500