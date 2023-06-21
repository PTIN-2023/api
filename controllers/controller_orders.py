
from flask import jsonify, request
import datetime
from datetime import timedelta
import jwt
from models.models import *
from utils.utils import checktoken , check_token_doctor
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def doctor_confirm_order():
    data = request.get_json()
    token = data['session_token']
    check = check_token_doctor(token)
    if check['valid'] == 'ok':
        query = {'order_identifier': data['order_identifier'] }
        order = orders.find_one(query)
        if order is None:
            response = {'valid': 'error', 'description': 'Order not found'}
        else:
            if order['approved'] == '':
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
        medNum = int(data['confirmations_per_page'])
        page = int(data['page'])
        limit_inf = (page - 1) * medNum
        pending_orders = orders.find({'approved': ""}).limit(medNum).skip(limit_inf)
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
        query = {'order_identifier': data['order_identifier'] }
        order = orders.find_one(query)
        if order is None:
            response = {'valid': 'error', 'description': 'Order not found'}
        else:
            if order['patient_email'] == check['email']:
                update_query = {'$set': {'state': 'delivered'}}
                orders.update_one(query, update_query)
                response = {'result': 'ok'}
            else:
                response = {'result': 'error', 'description': 'You are not the owner of the order'}
    else:
        response = check
    return jsonify(response)

def cancel_patient_order():
    data = request.get_json()
    token = data['session_token']
    check = checktoken(token)
    if check['valid'] == 'ok':
        query = {'order_identifier': data['order_identifier'] }
        order = orders.find_one(query)
        if order is None:
            response = {'valid': 'error', 'description': 'Order not found'}
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

def check_order(): #mirar a través del qr
    data = request.get_json()
    value = checktoken(data['session_token']) 
    if value['valid'] == 'ok': 
        order_identifier = data['order_identifier']
        query = {'order_identifier': data['order_identifier']} #buscar si existe el pedido
        order = orders.find_one(query) 
        if order is None:
            response={'result':'Order not found'}
        else:
            if order['patient_email'] == value['email']: #verificar el pedido es con el paciente 
                update_query = {'$set': {'state_num': 5}} #estado 5- es estado final de un pedido ENTREGADO
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
        medNum = int(data['confirmations_per_page'])      
        #orders que faltan para aprobar de ese doctor
        pending_orders_count = orders.count_documents({'approved': ''}) 
        num_pages = (pending_orders_count + medNum - 1) // medNum
        response = {'result': 'ok', 'num_pages': num_pages}
    else:
        response = value
    return jsonify(response)

    
def num_approved_confirmations():
    data = request.get_json()
    value = checktoken(data['session_token']) 
    if value['valid'] == 'ok':
        medNum = int(data['confirmations_per_page'])      
        #orders que ya estan aprobadas ese doctor
        approved_orders_count = orders.count_documents({'doctor_identifier': value['email'], 'approved': 'yes'})
        num_pages = (approved_orders_count + medNum - 1) // medNum
        response = {'result': 'ok', 'num_pages': num_pages}
    else:
        response = value
    return jsonify(response)
