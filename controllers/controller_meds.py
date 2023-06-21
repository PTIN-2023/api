from flask import jsonify, request
from models.models import *
from utils.utils import checktoken
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import json

def search_farmacs():
    data = request.get_json()
    token = data['session_token']
    logging.info(token)
    check = checktoken(token)
    if check['valid'] == 'ok':
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
        } for doc in results]
        return jsonify({"result":"ok","medicines":res})
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
