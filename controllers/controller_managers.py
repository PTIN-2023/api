from flask import jsonify, request
import datetime
from datetime import timedelta
import jwt
from models.models import *
from utils.utils import checktoken
import json


OK = 'ok'
INTERNAL = 'internal'

def list_all_orders():
    data = request.get_json()
    orders_per_page = data['orders_per_page']
    page = data['page']
    value = checktoken(data['session_token']) #checkeo si el usuario de la sesion tiene token
    if value['valid'] == 'ok': #si tiene token
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/list_all_orders"
            return requests.post(url, json=data).json()
        user_email = value['email']
        es_manager = users.find_one({'user_email': user_email})
        role_persona = es_manager['user_role']
        if role_persona == 'manager':
            te_orders = orders.find({}) #miro si tiene alguna receta
            te_orders_list = list(te_orders)
            if len(te_orders_list) > 0:
                response = []
                for te_order in te_orders_list:  # Para cada orden encontrada
                    meds_list = te_order['meds_list']
                    meds_details = []
                    for med_code in meds_list: #para cada medicamento de med_list
                        med_query = {'national_code': str(med_code)}
                        med_result = farmacs.find_one(med_query) #lo busco en farmacs

                        if med_result:  #guardo todo y lo meto en la array que se devolverá al final
                            med_result['_id'] = str(med_result['_id'])
                            meds_details.append(med_result)
                            
                    responses = {
                                'order_identifier': te_order['order_identifier'], 
                                'patient_email': te_order['patient_email'],
                                'medicine_list': meds_details,
                                'date': te_order['date'],
                                'state': te_order['state']
                    }
                    response.append(responses)
                response = {'result': 'ok', 'orders': response, 'page': page, 'orders_per_page': orders_per_page}
                
            else:
                response = {'result': 'Aquest pacient no té cap ordre'}       
        else:
             response = {'result': 'No ets manager, no pots revisar els ordres', 'rol': role_persona}    
    else:
        response = {'result': 'No tienes token para poder comprobar esto, espabila'}
        
    return jsonify(response)

def manager_list_doctors():
    data = request.get_json()
    value = checktoken(data['session_token'])
    
    if value['valid'] != OK or value['type'] != INTERNAL:
        response = {'result': 'unvalid token'}
    
    else:
        user_email = value['email']
        es_manager = users.find_one({'user_email': user_email})
        role_persona = es_manager['user_role']
        if role_persona == 'manager':
            patient_users = users.find({'user_role': 'patient'})
            patients = []
            
            for user in patient_users:
                patient_data = {
                    'user_full_name': user['user_full_name'],
                    'user_email': user['user_email'],
                    'user_phone': user['user_phone'],
                    'user_city': user['user_city']
                }
                
                patients.append(patient_data)
            
            response = {'result': 'ok', 'patients': patients}
        
        else:
            response = {'result': 'No ets manager, no pots revisar els ordres'}
        
    return jsonify(response)

# def manager_assign_doctors():
#     data = request.get_json()
#     value = checktoken(data['session_token'])
#     patient_id = data['patient_id']
    
#     if value['valid'] != OK or value['type'] != INTERNAL:
#         return jsonify({'result': 'unvalid token'})
    
#     else: 
#         user_email = value['email']
#         es_manager = users.find_one({'user_email': user_email})
#         role_persona = es_manager['user_role']
#         if role_persona == 'manager':
#             #nse donde asignarlo en BD 🤧
#             response = {'result': 'ok'} 
#         else:
#             response = {'result': 'No ets manager, no pots revisar els ordres'}
    
#     return jsonify(response)


# def stats():
#     data = request.get_json()
#     value = checktoken(data['session_token'])
    
#     if value['valid'] != OK or value['type'] != INTERNAL:
#         return jsonify({'result': 'unvalid token'})
    
#     else:
#         account_stats = []
#         topCities = []
#         yearOrders = []
#         topMeds = []
#         sellsComparation = []
        
#         response = {'result': 'ok', 
#                     'accounts_stat': account_stats,
#                     'topSeller_cities': topCities,
#                     'year_orders': yearOrders,
#                     'topSeller_meds': topMeds,
#                     'sells_comparation': sellsComparation}
        
#         return jsonify(response)