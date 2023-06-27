from flask import jsonify, request
from models.models import *
from utils.utils import checktoken, check_token_manager, quantity_available_user
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import json

def search_farmacs():
    data = request.get_json()
    token = data['session_token']
    logging.info(token)
    check = check_token_manager(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/list_available_medicines"
            return requests.post(url, json=data).json()
        query = {}
        if 'filter' in data:
            try:
                filter_data = data['filter']
                if 'med_name' in filter_data:
                    query['med_name'] = {'$regex': filter_data['med_name']}
                if 'pvp_min' in filter_data:
                    query['pvp'] = {'$gte': float(filter_data['pvp_min'])}
                if 'pvp_max' in filter_data:
                    if 'pvp' in query:
                        query['pvp']['$lte'] = float(filter_data['pvp_max'])
                    else:
                        query['pvp'] = {'$lte': float(filter_data['pvp_max'])}
                if 'prescription_needed' in filter_data:
                    if True == filter_data['prescription_needed']:
                        query['prescription_needed'] = {'$eq': True}
                    if False == filter_data['prescription_needed']:
                        query['prescription_needed'] = {'$eq': False}
                if 'form' in filter_data:
                    query['form'] = {'$in': filter_data['form']}
                if 'type_of_administration' in filter_data:
                    query['type_of_administration'] = {'$in': filter_data['type_of_administration']}
                medNum = int(filter_data['meds_per_page'])
                page = int(filter_data['page'])
             # Calculem el límit inferior i superior de medicaments a obtenir segons la pàgina i el número de medicaments per pàgina
                limit_inf = (page - 1) * medNum
             # Executem la query amb els límits especificats
                results = farmacs.find(query).limit(medNum).skip(limit_inf)
            except Exception as e:
                results = str(e)
    # Si no es proporciona un filtre, es retornen tots els medicaments
        else:
            results = farmacs.find()
        res=[{
            'medicine_identifier':  doc['national_code'],
            'medicine_name': doc['med_name'],
            'national_code': doc['national_code'],
            'use_type': str(doc['use_type']) + '€',
            'type_of_administration': doc['type_of_administration'],
            'prescription_needed': doc['prescription_needed'],
            'pvp': doc['pvp'],
            'form': doc['form'],
            'excipients': doc['excipients'],
            'form': doc['form'],
            'medicine_image_url': doc['medicine_image_url'],
            'quantity_available': doc['quantity_available']
        } for doc in results]
        return jsonify({"result":"ok","medicines":res})
    else:
        response = {'result': 'error', 'message': check['valid']}    #VALIDA EL CHECK
        return jsonify(response)
    
def search_client_farmacs():
    data = request.get_json()
    token = data['session_token']
    logging.info(token)
    check = checktoken(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/list_available_medicines"
            return requests.post(url, json=data).json()
        query = {}
        if 'filter' in data:
            try:
                filter_data = data['filter']
                if 'med_name' in filter_data:
                    query['med_name'] = {'$regex': filter_data['med_name']}
                if 'pvp_min' in filter_data:
                    query['pvp'] = {'$gte': float(filter_data['pvp_min'])}
                if 'pvp_max' in filter_data:
                    if 'pvp' in query:
                        query['pvp']['$lte'] = float(filter_data['pvp_max'])
                    else:
                        query['pvp'] = {'$lte': float(filter_data['pvp_max'])}
                if 'prescription_needed' in filter_data:
                    if True == filter_data['prescription_needed']:
                        query['prescription_needed'] = {'$eq': True}
                    if False == filter_data['prescription_needed']:
                        query['prescription_needed'] = {'$eq': False}
                if 'form' in filter_data:
                    query['form'] = {'$in': filter_data['form']}
                if 'type_of_administration' in filter_data:
                    query['type_of_administration'] = {'$in': filter_data['type_of_administration']}
                medNum = int(filter_data['meds_per_page'])
                page = int(filter_data['page'])
             # Calculem el límit inferior i superior de medicaments a obtenir segons la pàgina i el número de medicaments per pàgina
                limit_inf = (page - 1) * medNum
             # Executem la query amb els límits especificats
                results = farmacs.find(query).limit(medNum).skip(limit_inf)
            except Exception as e:
                results = str(e)
    # Si no es proporciona un filtre, es retornen tots els medicaments
        else:
            results = farmacs.find()
        res=[{
            'medicine_identifier':  doc['national_code'],
            'medicine_name': doc['med_name'],
            'national_code': doc['national_code'],
            'use_type': str(doc['use_type']) + '€',
            'type_of_administration': doc['type_of_administration'],
            'prescription_needed': doc['prescription_needed'],
            'pvp': doc['pvp'],
            'form': doc['form'],
            'excipients': doc['excipients'],
            'form': doc['form'],
            'medicine_image_url': doc['medicine_image_url'],
            'quantity_available': quantity_available_user(doc['national_code'], check['email'])
        } for doc in results]
        return jsonify({"result":"ok","medicines":res})
    else:
        response = {'result': 'error', 'message': check['valid']}    #VALIDA EL CHECK
        return jsonify(response)
    
def num_search_farmacs():
    data = request.get_json()
    token = data['session_token']
    logging.info(token)
    check = check_token_manager(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/list_available_medicines"
            return requests.post(url, json=data).json()
        query = {}
        if 'filter' in data:
            try:
                filter_data = data['filter']
                if 'med_name' in filter_data:
                    query['med_name'] = {'$regex': filter_data['med_name']}
                if 'pvp_min' in filter_data:
                    query['pvp'] = {'$gte': float(filter_data['pvp_min'])}
                if 'pvp_max' in filter_data:
                    if 'pvp' in query:
                        query['pvp']['$lte'] = float(filter_data['pvp_max'])
                    else:
                        query['pvp'] = {'$lte': float(filter_data['pvp_max'])}
                if 'prescription_needed' in filter_data:
                    if True == filter_data['prescription_needed']:
                        query['prescription_needed'] = {'$eq': True}
                    if False == filter_data['prescription_needed']:
                        query['prescription_needed'] = {'$eq': False}
                if 'form' in filter_data:
                    query['form'] = {'$in': filter_data['form']}
                if 'type_of_administration' in filter_data:
                    query['type_of_administration'] = {'$in': filter_data['type_of_administration']}
             # Executem la query amb els límits especificats
                results = farmacs.count_documents(query)
            except Exception as e:
                results = str(e)
    # Si no es proporciona un filtre, es retornen tots els medicaments
        else:
            results = farmacs.count_documents()
        return jsonify({"result":"ok","num": results})
    else:
        response = {'result': 'error', 'message': check['valid']}    #VALIDA EL CHECK
        return jsonify(response)
    
def num_search_client_farmacs():
    data = request.get_json()
    token = data['session_token']
    logging.info(token)
    check = checktoken(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/list_available_medicines"
            return requests.post(url, json=data).json()
        query = {}
        if 'filter' in data:
            try:
                filter_data = data['filter']
                if 'med_name' in filter_data:
                    query['med_name'] = {'$regex': filter_data['med_name']}
                if 'pvp_min' in filter_data:
                    query['pvp'] = {'$gte': float(filter_data['pvp_min'])}
                if 'pvp_max' in filter_data:
                    if 'pvp' in query:
                        query['pvp']['$lte'] = float(filter_data['pvp_max'])
                    else:
                        query['pvp'] = {'$lte': float(filter_data['pvp_max'])}
                if 'prescription_needed' in filter_data:
                    if True == filter_data['prescription_needed']:
                        query['prescription_needed'] = {'$eq': True}
                    if False == filter_data['prescription_needed']:
                        query['prescription_needed'] = {'$eq': False}
                if 'form' in filter_data:
                    query['form'] = {'$in': filter_data['form']}
                if 'type_of_administration' in filter_data:
                    query['type_of_administration'] = {'$in': filter_data['type_of_administration']}
             # Executem la query amb els límits especificats
                results = farmacs.count_documents(query)
            except Exception as e:
                results = str(e)
    # Si no es proporciona un filtre, es retornen tots els medicaments
        else:
            results = farmacs.count_documents()
        return jsonify({"result":"ok","num": results})
    else:
        response = {'result': 'error', 'message': check['valid']}    #VALIDA EL CHECK
        return jsonify(response)

def get_meds_prescription():
    data = request.get_json()
    token = data['session_token']
    logging.info(token)
    check = checktoken(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/list_available_medicines"
            return requests.post(url, json=data).json()
        medicine_list = recipes.find_one({'prescription_identifier': data['prescription_identifier']})['meds_list']
        list = []
        for doc in medicine_list:
            medicament = farmacs.find_one({'national_code': doc[0]})
            list.append({
                'medicine_identifier': medicament['national_code'],
                'medicine_image_url': medicament['medicine_image_url'],
                'medicine_name': medicament['med_name'],
                'excipient': medicament['excipients'],
                'pvp': medicament['pvp'],
                'contents': medicament['contents'],
                'prescription_needed': medicament['prescription_needed'],
                'form': medicament['form'],
                'type_of_administration': medicament['type_of_administration'],
            })
        response = {'result': 'ok', 'medicine_list': list}
    else:
        response = {'result': 'error', 'message': check['valid']}    #VALIDA EL CHECK
    return jsonify(response)


#ESTA PARA PROBAR DEJARLO
# def search_farmacs():
#     data = request.get_json()
#     token = data['session_token']
#     check = checktoken(token)
#     if check['valid'] == 'yes':
#         query = {}
#         results = farmacs.find()
#         res=[{
#             'medicine_identifier':  doc['national_code'],
#             'medicine_name': doc['med_name'],
#             'national_code': doc['national_code'],
#             'use_type': str(doc['use_type']) + '€',
#             'type_of_administration': doc['type_of_administration'],
#             'prescription_needed': doc['prescription_needed'],
#             'pvp': doc['pvp'],
#             'form': doc['form'],
#             'excipients': doc['excipients'],
#             'form': doc['form'],
#             'medicine_image_url': "https://picsum.photos/200",
#         } for doc in results]
#         return jsonify({"result":"ok","medicines":res})
#     else:
#         response = {'result': 'error', 'message': check['valid']}    #VALIDA EL CHECK
#         return jsonify(response)
