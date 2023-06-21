import json
from flask import jsonify, request
import datetime
from datetime import timedelta
import jwt
from models.models import *
import paho.mqtt.client as mqtt
from utils.utils import checktoken
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')    

def store_route():
    data = request.get_json()
    token = data['session_token']
    check = checktoken(token)
    if check['valid'] == 'ok':
        new_route = {
            'id_route': data['id_route'],
            'coordinates': data['coordinates']
        }
        try:
            id = routes.insert_one(new_route).inserted_id
            response = {'result': 'ok'}
        except pymongo.errors.DuplicateKeyError as description_error:
            response = {'result': 'error', 'description': str(description_error)}
    else:
        response = {'result': 'error', 'description': check['valid']}
    return jsonify(response)

def get_route():
    data = request.get_json()
    token = data['session_token']
    check = checktoken(token)
    if check['valid'] == 'ok':
        route = routes.find_one({'id_route': data['id_route']})
        if route is None:
            response = {'valid': 'error', 'description': 'Route not found'}
        else:
            response = {'result': 'ok', 'coordinates' : route['coordinates']}
    else:
        response = {'result': 'error', 'description': check['valid']}
    return jsonify(response)

#def generate_map_route():
#    data = request.get_json()
#    token = data['session_token']
#    check = checktoken(token)
#    if check['valid'] == 'ok':
#        route_act_end = {
#            location_act: data['location_act'],
#            location_end: data['location_end']
#        }
        
#        new_route = {'enviar y route_act_end a la web y recibir respuesta': route_act_end} #################falta enviar a web por nginx
#        if new_route['result'] == 'ok':
#            response = {'result': 'ok', 'id_route': new_route['id_route'], 'coordinates': new_route['coordinates']}
#        else:
#            response = new_route
#    else:
#        response = {'result': 'error', 'description': check['valid']}
#    return jsonify(response)

def send_order_cars():
    data = request.get_json()
    value = checktoken(data['session_token'])
    if value['valid'] !='ok' or value['type']!='internal':
        return jsonify({'result': 'tu no pots man'})
    # Crea un objeto cliente MQTT
    client = mqtt.Client()

    # Conecta al servidor MQTT
    client.connect("mosquitto", 1883, 60)

    for i in data["assignations"]:
        orders = []
        for j in i["cargo"]:
            orders.append(int(j["order_identifier"]))
        # Crea un mensaje JSON
        mensaje = {    "id_car":     i["id_car"],
                    "order":     orders,
                    "route":    i["route"]["coordinates"]}
        
        camions.update_one({"id_car": i["id_car"]} , {'$set': {'location_in': {"latitude":i["route"]["coordinates"][0][1],"longitude":i["route"]["coordinates"][0][0]}}})
        camions.update_one({"id_car": i["id_car"]} , {'$set': {'location_in': {"latitude":i["route"]["coordinates"][-1][1],"longitude":i["route"]["coordinates"][-1][0]}}})
        camions.update_one({"id_car": i["id_car"]} , {'$set': {'id_route': i["route"]["id_route"]}})
        
        # Codifica el mensaje JSON a una cadena
        mensaje_json = json.dumps(mensaje)
        logging.info(mensaje)
        # Publica el mensaje en el topic "PTIN2023/A1/CAR"
        client.publish("PTIN2023/CAR/STARTROUTE", mensaje_json)

    # Cierra la conexión MQTT
    client.disconnect()
    return jsonify({'result':'ok'})



    
def general_storage_pos():
    response = {    
        'result'    : 'ok', 
        'latitude'  : "41.221583", 
        'longitude' : "1.729806"
    }
    return jsonify(response)

