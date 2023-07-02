from flask import jsonify, request
from datetime import timedelta, datetime
import jwt
from models.models import *
from utils.utils import checktoken, check_token_doctor, get_coordinates, get_closest_beehive
import logging
from pymongo import UpdateOne
from unidecode import unidecode
    
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')    

OK = 'ok'
INTERNAL = 'internal'
USER_DOES_NOT_EXITS = "L'usuari no existeix!"

def login():
    data = request.get_json()
    user_email = data['user_email']
    if is_local == 1:
        url = cloud_api+"/api/login"
        response = requests.post(url, json=data).json()
        if response['result'] != 'ok':
            return response
        token = jwt.encode({'username': user_email}, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), algorithm='HS256')
        response['user_token'] = token
        entry = {
            "token": token,
            "data": datetime.now().isoformat(),
            "user_email": user_email,
        }
        sessio.insert_one(entry)
        return response
    user_password = data['user_password']
    doc = users.find_one({'user_email': user_email})
    if doc and doc['user_password'] == user_password:
        token = jwt.encode({'username': user_email}, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), algorithm='HS256')
        response = {'result': 'ok', 'user_given_name': doc['user_given_name'], 'user_role': doc['user_role'], 'user_picture': "https://picsum.photos/200", 'user_token': token}
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
    user_email = data['user_email']
    if is_local == 1:
        url = cloud_api+"/api/register"
        response = requests.post(url, json=data).json()
        if response['result'] != 'ok':
            return response
        url = cloud_api+"/api/logout"
        data2 = {
            'session_token': response['session_token']
        }
        requests.post(url, json=data2).json()
        token = jwt.encode({'username': user_email}, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), algorithm='HS256')
        response['session_token'] = token
        entry = {
            "token": token,
            "data": datetime.now().isoformat(),
            "user_email": user_email,
        }
        sessio.insert_one(entry)
        return response
    user_coordinates = get_coordinates(data['user_address'] + " , " + data['user_city'])
    if user_coordinates is None:
        #Parlar amb A3 sobre qué fer. direcció no vàlida. result != ok i mostrar error?
        response = {'result': 'error', 'description': "No es poden trobar les coordenades de la direcció"}
        return jsonify(response)
    else:
        user_latitude, user_longitude = user_coordinates
        city_lowercase_no_accents = unidecode(data['user_city']).lower()
        beehive_latitude, beehive_longitude = get_closest_beehive(city_lowercase_no_accents,user_latitude,user_longitude)
        entry = {
            "user_full_name": data['user_full_name'],
            "user_given_name": data['user_given_name'],
            "user_role": "patient",
            "user_email": user_email,
            "user_phone": data['user_phone'],
            "user_city": data['user_city'],
            "user_address": data['user_address'],
            "user_password": data['user_password'],
            "when": datetime.now(),
            "user_coordinates": {
                "latitude": user_latitude,
                "longitude": user_longitude
            },
            "beehive_coordinates": {
                "latitude": beehive_latitude,
                "longitude": beehive_longitude
            }
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
    user_email = data['user_email']
    if is_local == 1:
        url = cloud_api+"/api/manager_create_account"
        response = requests.post(url, json=data).json()
        if response['result'] != 'ok':
            return response
        url = cloud_api+"/api/logout"
        data2 = {
            'session_token': response['session_token']
        }
        requests.post(url, json=data2).json()
        token = jwt.encode({'username': user_email}, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), algorithm='HS256')
        response['session_token'] = token
        entry = {
            "token": token,
            "data": datetime.now().isoformat(),
            "user_email": user_email,
        }
        sessio.insert_one(entry)
        return response
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


