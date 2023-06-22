from flask import jsonify, request
import datetime
from datetime import timedelta
import jwt
from models.models import *
from utils.utils import checktoken

import json
import paho.mqtt.client as mqtt

START_ROUTE = 1
###########################################Igual seria conveniente que todo lo de drones se hga solo en los edges no en el cloud, se arreglaría pponiendo esta comanda en cada funcion
#
#    if is_local == 0:
#        return jsonify({'result':'error, funcio no disponible al cloud'})

def drons_full_info():
     data = request.get_json()
     value = checktoken(data['session_token'])
     response = {'value': value['valid']}
    
     if value['valid'] == 'ok':
        drones = drons.find()
        res=([{
            'id_dron': doc['id_dron'],
             #'id_route': doc['id_route'], #BBDD no tienen id_route
             'battery': doc['battery'],
             'status': doc['status'],
             'autonomy': doc['autonomy'],
             'capacity': doc['capacity'], #No lo tienen los de BBDD
             'last_maintenance_date': doc['last_maintenance_date'],
             'order_identifier': doc['order_identifier'],
             'id_beehive': doc['beehive'],
             'location_in ': doc['location_in'],
             'location_act': doc['location_act'],
             'location_end': doc['location_end'],

    }for doc in drones])
        return jsonify({'result':'ok','drons':res})
     else:
        return jsonify(response)




def drons_pos_info():
     data = request.get_json()
     value = checktoken(data['session_token'])
     response = {'value': value['valid']}

     if value['valid'] == 'ok':
        drones = drons.find()
        res=([{
             'id_dron': doc['id_dron'],
             'latitude': doc['location_in']['latitude'],
             'longitud': doc['location_in']['longitude'],

    }for doc in drones])
        return jsonify({'result':'ok','drons':res})
     else:
        return jsonify(response)

def send_order_drones():
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


#Faltan edges y mapa bien
def list_order_to_set_drones():
    data = request.get_json()
    value = checktoken(data['session_token']) 
    if value['valid'] == 'ok':
        response = {'result' : 'token bien'}
    else:
        response = {'result': 'Invalid token'}
        
    return jsonify(response)

def list_available_drones():
    data = request.get_json()
    value = checktoken(data['session_token'])
    response = {'result': value['valid']}

    if value['valid'] == 'ok':
        drones = drons.find()
        res=([{
            'id_car': doc['id_dron'],
            'status': doc['status'],
            'autonomy': doc['autonomy'],
            'capacity': doc['capacity']
    }for doc in drones])
        return jsonify({'result':'ok','drons':res})
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
        
def beehives_local():
    data = request.get_json()
    value = checktoken(data['session_token']) #checkeo si el usuario de la sesion tiene token
    if value['valid'] == 'ok': #si tiene token
        #mañana la acabo
        #variable de entorno, pillar su id
        #query = {'id_beehive': variable de entorno (id)}
        #for de ids
            #array auxiliar
            #latitud y longitud para ese id.append
        #en el response meter el array 
        response = {'valid': 'None1'}
    
    else:
        response = {'result': 'No tienes token para poder comprobar esto, espabila'}
        
    return jsonify(response)      

