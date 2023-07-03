from flask import jsonify, request
import datetime
from datetime import timedelta
import jwt
from models.models import *
from utils.utils import checktoken, check_token_doctor
import json
import uuid

def doctor_create_prescription():
    data = request.get_json()
    token = data['session_token']
    check = check_token_doctor(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/doctor_create_prescription"
            return requests.post(url, json=data).json()
        entry = {
            'prescription_identifier': data['prescription_identifier'],
            'patient_identifier': users.find_one({'user_full_name': data['user_full_name']})['user_email'],
            'meds_list': data['medicine_list'],  ####################################Esto igual está mal pero és lo que pone en el apicalls, un poco raro y tal
            'duration': data['duration'], 
            'renewal': data['renewal'],
            'last_used': '1970-01-01', 
            'notes': data['notes'] 
        }
        try:
            id = recipes.insert_one(entry).inserted_id
            response = {'result': 'ok'}
        except pymongo.errors.DuplicateKeyError as description_error:
            response = {'result': 'error', 'description': str(description_error)}
    else:
        response = check
    return jsonify(response)

def get_patient_prescription_history():
    data = request.get_json()

    if is_local == 1:
        url = cloud_api+"/api/get_patient_prescription_history"
        return requests.post(url, json=data).json()

    token = data['session_token']
    check = checktoken(token)

    if check['valid'] != 'ok':
        return jsonify(check)

    recipes_list = []

    if check['type'] == 'manager':
        return jsonify({'result': 'managers cannot check presciption history'})

    if check['type'] == 'patient':
        recipes_list = recipes.find({'patient_identifier': check['email']})

        if not recipes_list:
            return jsonify({'result': 'Aquest pacient no té cap ordre'})

    if check['type'] == 'doctor':
        if not 'patient_email' in data:
            return jsonify({'result': 'patient_email missing'})

        recipes_list = recipes.find({'patient_identifier': data['patient_email']})

    prescriptions_list = []
    for recipe in recipes_list:
        prescriptions_list.append({
            'prescription_identifier': recipe['prescription_identifier'],
            'medicine_list': recipe['meds_list'],
            'duration': recipe['duration'], 
            'renewal': recipe['renewal'], 
            'last_used': recipe['last_used'], 
            'notes': recipe['notes']
        })
    doc = users.find_one({'user_email' : check['email']})

    return jsonify({'result': 'ok', 'prescriptions': prescriptions_list,'user_name':doc['user_given_name']})

def get_prescription_identifier():
    data = request.get_json()
    token = data['session_token']
    check = check_token_doctor(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/get_prescription_identifier"
            return requests.post(url, json=data).json()
        max_recipe = recipes.find_one(
                        {"prescription_identifier": {"$regex": "^1"}, "prescription_identifier": {"$ne": "1"}},
                        sort=[("prescription_identifier", -1)],
        )
        if max_recipe:
            prescription_identifier =str(uuid.uuid4()) #str(int(max_recipe["prescription_identifier"])+1)
        else:
            prescription_identifier = "1"
        response = {'result': 'ok', 'prescription_identifier': prescription_identifier}
    else:
        response = check
    return jsonify(response)
    