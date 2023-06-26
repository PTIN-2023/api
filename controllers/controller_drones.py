from flask import jsonify, request
import datetime
from datetime import timedelta
import jwt
from models.models import *
from utils.utils import checktoken

import json
import paho.mqtt.client as mqtt

OK = 'ok'
DRON_WAITS = 'waits'
BEEHIVE_DOES_NOT_EXIST = {'result' : 'error, la colmena no existeix'}

START_ROUTE = 1
NOT_AVAILABLE_AT_CLOUD = { 'result': 'error, funcio no disponible al cloud' }

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
        return jsonify({'result':'error, funcio no disponible al cloud'})
    data = request.get_json()
    value = checktoken(data['session_token'])
    assignations = data['assignations'] 
    if value['valid'] == 'ok':

        # check si la ruta existe
        coordinates = routes.find_one({'id_route': assignation['id_route']})['coordinates']

        assignations = data['assignations']
        for assignation in assignations:
            send_dron(
                assignation['id_dron'],
                START_ROUTE,
                coordinates,
            )
                
        response = {'result' : 'ok'}
    else:
        response = {'result': 'Invalid token'}
        
    return jsonify(response)


def send_dron(id_dron, order, coordinates):
    if is_local == 0:
        return jsonify({'result':'error, funcio no disponible al cloud'})
    
    client = mqtt.Client()
    client.connect("mosquitto", 1883, 60)

    msg = {    
        "id_dron"   :   id_dron,
        "order"     :   order,
        "route"     :   coordinates
    }
    mensaje_json = json.dumps(msg)

    client.publish("PTIN2023/DRON/STARTROUTE", mensaje_json)
    client.disconnect()


def list_orders_to_send_drones():
    
    if is_local == 0:
        return jsonify(NOT_AVAILABLE_AT_CLOUD)
    
    data = request.get_json()
    value = checktoken(data['session_token']) 
    response = { 'value' : value['valid'] }

    if value['valid'] == OK:

        beehive = colmenas.find({ 'id_beehive' : data['id_beehive'] })
        if beehive is not None:

            orders = []
            packages = beehive['packages']

            for package in packages:
                order_identifier = package['order_identifier']
                order = orders.find({ 'order_identifier' : order_identifier })

                # Para probar ponemos un destino fijo, edge 2, ubicación -> cubelles
                # Av. Corral d'en Cona, 8, 08880 El Corral d'en Cona, Barcelona -> 41.219670, 1.669643

                # Final: coger info del cloud a partir de patient_email, y sacar coordenadas
                coords_destiny = {
                    'latitude'  :   '41.219670',
                    'longitude' :   '1.669643'
                }

                orders.append({
                    'order_identifier'  : order['order_identifier'],
                    'medicine_list'     : order['meds_list'],
                    'date'              : order['date'],
                    'state'             : order['state'],
                    'coords_destiny'    : coords_destiny
                })

            return jsonify({
                'result'    : OK, 
                'orders'    : orders
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

# def colmena_global():
#     data = request.get_json()
#     value = checktoken(data['session_token'])
#     response = {'value': value['valid']}
    
#     if value['valid'] == 'ok':
#         colmena = colmenas.find()
#         return jsonify(response, [{
#             'id_beehive': doc['id_beehive'],
#         #falta latitude y longitud
#         }for doc in drones])
#     else:
#         return jsonify(response)
        
#def beehives_local():
#    if is_local == 0:
#        return jsonify({'result':'error, funcio no disponible al cloud'})
#    data = request.get_json()
#    value = checktoken(data['session_token']) #checkeo si el usuario de la sesion tiene token
#    if value['valid'] == 'ok': #si tiene token
#        #mañana la acabo
#        #variable de entorno, pillar su id
#        #query = {'id_beehive': variable de entorno (id)}
#        #for de ids
#            #array auxiliar
#            #latitud y longitud para ese id.append
#        #en el response meter el array 
#        response = {'valid': 'None1'}
#    
#    else:
#        response = {'result': 'No tienes token para poder comprobar esto, espabila'}
#        
#    return jsonify(response)      
#
