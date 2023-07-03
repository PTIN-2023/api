
from flask import jsonify, request
import datetime
from datetime import timedelta
import jwt
from models.models import *
from utils.utils import checktoken , check_token_doctor
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import json
import paho.mqtt.client as mqtt

OK = 'ok'
ERROR = 'error'
INTERNAL = 'internal'

NOT_AVAILABLE_AT_EDGE   = { 'result': "error, funcio no disponible a l'edge" }

def doctor_confirm_order():
    data = request.get_json()
    token = data['session_token']
    check = check_token_doctor(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/doctor_confirm_order"
            return requests.post(url, json=data).json()
        query = {'order_identifier': data['order_identifier'] }
        order = orders.find_one(query)
        if order is None:
            response = {'valid': 'error', 'description': 'Order not found'}
        else:
            if order['approved'] == 'no':
                update_query = {'$set': {'approved': data['approved'], 'state_num': 2, 'state': 'ordered', 'doctor_identifier': check['email']}}
                if not data['approved']:
                    update_query['$set']['reason'] = data['reason']
                orders.update_one(query, update_query)
                response = {'result': 'ok'}
            else:
                response = {'result': 'error', 'description': 'Order already approved/disapproved'}
    else:
        response = check
    return jsonify(response)


def list_doctor_approved_confirmations():
    data = request.get_json()
    token = data['session_token']
    check = check_token_doctor(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/list_doctor_approved_confirmations"
            return requests.post(url, json=data).json()
        medNum = int(data['confirmations_per_page'])
        page = int(data['page'])
        limit_inf = (page - 1) * medNum
        approved_orders = orders.find({'doctor_identifier': check['email'], 'approved': 'yes'}).limit(medNum).skip(limit_inf)
        list = [{
            'order_identifier': doc['order_identifier'],
            'date': doc['date'],
            'patient_full_name': users.find_one({'user_email': doc['patient_email']})['user_full_name'],
            'medicine_list': [(med, farmacs.find_one({'national_code': med})['med_name']) for med in doc['meds_list']]
        } for doc in approved_orders]
        response = {'result': 'ok', 'orders': list}
    else:
        response = check
    return jsonify(response)

def list_doctor_pending_confirmations():
    data = request.get_json()
    token = data['session_token']
    check = check_token_doctor(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/list_doctor_pending_confirmations"
            return requests.post(url, json=data).json()
        medNum = int(data['confirmations_per_page'])
        page = int(data['page'])
        limit_inf = (page - 1) * medNum
        pending_orders = orders.find({'approved': 'no'}).limit(medNum).skip(limit_inf)
        list = [{
            'order_identifier': doc['order_identifier'],
            'date': doc['date'],
            'patient_full_name': users.find_one({'user_email': doc['patient_email']})['user_full_name'],
            'medicine_list': [(med, farmacs.find_one({'national_code': med})['med_name']) for med in doc['meds_list']]
        } for doc in pending_orders]
        response = {'result': 'ok', 'orders': list}
    else:
        response = check
    return jsonify(response)

def confirm_patient_order():

    data = request.get_json()
    token = data['session_token']
    check = checktoken(token)
    
    if check['valid'] == 'ok':
        
        if is_local == 1:
            url = cloud_api+"/api/confirm_patient_order"
            response = requests.post(url, json=data).json()
            
            if response['result'] == ERROR:
                send_confirmation_to_dron(False, data['order_identifier'])   
            else:
                send_confirmation_to_dron(True, data['order_identifier'])   

            return response
        
        query = {'order_identifier': data['order_identifier'] }
        order = orders.find_one(query)
        if order is None:
            response = {'result': 'error', 'description': 'Order not found'}
        else:
            if order['patient_email'] == check['email']:
                response = {'result': 'ok'}
            else:
                response = {'result': 'error', 'description': 'You are not the owner of the order'}
    else:
        response = check

    return jsonify(response)

# TODO
def cancel_patient_order():
    data = request.get_json()
    token = data['session_token']
    check = checktoken(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            url = cloud_api+"/api/cancel_patient_order"
            return requests.post(url, json=data).json()
        query = {'order_identifier': data['order_identifier'] }
        order = orders.find_one(query)
        if order is None:
            response = {'result': 'error', 'description': 'Order not found'}
        else:
            if order['patient_email'] == check['email']:
                update_query = {'$set': {'state': 'canceled'}}
                orders.update_one(query, update_query)
                response = {'result': 'ok'}
            else:
                response = {'result': 'error', 'description': 'You are not the owner of the order'}
    else:
        response = check
    return jsonify(response)


def send_confirmation_to_dron(confirmed, order_identifier):

    status = 1 if confirmed else 2
        
    dron = drons.find_one({ 'order_identifier' : order_identifier })
    id_dron = dron['id_dron']

    CONFIRMDELIVERY = "PTIN2023/" + topic_city + "/DRON/CONFIRMDELIVERY"

    SERVER = "192.168.80.241" if id_dron == 0 else "mosquitto"

    client = mqtt.Client()
    client.connect(SERVER, 1883, 60)

    msg = {    
        "id_dron"    :   id_dron,
        "status"     :   status
    }
    message = json.dumps(msg)

    client.publish(CONFIRMDELIVERY, message)
    client.disconnect()


def check_order(): #mirar a través del qr
    data = request.get_json()
    value = checktoken(data['session_token']) 
    if value['valid'] == 'ok': 
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/check_order"
            return requests.post(url, json=data).json()
        order_identifier = data['order_identifier']
        query = {'order_identifier': data['order_identifier']} #buscar si existe el pedido
        order = orders.find_one(query) 
        if order is None:
            response={'result':'Order not found'}
        else:
            if order['patient_email'] == value['email']: #verificar el pedido es con el paciente 
                update_query = {'$set': {'state_num': 5, 'state': 'delivered'}} #estado 5- es estado final de un pedido ENTREGADO
                orders.update_one(query, update_query)
                response = {'result': 'ok'}
            else:
                response = {'result': 'You are not the owner of the order'}
    else:
        response = value
    return jsonify(response)

def num_pending_confirmations():
    data = request.get_json()
    value = checktoken(data['session_token']) 
    if value['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/num_pages_doctor_pending_confirmations"
            return requests.post(url, json=data).json()
        medNum = int(data['confirmations_per_page'])      
        #orders que faltan para aprobar de ese doctor
        pending_orders_count = orders.count_documents({'approved': 'no'}) 
        num_pages = (pending_orders_count + medNum - 1) // medNum
        response = {'result': 'ok', 'num_pages': num_pages}
    else:
        response = value
    return jsonify(response)

    
def num_approved_confirmations():
    data = request.get_json()
    value = checktoken(data['session_token']) 
    if value['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/num_pages_doctor_approved_confirmations"
            return requests.post(url, json=data).json()
        medNum = int(data['confirmations_per_page'])      
        #orders que ya estan aprobadas ese doctor
        approved_orders_count = orders.count_documents({'doctor_identifier': value['email'], 'approved': 'yes'})
        num_pages = (approved_orders_count + medNum - 1) // medNum
        response = {'result': 'ok', 'num_pages': num_pages}
    else:
        response = value
    return jsonify(response)


def update_status_order():

    data = request.get_json()
    value = checktoken(data['session_token'])
    response = { 'value' : value['valid'] }

    if value['valid'] == 'ok':
        
        if is_local == 1 and data['session_token'] != 'internal':
            return jsonify(NOT_AVAILABLE_AT_EDGE)

        order_identifier    = data['order_identifier']
        state               = data['state']
        state_num           = data['state_num']

        update_fields = {
            'state'     : state,
            'state_num' : state_num
        }
        result = orders.update_one(
            { 'order_identifier' : order_identifier }, 
            { '$set'             : update_fields } 
        )
        if is_local == 0:
            data['session_token'] = 'internal'
            url = edge0_api+"/api/cancel_patient_order"
            response0 = requests.post(url, json=data).json()
            url = edge1_api+"/api/cancel_patient_order"
            response1 = requests.post(url, json=data).json()
            url = edge2_api+"/api/cancel_patient_order"
            response2 =  requests.post(url, json=data).json()
        
         

        if result.modified_count > 0:
            response = {'result': 'ok', 'respnse0': response0, 'respnse1': response1, 'respnse2': response2
     
        else:
            response['result'] = 'failed'

    else:
        response = value
    
    return jsonify(response)