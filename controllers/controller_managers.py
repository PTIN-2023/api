from flask import jsonify, request
from models.models import *
from utils.utils import checktoken


def list_all_orders():
    data = request.get_json()
    orders_per_page = data['orders_per_page']
    page = data['page']
    value = checktoken(data['session_token']) #checkeo si el usuario de la sesion tiene token
    if value['valid'] == 'ok': #si tiene token
        user_email = value['email']
        es_manager = users.find_one({'user_email': user_email})
        role_persona = es_manager['user_role']
        if role_persona == 'manager':
            te_orders = orders.find({}) #miro si tiene alguna receta
            te_orders_list = list(te_orders)
            response_list = []
            if len(te_orders_list) > 0:
                for order in te_orders_list:  # Para cada orden encontrada
                    meds_list = order['meds_list']
                    meds_details = []
                    for med_code in meds_list: #para cada medicamento de med_list
                        med_query = {'national_code': str(med_code[0])}
                        med_result = farmacs.find_one(med_query) #lo busco en farmacs

                        if med_result:  #guardo todo y lo meto en la array que se devolverá al final
                            med_result = [{
                                'medicine_identifier':  med_result['national_code'],
                                'medicine_name': med_result['med_name'],
                                'national_code': med_result['national_code'],
                                'use_type': str(med_result['use_type']) + '€',
                                'type_of_administration': med_result['type_of_administration'],
                                'prescription_needed': med_result['prescription_needed'],
                                'pvp': med_result['pvp'],
                                'form': med_result['form'],
                                'excipients': med_result['excipients'],
                                'form': med_result['form'],
                                'medicine_image_url': med_result['medicine_image_url'],
                                'amount_sold': med_result['amount_sold'],
                            }, med_code[1]]
                            meds_details.append(med_result)
                            
                    responses = {'order_identifier': order['order_identifier'], 
                                'medicine_list': meds_details,
                                'date': order['date'],
                                'state': order['state']
                                }
                    response_list.append(responses)
                
                if order['state'] == 'dron_sent':
                    if is_local == 1:#actual
                        posicio_trobada = drons.find_one({'status_num': order['state_num']})
                        posicio_act = posicio_trobada['location_act']
                        #final
                        posicio_final = users.find_one({'user_email': order['patient_email']})
                        carrer = posicio_final['user_address']
                    else:
                        posicio_act = 'Està sent repartit pels drons'
                        posicio_final = users.find_one({'user_email': order['patient_email']})
                        carrer = posicio_final['user_address']
                
                elif order['state'] == 'car_sent':
                    if is_local == 0:#actual
                        posicio_trobada = camions.find_one({'status_num': order['state_num']})
                        posicio_act = posicio_trobada['location_act']
                        #final
                        posicio_final = users.find_one({'user_email': order['patient_email']})
                        carrer = posicio_final['user_address']
                    else:
                        posicio_act = 'Està sent repartit pels cotxes'
                        posicio_final = users.find_one({'user_email': order['patient_email']})
                        carrer = posicio_final['user_address']
                    
                elif order['state'] == 'delivered':
                    posicio_final = users.find_one({'user_email': order['patient_email']})
                    carrer, posicio_act = posicio_final['user_address']
                
                else:
                    posicio_act = 'Encara no esta confirmat/enviat'
                    posicio_final = users.find_one({'user_email': order['patient_email']})
                    carrer = posicio_final['user_address']
                
                response = {'result': 'ok', 
                            'orders': response_list, 
                            'page': page, 
                            'orders_per_page': orders_per_page,
                            'location_act': posicio_act,
                            'location_end': carrer
                        }
                
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
        return jsonify({'result': 'Unvalid token'})
    
    if is_local == 1:
        url = cloud_api+"/api/manager_list_doctors"
        return requests.post(url, json=data).json()
    
    if value['type'] != 'internal':
        user_email = value['email']
        es_manager = users.find_one({'user_email': user_email})
        role_persona = es_manager['user_role']

        if (role_persona != 'manager' and role_persona != 'doctor'):
            return jsonify({'result': 'No ets manager, no pots revisar els ordres'})
        
        
    patient_users = users.find({'user_role': 'patient'})
    patients = []
    
    for user in patient_users:
        
        prueba_email = user['user_email']
        print(prueba_email)
        
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
    
    return jsonify({'result': 'ok', 'patients': patients, 'doctors': doctors})


