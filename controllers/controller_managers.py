from flask import jsonify, request
from models.models import *
from utils.utils import checktoken


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
    
    if value['valid'] != 'ok':
        response = {'result': 'Unvalid token'}
    
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
            
            doctor_users = users.find({'user_role': 'doctor'})
            doctors = []
            
            for doctor in doctor_users:
                doctor_data = {
                    'user_full_name': doctor['user_full_name'],
                    'user_email': doctor['user_email'],
                    'user_phone': doctor['user_phone'],
                    'user_city': doctor['user_city']
                }
                
                doctors.append(doctor_data)
            
            response = {'result': 'ok', 'patients': patients, 'doctors': doctors}
        
        else:
            response = {'result': 'No ets manager, no pots revisar els ordres'}
        
    return jsonify(response)


def list_assigned_doctors():
    data = request.get_json()
    value = checktoken(data['session_token'])
    doctor_email = data['doctor_email']
    
    if value['valid'] != 'ok':
        response = {'result': 'Unvalid token'}
    
    else: 
        user_email = value['email']
        es_manager = users.find_one({'user_email': user_email})
        role_persona = es_manager['user_role']
        if role_persona == 'manager':
            list_patients = []
            patients = doctor.find({'doctor_email': doctor_email})
            
            for patient in patients:
                patient_email = patient['patients_email']
                
                patient_user = users.find_one({'user_email': patient_email})
                
                patient_data = {
                    'user_full_name': patient_user['user_full_name'],
                    'user_email': patient_user['user_email'],
                    'user_phone': patient_user['user_phone'],
                    'user_city': patient_user['user_city']
                }

                list_patients.append(patient_data)
            
            response = {'result': 'ok', 'patients': list_patients} 
        else:
            response = {'result': 'No ets manager, no pots revisar els ordres'}
    
    return jsonify(response)

def manager_assign_doctors():
    data = request.get_json()
    value = checktoken(data['session_token'])
    doctor_email = data['doctor_email']
    patient_email = data['patient_email']
    
    if value['valid'] != 'ok':
        response = {'result': 'Unvalid token'}
    
    else: 
        user_email = value['email']
        es_manager = users.find_one({'user_email': user_email})
        role_persona = es_manager['user_role']
        if role_persona == 'manager':
            doctor_te_assignats = doctor.find_one({'doctor_email': doctor_email})
            if doctor_te_assignats: #el doctor ja tenia a un pacient assignat
                patients_email = doctor_te_assignats.get('patients_email', [])
                if patient_email in patients_email:
                    response = {'result': 'El doctor ja te assignat a aquest pacient'}
                else:
                    patients_email.append(patient_email)
                    
                    doctor.update_one(
                        {'doctor_email': doctor_email},
                        {'$set': {'patients_email': patients_email}}
                    )
                
            else: #el doctor no tenia cap pacient assignat
               nova_assignacio = {
                    'doctor_email': doctor_email,
                    'patients_email': [patient_email]
               }
               
               doctor.insert_one(nova_assignacio)
                
            response = {'result': 'ok'} 
        
        else:
            response = {'result': 'No ets manager, no pots revisar els ordres'}
    
    return jsonify(response)


def delete_assignations_doctor():
    data = request.get_json()
    value = checktoken(data['session_token'])
    doctor_email = data['doctor_email']
    patient_email = data['patient_email']
    
    if value['valid'] != 'ok':
        response = {'result': 'Token inválido'}
    
    else: 
        user_email = value['email']
        es_manager = users.find_one({'user_email': user_email})
        role_persona = es_manager['user_role']
        
        if role_persona == 'manager':
            doctor_te_assignats = doctor.find_one({'doctor_email': doctor_email})
            
            if doctor_te_assignats:  # tiene pacientes
                patients_email = doctor_te_assignats.get('patients_email', [])
                
                if patient_email in patients_email:
                    patients_email.remove(patient_email)
                    
                    if len(patients_email) == 0:  # solo tenia a ese paciente
                        doctor.delete_one({'doctor_email': doctor_email})
                    else:  # Había más de un paciente asignado
                        doctor.update_one(
                            {'doctor_email': doctor_email},
                            {'$set': {'patients_email': patients_email}}
                        )
                    
                    response = {'result': 'ok'}
                else:
                    response = {'result': 'El doctor no te aquest pacient assignat'}
            
            else:  #no tenia pacientes
                response = {'result': 'El doctor no te pacients assignats o no existeix'}
        else:
            response = {'result': 'No ets manager, no pots revisar les assignacions'}
    
    return jsonify(response)


