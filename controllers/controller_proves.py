from flask import jsonify, request
import datetime
from datetime import timedelta
import jwt
from models.models import *
from utils.utils import checktoken
import paho.mqtt.client as mqtt
import json
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')    

import requests

def proves():
    if is_local == 1:
        return jsonify({'result':'error, funcio no disponible al edge'})
    drons = drones.find()
    cotxes = camions.find()

    drons_data = [{
        'id_dron': doc['id_dron'],
        'battery': doc['battery'],
    } for doc in drons]

    cotxes_data = [{
        'id_car': doc['id_car'],
        'license_plate': doc['license_plate'],
    } for doc in cotxes]

    response_data = {
        'drons': drons_data,
        'cotxes': cotxes_data
    }

    return jsonify(response_data)