def list_assigned_doctors():
    data = request.get_json()
    value = checktoken(data['session_token'])
    doctor_email = data['doctor_email']
    
    if value['valid'] != 'ok':
        return jsonify({'result': 'Unvalid token'})
    
    if is_local == 1:
        url = cloud_api+"/api/list_assigned_doctors"
        return requests.post(url, json=data).json()
    
    if value['type'] != 'internal':
        user_email = value['email']
        es_manager = users.find_one({'user_email': user_email})
        role_persona = es_manager['user_role']

        if (role_persona != 'manager' and role_persona != 'doctor'):
            return jsonify({'result': 'No ets manager, no pots revisar els ordres'})
        
    list_patients = []
    doctor_list = doctor.find_one({'doctor_email': doctor_email})
    
    if doctor_list:
        patients_email = doctor_list.get('patients_email', [])
        
        for patient in patients_email:
            try:
                print("[list_assigned_doctors]", patient)
                patient_user = users.find_one({'user_email': patient})

                if patient_user:
                    patient_data = {
                        'user_full_name': patient_user.get('user_full_name', ''),
                        'user_email': patient_user.get('user_email', ''),
                        'user_phone': patient_user.get('user_phone', ''),
                        'user_city': patient_user.get('user_city', '')
                    }

                    list_patients.append(patient_data)

            except Exception as e:   
                print(f"Error occurred while processing patient data: {e}")
                return jsonify({'result': f"Error occurred while processing patient data: {e}"})
    
    return jsonify({'result': 'ok', 'patients': list_patients})

def manager_assign_doctors():
    data = request.get_json()
    value = checktoken(data['session_token'])
    doctor_email = data['doctor_email']
    patient_email = data['patient_email']
    
    if value['valid'] != 'ok':
        response = {'result': 'Unvalid token'}
    
    else: 
        if is_local == 1:
            url = cloud_api+"/api/manager_assign_doctors"
            return requests.post(url, json=data).json()
        user_email = value['email']
        es_manager = users.find_one({'user_email': user_email})
        role_persona = es_manager['user_role']
        if role_persona == 'manager':
            doctor_te_assignats = doctor.find_one({'doctor_email': doctor_email})
            if doctor_te_assignats: #el doctor ja tenia a un pacient assignat
                patients_email = doctor_te_assignats.get('patients_email', [])
                
                if patient_email in patients_email:
                    response = {'result': 'El doctor ja te assignat a aquest pacient'}
                    return jsonify(response)
                
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
        response = {'result': 'Unvalid token'}
    
    else: 
        if is_local == 1:
            url = cloud_api+"/api/delete_assignations_doctor"
            return requests.post(url, json=data).json()
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

def get_patient_doctor():
    data = request.get_json()
    value = checktoken(data['session_token'])
    
    if value['valid'] != 'ok':
        response = {'result': 'Unvalid token'}
    
    else:
        if is_local == 1:
            url = cloud_api+"/api/manager_list_doctors"
            return requests.post(url, json=data).json()
        
        patient_email = value['email']
        doctor_encontrado = doctor.find_one({'patients_email': patient_email})
        
        if doctor_encontrado:
            doctor_email = doctor_encontrado['doctor_email']
            doctor_user = users.find_one({'user_email': doctor_email})
            
            if doctor_user:
                doctor_phone = doctor_user['user_phone']
                response = {
                            'result': 'ok',
                            'doctor_phone': doctor_phone,
                            'doctor_email': doctor_email
                }
            else:
                response = {'result': 'El doctor trobat no es troba a la BD Users'}
        else:
            response = {'result': 'No te cap doctor assignat'}
    
    return jsonify(response)


