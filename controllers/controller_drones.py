from flask import jsonify, request
import datetime
from datetime import timedelta
import jwt
from models.models import *
from utils.utils import checktoken, generate_extra_points

import logging
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')

import json
import paho.mqtt.client as mqtt

OK = 'ok'
INTERNAL = 'internal'

CAR_SENT = 'car_sent'

RES_OK  = { 'value': "ok" }
FAILED  = { 'value': "failed" }
BEEHIVE_DOES_NOT_EXIST = {'result' : 'error, la colmena no existeix'}
NOT_AVAILABLE_AT_CLOUD = { 'result': 'error, funcio no disponible al cloud' }

START_ROUTE = 1
DRON_WAITS = 'waits'

def drons_full_info():
    
    if is_local == 0:
        return jsonify(NOT_AVAILABLE_AT_CLOUD)
    
    data = request.get_json()
    value = checktoken(data['session_token'])
    response = { 'value' : value['valid'] }
    
    if value['valid'] == OK:
        drones = drons.find()
        res=( [{
            'id_dron'               : doc['id_dron'],
            'id_route'              : doc['id_route'],
            'beehive'               : doc['beehive'],
            'order_identifier'      : doc['order_identifier'],
            'battery'               : doc['battery'],
            'status'                : doc['status_num'],
            'status_text'           : doc['status'],
            'autonomy'              : doc['autonomy'],
            'capacity'              : doc['capacity'],
            'id_beehive'            : doc['beehive'],
            'location_in '          : doc['location_in'],
            'location_act'          : doc['location_act'],
            'location_end'          : doc['location_end'],
            'last_maintenance_date' : doc['last_maintenance_date'],
        } for doc in drones] )
        
        return jsonify({
            'result'    : OK, 
            'drones'    : res
        })
    
    else:
        return jsonify(response)


def drons_pos_info():

    if is_local == 0:
        return jsonify(NOT_AVAILABLE_AT_CLOUD)
    
    data = request.get_json()
    value = checktoken(data['session_token'])
    response = { 'value' : value['valid'] }

    if value['valid'] == OK:
        drones = drons.find()
        res=( [{
             'id_dron'  : doc['id_dron'],
             'latitude' : doc['location_in']['latitude'],
             'longitud' : doc['location_in']['longitude'],
        } for doc in drones] )

        return jsonify({
            'result'    : OK, 
            'drones'    : res
        })
    
    else:
        return jsonify(response)

def send_order_drones():
    
    if is_local == 0:
        return jsonify(NOT_AVAILABLE_AT_CLOUD)
    
    data = request.get_json()
    value = checktoken(data['session_token'])
    if value['valid'] != OK or value['type'] != INTERNAL:
        return jsonify(FAILED)
    
    for dron in data['assignations']:
        id_dron             = dron['id_dron']
        id_route            = dron['route']['id_route']
        order_identifier    = dron['order']['order_identifier']
        coordinates         = routes.find_one({ 'id_route': id_route })['coordinates']

        update_fields = { 
            'id_route'          : id_route,
            'order_identifier'  : order_identifier,
        }
        result = drons.update_one(
            {'id_dron'  : id_dron }, 
            {'$set'     : update_fields }
        )
                
        if result.modified_count > 0:
            route = coordinates
            send_dron(id_dron, route)

        else:
            logging.info("DRONS | El documento no se actualizó. Puede que no se encontrara el id_dron especificado.")
            return jsonify(FAILED), 404

    return jsonify(RES_OK)
        

def send_dron(id_dron, coordinates):
    
    if is_local == 0:
        return jsonify(NOT_AVAILABLE_AT_CLOUD)
    
    SERVER = "192.168.80.241" if id_dron == 0 else "mosquitto"

    client = mqtt.Client()
    client.connect(SERVER, 1883, 60)

    msg = {    
        "id_dron"   :   id_dron,
        "order"     :   START_ROUTE,
        "route"     :   str(coordinates)
    }
    mensaje_json = json.dumps(msg)

    STARTROUTE = "PTIN2023/" + str(topic_city) + "/DRON/STARTROUTE"

    client.publish(STARTROUTE, mensaje_json)
    client.disconnect()


def list_orders_to_send_drones():
    
    if is_local == 0:
        return jsonify(NOT_AVAILABLE_AT_CLOUD)
    
    data = request.get_json()
    value = checktoken(data['session_token']) 
    response = { 'value' : value['valid'] }

    if value['valid'] == OK:

        beehive = colmenas.find_one({ 'id_beehive' : int(data['id_beehive']) })
        if beehive is not None:

            orders_to_send = []
            packages = beehive['packages']

            for package in packages:
                order_identifier = package['order_identifier']
                order = orders.find_one({
                    'order_identifier'    : order_identifier,
                    'state'               : CAR_SENT 
                })

                if order != None:                    
                    payload = {
                        'session_token' : INTERNAL,
                        'user_email'    : order['patient_email']
                    }
                    url = cloud_api + "/api/user_position"
                    response = requests.post(url, json=payload).json()

                    coords_destiny = ''
                    if response['result'] == OK:
                        coords_destiny = response['user_coordinates']
                       
                    orders_to_send.append({
                        'order_identifier'  : order['order_identifier'],
                        'medicine_list'     : order['meds_list'],
                        'date'              : order['date'],
                        'state'             : order['state'],
                        'coords_destiny'    : coords_destiny
                    })

            return jsonify({
                'result'    : OK, 
                'orders'    : orders_to_send
            })

        else:
            return jsonify(BEEHIVE_DOES_NOT_EXIST)

    else:
        return jsonify(response)

def list_available_drones():
    
    if is_local == 0:
        return jsonify(NOT_AVAILABLE_AT_CLOUD)
    
    data = request.get_json()
    value = checktoken(data['session_token'])
    response = { 'value' : value['valid'] }

    if value['valid'] == OK:
        drones = drons.find({
            'status'    : DRON_WAITS,
            'beehive'   : int(data['id_beehive'])
        })
        res=( [{
            'id_dron'   : doc['id_dron'],
            'status'    : doc['status_num'],
            'autonomy'  : doc['autonomy'],
            'capacity'  : doc['capacity']
    } for doc in drones] )
        
        return jsonify({
            'result'    : OK, 
            'drones'    : res
        })
    else:
        return jsonify(response)



def send_anomalias_dron():
    data = request.get_json()
    value = checktoken(data['session_token']) #checkeo si el usuario de la sesion tiene token
    if value['valid'] == 'ok': #si tiene token
        client = mqtt.Client()
        client.connect("mosquitto", 1883, 60)

        msg = {
            "hehe" : data['hehe'],
            "id_dron" : data['id_dron']
        }
        mensaje_json = json.dumps(msg)

        client.publish("PTIN2023/"+topic_city+"/DRON/ANOMALIA", mensaje_json)
        client.disconnect()
        return { 'result' : 'ok' }
    else:
        return { 'result' : 'error' }
