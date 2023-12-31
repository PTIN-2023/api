from flask import jsonify, request
import datetime
from datetime import timedelta
import jwt
from models.models import *
from utils.utils import checktoken, prescription_given, add_med, update_recipes, restar_meds, paginate
import paho.mqtt.client as mqtt
import json
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')    


def has_prescription():
    data = request.get_json()
    value = checktoken(data['session_token'])
    if value['valid'] == 'ok': #entro si la persona que esta en la web tiene token
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/has_prescription"
            return requests.post(url, json=data).json()
        medicine_identifier = data['medicine_identifier']
        query = {'national_code': medicine_identifier}
        med_exists = farmacs.find_one(query) #checkeo que el medicamento existe
        
        if med_exists and med_exists['prescription_needed'] == True: #si el medicamento existe y necesita receta
            patient_identifier = value['email'] #cojo el mail de la persona 
            prescription_given = recipes.find_one({'patient_identifier': patient_identifier}) #miro si tiene alguna receta
            if prescription_given and medicine_identifier in prescription_given['meds_list']: #si tiene recetas  
                response = {
                    'result': 'ok', 'prescription_needed': 'true', 'prescription_given': 'true'
                }
            else: #si no tiene recetas
                response = {
                    'result': 'ok', 'prescription_needed': 'true', 'prescription_given': 'false'
                }
            
        else: #si el medicamento no necesita receta
            response = {
                'result': 'ok', 'prescription_needed': 'false', 'prescription_given': 'true'
            }
    
    else: #si la persona que esta intentando mirar sus recetas no tiene token
        response = {
                'result': 'unvalid token', 'prescription_needed': 'false', 'prescription_given': 'false'
        }
    
    return jsonify(response)

#si hay dudas -> david  
def list_patient_orders():
    data = request.get_json()
    orders_per_page = data['orders_per_page']
    page = data['page']
    value = checktoken(data['session_token']) #checkeo si el usuario de la sesion tiene token
    if value['valid'] == 'ok': #si tiene token
        user_email = value['email']
        te_orders = orders.find({'patient_email': user_email}) #miro si tiene alguna receta
        te_orders_list = list(te_orders)
        response_list = []
        if len(te_orders_list) > 0:
            for order in te_orders_list:  # Para cada orden encontrada
                meds_list = order['meds_list']
                meds_details = []
                for med_code in meds_list: #para cada medicamento de med_list
                    if is_local == 1:
                        url = cloud_api+"/api/get_med"
                        data['session_token'] = 'internal'
                        data['national_code'] = str(med_code[0])
                        med_result = requests.post(url, json=data).json()['med_result']
                    else:
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
            
            
            if is_local == 1:
                url = cloud_api+"/api/user_info_internal"
                data['email'] = order['patient_email']
                posicio_final = requests.post(url, json=data).json()
            else:
                posicio_final = users.find_one({'user_email': order['patient_email']})
            if order['state'] == 'dron_sent':
                if is_local == 1:#actual
                    posicio_trobada = drons.find_one({'order_identifier': order['order_identifier']})
                    if posicio_trobada:
                        posicio_act = posicio_trobada['location_act']
                    else:
                        posicio_act = 'Pendent dassignar a un dron'
                    #final
                    carrer = posicio_final['user_address']
                else:
                    posicio_act = 'Està sent repartit pels drons'
                    carrer = posicio_final['user_address']
            
            elif order['state'] == 'car_sent':
                if is_local == 0:#actual
                    logging.info(order['order_identifier'])
                    posicio_trobada = camions.find_one({'packages.order_identifier': order['order_identifier']})
                    if posicio_trobada:
                        posicio_act = posicio_trobada['location_act']
                    else:
                        posicio_act = 'Pendent dassignar a un dron'
                    #final
                    carrer = posicio_final['user_address']
                else:
                    posicio_act = 'Està sent repartit pels cotxes'
                    carrer = posicio_final['user_address']
                
            elif order['state'] == 'delivered':
                posicio_act = posicio_final['user_address']
                carrer = posicio_final['user_address']
            
            else:
                posicio_act = 'Encara no esta confirmat/enviat'
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
        response = {'result': 'No tienes token para poder comprobar esto, espabila'}
        
    return jsonify(response)


def num_pages_patient_orders():
    data = request.get_json()
    orders_per_page = data['orders_per_page']
    value = checktoken(data['session_token']) #checkeo si el usuario de la sesion tiene token
    if value['valid'] == 'ok': #si tiene token
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/num_pages_patient_orders"
            return requests.post(url, json=data).json()
        patient_email = value['email']
        te_orders = orders.find({'patient_email': patient_email}) #miro si tiene alguna receta //comprobar si hay mas de una
        if te_orders:
            #medicaments
            response = []
            for te_order in te_orders:  # Para cada orden encontrada
                meds_list = te_order['meds_list']
                meds_details = []
                for med_code in meds_list: #para cada medicamento de med_list
                    med_query = {'national_code': str(med_code)}
                    med_result = farmacs.find_one(med_query) #lo busco en farmacs

                    if med_result:  #guardo todo y lo meto en la array que se devolverá al final
                        med_result['_id'] = str(med_result['_id'])
                        meds_details.append(med_result)
                        
                responses = {'order_identifier': te_order['order_identifier'], 
                            'medicine_list': meds_details,
                            'date': te_order['date'],
                            'state': te_order['state']
                            }
                
                response.append(responses)
                
            #Paginar
            paginated_response, number_of_pages = paginate(response, int(orders_per_page))
            
            response = {'result': 'ok', 'data': paginated_response, 'number_of_pages': number_of_pages}
        
        else:
            response = {'result': 'Aquest pacient no te cap ordre'}
    else:
        response = {'result': 'Invalid token'}
        
    return jsonify(response)


