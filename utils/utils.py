from datetime import datetime, timedelta
from flask import request
from models.models import *
from geopy.geocoders import Nominatim
from math import radians, cos, sin, asin, sqrt

def checktoken(token):
    
    if is_local == 0:

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

    else:
        data = { 'token': token }
        url = cloud_api+"/api/checktoken"
        return requests.post(url, json=data).json()

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

def check_token_manager(token):
    user_data = sessio.find_one({'token': token})
    if user_data is None:
        response = {'valid': 'None1'}
    else:
        user = users.find_one({'user_email': user_data['user_email']})
        if user is None:
            response = {'valid': 'None2'}
            return response
        elif datetime.now() <= (datetime.strptime(user_data['data'], '%Y-%m-%dT%H:%M:%S.%f') + timedelta(minutes=50)):
            if user['user_role'] == 'manager':
                response = {'valid': 'ok', 'email': user['user_email'], 'type': user["user_role"]}
            else:
                response = {'valid': 'error', 'description': 'No ets manager'}
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

def get_distance(lat1, lat2, lon1, lon2):
     
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
      
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371
      
    # calculate the result
    return(c * r)

def get_closest_beehive(city, user_latitude, user_longitude):
    query = {"city": city}
    result = colmenas.find(query)
    colmenass = list(result)
    count = len(colmenass)

    if count == 1:
        colmena = colmenass[0]
        colmena_latitude = colmena['location_end']['latitude']
        colmena_longitude = colmena['location_end']['longitude']
        
        return (colmena_latitude, colmena_longitude)
    
    elif count > 1:
        closest_distance = float('inf')
        closest_colmena = None
        
        for colmena in colmenass:
            colmena_latitude = colmena['location_end']['latitude']
            colmena_longitude = colmena['location_end']['longitude']
            
            distance = get_distance(user_latitude, colmena_latitude, user_longitude, colmena_longitude)
            
            if distance < closest_distance:
                closest_distance = distance
                closest_colmena = (colmena_latitude, colmena_longitude)
        
        if closest_colmena:
            return closest_colmena

def get_url_edge(id_beehive):
    
    if id_beehive in BEEHIVES_EDGE0:
        return edge0_api
    
    elif id_beehive in BEEHIVES_EDGE1:
        return edge1_api
    
    elif id_beehive in BEEHIVES_EDGE2:
        return edge2_api
    
    else:
        return -1

def prescription_given(patient_identifier):
    prescription_given = recipes.find({'patient_identifier': patient_identifier})
    meds = []
    for prescription in prescription_given:
        for med in prescription['meds_list']:
            add_med(meds, med)
    return meds

def add_med(meds, new_med):
    trobat = False
    for med in meds:
        if med[0] == new_med[0]:
            trobat = True
            med[1] += new_med[1]
            break
    if not trobat:
        meds.append(new_med)

def update_recipes(patient_identifier, ordered_med):
    recipes_list = recipes.find({'patient_identifier': patient_identifier})
    for recipe in recipes_list:
        update_needed = False
        for med in recipe['meds_list']:
            if ordered_med[0] == med[0]:
                if ordered_med[1] > med[1]:
                    ordered_med -= med[1]
                    med[1] = 0
                else:
                    med[1] -= ordered_med[1]
                update_needed = True
                break
        if update_needed:
            update_query = {'$set': {'meds_list': recipe['meds_list']}}
            query = {'prescription_identifier': recipe['prescription_identifier']}
            orders.update_one(query, update_query)

def quantity_available_user(national_code, user):
    medicament = farmacs.find_one({'national_code': national_code})
    quant = 0
    if not medicament['prescription_needed']:
        return int(medicament['quantity_available'])
    prescription_given = recipes.find({'patient_identifier': user})
    for prescription in prescription_given:
        for med in prescription['meds_list']:
            if med[0] == national_code:
                quant += med[1]
                break
    return int(min(int(quant),int(medicament['quantity_available'])))

def restar_meds(meds_list):
    for med in meds_list:
        farmac = farmacs.find_one({'national_code': med[0]})
        farmacs.update_one({'national_code': med[0]}, {'$set': {'quantity_available': farmac['quantity_available'] - med[1], 'amount_sold': farmac['amount_sold'] + med[1]}})


def paginate(data, items_per_page):
    paginated_data = []
    total_pages = (len(data) + items_per_page - 1) // items_per_page  # calcular el número total de páginas
    
    for page in range(total_pages):
        start = page * items_per_page
        end = start + items_per_page
        paginated_data.append(data[start:end])
    
    return paginated_data, total_pages