def stats():
    data = request.get_json()
    value = checktoken(data['session_token'])
    
    if value['valid'] != 'ok':
        response = {'result': 'Unvalid token'}
    
    else: 
        num_patients = users.count_documents({'user_role': 'patient'})
        num_doctor = users.count_documents({'user_role': 'doctor'})
        num_manager = users.count_documents({'user_role': 'manager'})
        
        #hardcodeado ya que no tenemos suficiente informacion
        response = {
                    "result": "ok",
                    "accounts_stat": {
                        "stat_type": "accounts_stat_query",
                        "accounts_stat_query": [
                            {
                                "name": "Pacientes",
                                "value": num_patients
                            },
                            {
                                "name": "Medicos",
                                "value": num_doctor
                            },
                            {
                                "name": "Gestores",
                                "value": num_manager
                            }
                        ]
                    },
                    "topSeller_cities": {
                        "stat_type": "topSeller_cities_query",
                        "topSeller_cities_query": [
                            {
                                "name": "Barcelona",
                                "value": 400
                            },
                            {
                                "name": "Martorell",
                                "value": 300
                            },
                            {
                                "name": "Torrelavit",
                                "value": 300
                            },
                            {
                                "name": "Lleida",
                                "value": 200
                            }
                        ]
                    },
                    "year_orders": {
                        "stat_type": "year_orders_query",
                        "year_orders_query": [
                            {
                                "name": "Enero",
                                "maximo": 4000
                            },
                            {
                                "name": "Fabrero",
                                "maximo": 3000
                            },
                            {
                                "name": "Marzo",
                                "maximo": 2000
                            },
                            {
                                "name": "Abril",
                                "maximo": 2780
                            },
                            {
                                "name": "Mayo",
                                "maximo": 1890
                            },
                            {
                                "name": "Junio",
                                "maximo": 2390
                            },
                            {
                                "name": "Julio",
                                "maximo": 3490
                            },
                            {
                                "name": "Septiembre",
                                "maximo": 3490
                            },
                            {
                                "name": "Octubre",
                                "maximo": 3490
                            },
                            {
                                "name": "Noviembre",
                                "maximo": 3490
                            },
                            {
                                "name": "Diciembre",
                                "maximo": 3490
                            }
                        ]
                    },
                    "topSeller_meds": {
                        "stat_type": "topSeller_meds_query",
                        "topSeller_meds_query": [
                            {
                                "name": "Ibuprofeno",
                                "cantidad": 4000
                            },
                            {
                                "name": "Heparina",
                                "cantidad": 3000
                            },
                            {
                                "name": "Dolocatil",
                                "cantidad": 2000
                            },
                            {
                                "name": "Dalsy",
                                "cantidad": 2780
                            },
                            {
                                "name": "Pectoxlisina",
                                "cantidad": 1890
                            },
                            {
                                "name": "Apiretal",
                                "cantidad": 2390
                            },
                            {
                                "name": "Omeprazol",
                                "cantidad": 3490
                            },
                            {
                                "name": "Enantyum",
                                "cantidad": 3490
                            },
                            {
                                "name": "Diazepam",
                                "cantidad": 3490
                            },
                            {
                                "name": "Adiro",
                                "cantidad": 3490
                            },
                            {
                                "name": "Amoxicilina",
                                "cantidad": 3490
                            }
                        ]
                    },
                    "sells_comparation": {
                        "stat_type": "sells_comparation_query",
                        "sells_comparation_query": [
                            {
                                "name": "Enero",
                                "anterior": 4000,
                                "actual": 2400
                            },
                            {
                                "name": "Fabrero",
                                "anterior": 3000,
                                "actual": 1398
                            },
                            {
                                "name": "Marzo",
                                "anterior": 2000,
                                "actual": 9800
                            },
                            {
                                "name": "Abril",
                                "anterior": 2780,
                                "actual": 3908
                            },
                            {
                                "name": "Mayo",
                                "anterior": 1890,
                                "actual": 4800
                            },
                            {
                                "name": "Junio",
                                "anterior": 2390,
                                "actual": 3800
                            },
                            {
                                "name": "Julio",
                                "anterior": 3490,
                                "actual": 4300
                            },
                            {
                                "name": "Septiembre",
                                "anterior": 3490,
                                "actual": 4300
                            },
                            {
                                "name": "Octubre",
                                "anterior": 3490,
                                "actual": 4300
                            },
                            {
                                "name": "Noviembre",
                                "anterior": 3490,
                                "actual": 4300
                            },
                            {
                                "name": "Diciembre",
                                "anterior": 3490,
                                "actual": 4300
                            }
                        ]
                    }
                }
        
    return jsonify(response)