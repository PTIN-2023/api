from flask import jsonify, request
from datetime import timedelta, datetime
import jwt
from models.models import *
from utils.utils import checktoken
import logging
from pymongo import UpdateOne
    
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')    


def login():
    data = request.get_json()
    user_email = data['user_email']
    user_password = data['user_password']
    doc = users.find_one({'user_email': user_email})
    if doc and doc['user_password'] == user_password:
        token = jwt.encode({'username': user_email}, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), algorithm='HS256')
        response = {'result': 'ok', 'user_given_name': doc['user_given_name'], 'user_role': doc['user_role'], 'user_picture': "No tenim imatge", 'user_token': token}
        entry = {
            "token": token,
            "data": datetime.now().isoformat(),
            "user_email": user_email,
        }
        res = sessio.insert_one(entry)
        return jsonify(response)
    else:
        response = {'result': 'error', 'message': 'Credenciales inválidas'}
        return jsonify(response)

def logout():
    data = request.get_json()
    try:
        sessio.delete_one({'token': data['session_token']})
        response = {'result': 'ok'}
    except pymongo.errors.DuplicateKeyError as description_error:
        response = {'result': 'error', 'description': str(description_error)}
    return jsonify(response)


def register():
    data = request.get_json()
    entry = {
        "user_full_name": data['user_full_name'],
        "user_given_name": data['user_given_name'],
        "user_role": "patient",
        "user_email": data['user_email'],
        "user_phone": data['user_phone'],
        "user_city": data['user_city'],
        "user_address": data['user_address'],
        "user_password": data['user_password'],
        "when": datetime.now(),
    }
    try:
        id = users.insert_one(entry).inserted_id
        token = jwt.encode({'username': entry['user_email']}, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), algorithm='HS256')
        token_entry = {
            "token": token,
            "data": datetime.now().isoformat(),
            "user_email": entry['user_email'],
        }
        res = sessio.insert_one(token_entry)
        response = {'result': 'ok', 'session_token': token}
    except pymongo.errors.DuplicateKeyError as description_error:
        response = {'result': 'error', 'description': str(description_error)}
    return jsonify(response)


def register_premium():
    data = request.get_json()
    entry = {
        "user_full_name": data['user_full_name'],
        "user_given_name": data['user_given_name'],
        "user_role": "patient",
        "user_email": data['user_email'],
        "user_phone": data['user_phone'],
        "user_city": data['user_city'],
        "user_address": data['user_address'],
        "user_password": data['user_password'],
        "user_role": data['user_role'],
        "when": datetime.now(),
    }
    try:
        id = users.insert_one(entry).inserted_id
        token = jwt.encode({'username': entry['user_email']}, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), algorithm='HS256')
        token_entry = {
            "token": token,
            "data": datetime.now().isoformat(),
            "user_email": entry['user_email'],
        }
        res = sessio.insert_one(token_entry)
        response = {'result': 'ok', 'session_token': token}
    except pymongo.errors.DuplicateKeyError as description_error:
        response = {'result': 'error', 'description': str(description_error)}
    return jsonify(response)


# def google():
#     data = request.get_json()
#     user_google = data['user_google_token']
#     #No es suficiente este token, falta info
#     entry = {
#             "user_full_name": data['user_full_name'],
#             "user_given_name": data['user_given_name'],
#             "user_email": data['user_email'],
#             "user_phone": data['user_phone'],
#             "user_city": data['user_city'],
#             "user_address":data['user_address'],
#             "user_password": data['user_password'] ,
#             "when": datetime.datetime.now(),
#     }
#     try:
#         id = users.insert_one(entry).inserted_id
#         response = {'result': 'ok'}
#         #Falta token aquí, añadir en response
#     except pymongo.errors.DuplicateKeyError as description_error:
#          response = {'result': 'error',
# 		     'description': str(description_error)}
#     #response = {'result': 'ok'}
#     return jsonify(response)


def get_user_info():
    data = request.get_json()
    token = data['token']
    check = checktoken(token)
    if check['valid'] == 'ok':
        doc = users.find_one({'user_email': check['email']})
        response = {'result': 'ok', 'user_given_name': doc['user_given_name'], 'user_role': doc['user_role'], 'user_full_name': doc['user_full_name'], 'user_email': doc['user_email'], 'user_phone': doc['user_phone'], 'user_city': doc['user_city'], 'user_address': doc['user_address'], 'user_picture': "No tenim imatge", 'user_token': token}
        return jsonify(response)
    else:
        response = {'result': 'error', 'message': check['valid']}
    return jsonify(response)


def check_token():
    data = request.get_json()
    token = data['token']
    check = checktoken(token)
    return jsonify(check)


def set_user_info():
    data = request.get_json()
    token = data['token']
    check = checktoken(token)
    if check['valid'] == 'ok':
        # Obtain values
        user_email = check['email']
        user_full_name = data['user_full_name']
        user_given_name = data['user_given_name']
        user_email = data['user_email']
        user_phone = data['user_phone']
        user_city = data['user_city']
        user_address = data['user_address']
        
        # Update values
        update_operations = [
            UpdateOne({'user_email': user_email},
                      {'$set': {
                          'user_full_name': user_full_name,
                          'user_given_name': user_given_name,
                          #'user_email': user_email,
                          'user_phone': user_phone,
                          'user_city': user_city,
                          'user_address': user_address
                      }})
        ]
        users.bulk_write(update_operations)

        response = {'result': 'ok'}

        return jsonify(response)
    else:
        response = {'result': 'Token invàlid'}
    
    
