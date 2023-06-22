import json
from flask import jsonify, request
import datetime
from datetime import timedelta
import jwt
import paho.mqtt.client as mqtt
import json
from models.models import *
from utils.utils import checktoken

def cars_full_info():
    if is_local == 1:
        return jsonify({'result':'error, funcio no disponible al edge'})
    data = request.get_json()
    value = checktoken(data['session_token'])
    response = {'value': value['valid']}
    
    if value['valid'] == 'ok':
        coches = camions.find()
        res=([{
            'id_car': doc['id_car'],
            'id_route': doc['id_route'],
            'license_plate': doc['license_plate'],
            'battery': doc['battery'],
            'status_text': doc['status'],
            'status': doc['status_num'],
            'autonomy': doc['autonomy'],
            'capacity': doc['capacity'],
            'last_maintenance_date': doc['last_maintenance_date'],
            'packages': doc['packages'],
            'beehive': doc['beehive'],
            'location_in ': doc['location_in'],
            'location_act': doc['location_act'],
            'location_end': doc['location_end'],
    }for doc in coches])
        return jsonify({'result':'ok','cars':res})
    else:
        return jsonify(response)

def car_pos_info():
    if is_local == 1:
        return jsonify({'result':'error, funcio no disponible al edge'})
    data = request.get_json()
    value = checktoken(data['session_token'])
    response = {'result': value['valid']}

    if response['result'] == 'ok':
        coches = camions.find()
        return jsonify(response, [{
            'id_car': doc['id_car'],
            'latitude ': doc['location_act']['latitude'],
            'longitude': doc['location_act']['longitude'],
        }for doc in coches])

    return jsonify(response)

def list_available_cars():
    if is_local == 1:
        return jsonify({'result':'error, funcio no disponible al edge'})
    data = request.get_json()
    value = checktoken(data['session_token'])
    response = {'result': value['valid']}

    if value['valid'] =='ok':
        coches = camions.find({'status':"waits"})
        response['cars'] = [{
            'id_car': doc['id_car'],
            'status': doc['status'],
            'autonomy': doc['autonomy'],
            'capacity': doc['capacity']
        }for doc in coches]
    return jsonify(response)

def prova_list_available_cars():
    if is_local == 1:
        return jsonify({'result':'error, funcio no disponible al edge'})
    response = {'value': 'cloduy'}
    coches = camions.find({'status':"waits"})
    return jsonify(response, [{
        'id_car': doc['id_car'],
        'latitude ': doc['location_act']['latitude'],
        'longitude': doc['location_act']['longitude'],
    }for doc in coches])




def list_orders_to_send_cars():
    if is_local == 1:
        return jsonify({'result':'error, funcio no disponible al edge'})
    data = request.get_json()
    value = checktoken(data['session_token'])
    if value['valid'] =='ok':
        orderss = orders.find({'state':"ordered"})
        ordersss = []
        for doc in orderss:
            colmena_random_cursor = colmenas.aggregate([{ "$sample": { "size": 1 } }])
            colmena_random = next(colmena_random_cursor, None)
            #colmena_random = colmenas.find_one()
            ordersss.append({
                'order_identifier': doc['order_identifier'],
                'beehive_coords_destiny': {
                    'id_beehive': colmena_random['id_beehive'],
                    'latitude': colmena_random['location_end']['latitude'],
                    'longitude': colmena_random['location_end']['longitude']
                },
                'medicine_list': [{
                    'medicine_identifier': medicine
                } for medicine in doc['meds_list']],
                'date': doc['date'],
                'state': doc['state'],
            })
        return jsonify({
            'result': value['valid'],
            'orders': ordersss})
        # return jsonify({
        #     'result': value['valid'],
        #     'orders': [{
        #         'order_identifier': doc['order_identifier'],
        #         'beehive_destiny': {
                        # doc['colmena']['location_end']mirar api calls A3 i completar con la colmena quando neste en basde de datos
        #         'medicine_list': [{
        #             'medicine_identifier': medicine
        #         } for medicine in doc['meds_list']],
        #         'date': doc['date'],
        #         'state': doc['state'],
        # }for doc in orderss]
        # })
    else:
        response = {'result': value['valid']}
    return jsonify(response)


# def send_order_cars():
#     data = request.get_json()
#     value = checktoken(data['session_token'])
#     if value['valid'] !='ok' or value['type']!='internal':
#         return jsonify({'result': 'tu no pots man'})
# #     for cotxe in data['assignations']:
# 
#         id_car = cotxe['id_car']
#         id_route = cotxe['route']['id_route']

#         coordinates = routes.find({'id_route' : id_route})

#         send_car(id_car, coordinates)

        #Enviar por mqtt a todos los coches el id, las coordenadas, y todo lo necesario que esta dentro de la variable cotxe
#         pass



def send_car(id_car, route):
    if is_local == 1:
        return jsonify({'result':'error, funcio no disponible al edge'})
    # Crea un objeto cliente MQTT
    client = mqtt.Client()

    # Conecta al servidor MQTT
    client.connect("mosquitto", 1883, 60)

    # Crea un mensaje JSON
    mensaje = {    
        "id_car":     id_car,
        "order":     1,
        "route":    0
    }

    mensaje["route"] = route["coordinates"]

    # Codifica el mensaje JSON a una cadena
    mensaje_json = json.dumps(mensaje)

    # Publica el mensaje en el topic "PTIN2023/A1/CAR"
    client.publish("PTIN2023/CAR/STARTROUTE", mensaje_json)

    # Cierra la conexión MQTT
    client.disconnect()


def update_order_cars():
    if is_local == 1:
        return jsonify({'result':'error, funcio no disponible al edge'})
    data = request.get_json()
    value = checktoken(data['session_token'])
    if value['valid'] !='ok' or value['type']!='internal':
        return jsonify({'result': 'tu no pots man'})
    
    # Crea un objeto cliente MQTT
    client = mqtt.Client()

    # Conecta al servidor MQTT
    client.connect("mosquitto", 1883, 60)

    # Crea un mensaje JSON
    mensaje = {    "id_car":     1,
                "order":     1,
                "route":    0}

    # recibido de mapas
    route = {"coordinates" :    "[[1.729895,41.220972],[1.730095,41.220594],[1.730957,41.220821],[1.730341,41.222103],[1.732058,41.222625],[1.732593,41.222967],[1.732913,41.223435],[1.733119,41.224977],[1.733229,41.225046],[1.733257,41.225324],[1.733531,41.225684],[1.73421,41.226188],[1.737807,41.22931],[1.738258,41.229572],[1.738483,41.229682],[1.738329,41.229879],[1.738106,41.229798],[1.738094,41.22967],[1.737657,41.22918],[1.737265,41.228995],[1.736156,41.228027],[1.735887,41.227883],[1.735424,41.228285]]",
            "type":            "LineString"}

    mensaje["route"] = route["coordinates"]
    logging.info()
    # Codifica el mensaje JSON a una cadena
    mensaje_json = json.dumps(mensaje)

    # Publica el mensaje en el topic "PTIN2023/A1/CAR"
    client.publish("PTIN2023/DRON/STARTROUTE", mensaje_json)

    # Cierra la conexión MQTT
    client.disconnect()
    return jsonify({'result':'ok'})