def add_medicine():
    #mirar si es un gestor
    #guardar en bd
    # retronrar resultado funcion, medicine id, medicine name
    data = request.get_json()
    value = checktoken(data['session_token'])
    if value['valid'] != 'ok':
        response = {'result': 'Unvalid token'}
    else: 
        if is_local == 1:
            url = cloud_api+"/api/add_medicine"
            return requests.post(url, json=data).json()
        user_email = value['email']
        es_manager = users.find_one({'user_email': user_email})
        role_persona = es_manager['user_role']
        
        if role_persona == 'manager':
            #es un gestor puede guardar esa medicina en meds
            national_code = data['national_code']
            medicine_image_url = data['medicine_image_url']
            med_name = data['med_name']
            excipients = data['excipients']
            pvp = data['pvp']
            use_type = data['use_type']
            contents = data['contents']
            prescription_needed = data['prescription_needed']
            form = data['form']
            type_of_administration = data['type_of_administration']
            quantity_available = data['quantity_available']


            #guardar en bd si no esta ya puesta en bd 
            #pregunta: això busca si algun dels camps és igual o si tots son iguals?
            #no te molt sentit en cap dels dos casos
            existing_medicine=  None
            existing_medicine = farmacs.find_one({
                "national_code": national_code,
                "medicine_image_url": medicine_image_url,
                "med_name": med_name,
                "excipients": excipients,
                "pvp": pvp,
                "use_type": use_type,
                "contents": contents,
                "prescription_needed": prescription_needed,
                "form": form,
                "type_of_administration": type_of_administration
            })  

            if existing_medicine: #encontrada la medicina
                response={'result': 'Hi ha un medicament amb els mateixos detalls que els entrats'}
                return jsonify(response)
            else:
                medicine_data = {
                "national_code": national_code,
                "medicine_image_url": medicine_image_url,
                "med_name": med_name,
                "excipients": excipients,
                "pvp": pvp,
                "use_type": use_type,
                "contents": contents,
                "prescription_needed": prescription_needed,
                "form": form,
                "type_of_administration": type_of_administration,
                "quantity_available": quantity_available,
                "amount_sold": 0
                }

                result = farmacs.insert_one(medicine_data)
                response={
                    "result":"ok",
                    "medicine_identifier":national_code, #id de la medicina es el national code
                    "medicine_name":med_name
                }         
        else:
            response = {'result': 'No ets manager, no pots revisar les assignacions'}
    
    return jsonify(response)

def update_medicine():
    data = request.get_json()
    token = data['session_token']
    check = checktoken(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            url = cloud_api+"/api/update_medicine"
            return requests.post(url, json=data).json()
    try:
        farmacs.update_one({'national_code': data['national_code']}, {'$set': {'quantity_available': data['quantity_available'], 'pvp': data['pvp']}})
        response = {'result': 'ok'}
    except pymongo.errors.DuplicateKeyError as description_error:
        response = {'result': 'error', 'description': str(description_error)}
    return jsonify(response)

def delete_medicine():
    data = request.get_json()
    token = data['session_token']
    check = checktoken(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            url = cloud_api+"/api/delete_medicine"
            return requests.post(url, json=data).json()
    try:
        farmacs.delete_one({'national_code': data['national_code']})
        response = {'result': 'ok'}
    except pymongo.errors.DuplicateKeyError as description_error:
        response = {'result': 'error', 'description': str(description_error)}
    return jsonify(response)

def stats():
    data = request.get_json()
    value = checktoken(data['session_token'])
    
    if value['valid'] != 'ok':
        response = {'result': 'Unvalid token'}
    
    else: 
        if is_local == 1:
            url = cloud_api+"/api/stats"
            return requests.post(url, json=data).json()
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