#si hay dudas -> david
def make_order():
    data = request.get_json()
    logging.info(data)
    value = checktoken(data['session_token'])
    if value['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/make_order"
            return requests.post(url, json=data).json()
        meds_list = data['medicine_identifiers']
        patient_identifier = value['email'] #cojo el mail de la persona
       
        approvation_required = False 
        #prescription_given = recipes.find({'patient_identifier': patient_identifier})
        prescription_list = prescription_given(patient_identifier)
        for ordered_med in meds_list: #se revisa si el input es correcto
            med_result = farmacs.find_one({'national_code': ordered_med[0]}) #lo busco en farmacs
            
            if med_result:
                response = {'result': 'vas bien'}
                if med_result['prescription_needed']:
                    #mirar si el user tiene receta para este med
                    medicament_receptat = False
                    for med in prescription_list:
                            if med[0] == ordered_med[0] and med[1] >= ordered_med[1]:
                                medicament_receptat = True
                                update_recipes(patient_identifier,ordered_med)
                                break
                    if not medicament_receptat:
                        approvation_required = True
            else:
                response = {'result': 'Hay un medicamento no encontrado en la bd'}
                return jsonify(response)

        if approvation_required:
            approved = "pending"
        else:
            approved = "yes"
            restar_meds(meds_list)
        # max_order = orders.find_one({}, sort=[("order_identifier", -1)])
        max_order = orders.find_one({},sort=[("_id", -1)])
        #    
        logging.info(max_order)
        if max_order and len(max_order)>0:
            new_identifier = str(int(max_order["order_identifier"]) + 1)
        else:
            new_identifier = "0"
        print("este max order",max_order)
        print("new id",new_identifier)
        
        entry = {
            "order_identifier": new_identifier,
            "patient_email": patient_identifier,
            "approved": approved,
            "reason": "-",
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "state": "ordered",
            "state_num": 2,
            "meds_list": meds_list
        }
                
        try:
            id = orders.insert_one(entry).inserted_id
            response = {'result': 'ok', "order_identifier" : new_identifier}
        except pymongo.errors.DuplicateKeyError as description_error:
            response = {'result': 'error', 'description': str(description_error)}
    else:
        response = {'result':value}
        #response = {'result': 'No tienes token para poder comprobar esto, espabila'}
    logging.info("LLEGA AQUI!!")
    if(response['result']=="ok" and response['result']=="ok"):
        return jsonify(response)
    else:
        return jsonify({'result':"error en el envio a omar"})
    



def cancel_order():
    data = request.get_json()
    value = checktoken(data['session_token'])
    response = {'value': value['valid']}
    if value['valid'] == 'ok': 
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/cancel_patient_order"
            return requests.post(url, json=data).json()
        order = data['order_identifier']
    response = {'result': ''}
    return jsonify(response)


def send_car():
    # Crea un objeto cliente MQTT
    client = mqtt.Client()

    # Conecta al servidor MQTT
    client.connect("mosquitto", 1883, 60)

    # Crea un mensaje JSON
    mensaje = {    "id_car":     1,
                "order":     1,
                "route":    0}

    # recibido de mapas
    route = {"coordinates" :    """[
    [41.220972, 1.729895],
    [41.220594, 1.730095],
    [41.220821, 1.730957],
    [41.222103, 1.730341],
    [41.222625, 1.732058],
    [41.222967, 1.732593],
    [41.223435, 1.732913],
    [41.224977, 1.733119],
    [41.225046, 1.733229],
    [41.225324, 1.733257],
    [41.225684, 1.733531],
    [41.226188, 1.73421],
    [41.22931, 1.737807],
    [41.229572, 1.738258],
    [41.229682, 1.738483],
    [41.229879, 1.738329],
    [41.229798, 1.738106],
    [41.22967, 1.738094],
    [41.22918, 1.737657],
    [41.228995, 1.737265],
    [41.228027, 1.736156],
    [41.227883, 1.735887],
    [41.228285, 1.735424]
]""",
            "type":            "LineString"}

    mensaje["route"] = route["coordinates"]

    # Codifica el mensaje JSON a una cadena
    mensaje_json = json.dumps(mensaje)

    # Publica el mensaje en el topic "PTIN2023/A1/CAR"
    client.publish("PTIN2023/CAR/STARTROUTE", mensaje_json)

    # Cierra la conexión MQTT
    client.disconnect()



