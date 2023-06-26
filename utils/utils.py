from datetime import datetime, timedelta
from flask import request
from models.models import *
from geopy.geocoders import Nominatim

def checktoken(token):
    if(token==""):
        token=request.get_json()['token']
    if(token=="internal"):
        return {'valid':'ok', 'type':'internal'}
    user_data = sessio.find_one({'token': token})
    if user_data is None:
        response = {'valid': 'None1'}
    else:
        user = users.find_one({'user_email': user_data['user_email']})
        if user is None:
            response = {'valid': 'None2'}
        elif datetime.now() <= (datetime.strptime(user_data['data'], '%Y-%m-%dT%H:%M:%S.%f') + timedelta(minutes=50)):
            response = {'valid': 'ok', 'email': user['user_email'], 'type': user["user_role"]}
            sessio.update_one({'token': token}, {'$set': {'data': datetime.now().isoformat()}})
            
        else:
            response = {'valid': 'timeout'}
    return response


def check_token_doctor(token):
    user_data = sessio.find_one({'token': token})
    if user_data is None:
        response = {'valid': 'None1'}
    else:
        user = users.find_one({'user_email': user_data['user_email']})
        if user is None:
            response = {'valid': 'None2'}
            return response
        elif datetime.now() <= (datetime.strptime(user_data['data'], '%Y-%m-%dT%H:%M:%S.%f') + timedelta(minutes=50)):
            if user['user_role'] == 'doctor':
                response = {'valid': 'ok', 'email': user['user_email'], 'type': user["user_role"]}
            else:
                response = {'valid': 'error', 'description': 'No ets doctor'}
        else:
            response = {'valid': 'error', 'description': 'timeout'}
    return response

def checktokenv2():
    # Define the query to find the document
    query = {'user_email': 'valor'}

    # Sort the documents in ascending order based on the "data" field
    sort_criteria = [('data', ASCENDING)]

    # Find the document with the earliest "data" value
    document = sessio.find_one(query, sort=sort_criteria)
    if document:
        return {'existe': 'si'}
    else:
        return {'existe':'0'}

def get_coordinates(address):
    geolocator = Nominatim(user_agent="geo_locator")
    location = geolocator.geocode(address)
    if location is None:
        return None
    else:
        return location.latitude, location.longitude