def get_user_info():
    
    data    = request.get_json()
    token   = data['session_token']
    check   = checktoken(token)
    
    if check['valid'] == 'ok':
        
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api + "/api/user_info"
            return requests.post(url, json=data).json()
        
        doc = users.find_one({'user_email' : check['email']})
        response = {
            'result'            : 'ok', 
            'user_given_name'   : doc['user_given_name'], 
            #edad?
            'user_role'         : doc['user_role'], 
            'user_full_name'    : doc['user_full_name'],
            'user_email'        : doc['user_email'],
            'user_password'     : doc['user_password'],
            'user_phone'        : doc['user_phone'],
            'user_city'         : doc['user_city'],
            'user_address'      : doc['user_address'],
            'user_picture'      : "https://picsum.photos/200",
            'user_token'        : token
        }
        
        return jsonify(response)
    
    else:
        response = {'result': 'error', 'message': check['valid']}
    
    return jsonify(response)


def get_user_position():

    data = request.get_json()
    value = checktoken(data['session_token']) 
    response = { 'value' : value['valid'] }

    if value['valid'] == OK:
            
        if is_local == 1:
            data['session_token'] = INTERNAL
            url = cloud_api + "/api/user_position"
            return requests.post(url, json=data).json()

        doc = users.find_one({'user_email' : data['user_email']})
        if doc != None:
            return jsonify({
                'result'                : OK,
                'user_coordinates'      : doc['user_coordinates'],
                'beehive_coordinates'   : doc['beehive_coordinates']
            })
        else:
            response['result'] = USER_DOES_NOT_EXITS
    
    return jsonify(response)



def info_clients_for_doctor():
    data = request.get_json()
    token = data['session_token']
    check = check_token_doctor(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/info_clients_for_doctor"
            return requests.post(url, json=data).json()
        doc = users.find_one({'user_full_name': data['user_full_name']})
        response = {'result': 'ok', 'user_given_name': doc['user_given_name'], 'user_role': doc['user_role'], 'user_full_name': doc['user_full_name'], 'user_email': doc['user_email'], 'user_phone': doc['user_phone'], 'user_city': doc['user_city'], 'user_address': doc['user_address'], 'user_picture': "https://picsum.photos/200", 'user_token': token}
        return jsonify(response)
    else:
        response = {'result': 'error', 'message': check['valid']}
    return jsonify(response)

def check_token():
    data = request.get_json()
    token = data['session_token']
    check = checktoken(token)
    return jsonify(check)


def set_user_info():
    data = request.get_json()
    token = data['session_token']
    check = checktoken(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/set_user_info"
            return requests.post(url, json=data).json()
        # Obtain values
        user_email = check['email']
        user_full_name = data['user_full_name']
        user_given_name = data['user_given_name']
        user_email = data['user_email']
        user_password=data['user_password']
        user_phone = data['user_phone']
        user_city = data['user_city']
        user_address = data['user_address']
        
       #user_coordinates = get_coordinates(data['user_address'] + " , " + data['user_city'])
        #if user_coordinates is None:
            #Parlar amb A3 sobre qué fer. direcció no vàlida. result != ok i mostrar error?
         #   response = {'result': 'error', 'description': "No es poden trobar les coordenades de la direcció"}
          #  return jsonify(response)
        #else:
        #    user_latitude, user_longitude = user_coordinates
         #   city_lowercase_no_accents = unidecode(data['user_city']).lower()
          #  beehive_latitude, beehive_longitude = get_closest_beehive(city_lowercase_no_accents,user_latitude,user_longitude)   
            # Update values
        update_operations = [
            UpdateOne({'user_email': user_email},
                    {'$set': {
                        'user_full_name': user_full_name,
                        'user_given_name': user_given_name,
                        # 'user_coordinates': {
                        #    'longitude': user_longitude,
                        #    'latitude': user_latitude
                        #},
                        #'beehive_coordinates': {
                         #   'longitude': beehive_longitude,
                          #  'latitude': beehive_latitude
                        #},
                        'user_email':user_email,
                        'user_phone': user_phone,
                        'user_password':user_password,
                        'user_city': user_city,
                        'user_address': user_address        
                    }})
            ]
        users.bulk_write(update_operations)

        response = {'result': 'ok'}

        return jsonify(response)
    else:
        response = {'result': 'Token invàlid'}
        
        
