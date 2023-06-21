from flask import jsonify, request
import datetime
from datetime import timedelta
import jwt
from models.models import *
from utils.utils import checktoken
import paho.mqtt.client as mqtt
import json
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')    

#si hay dudas -> david
#EL CHECKTOKEN SE HACE PREVIO A TOD0 EL RESTO

# Comentarios Jaume: Done 👌
# Prescripction_given y prescription_needed tienen que ser true o false.
# El token se tiene que comprobar antes de nada
# Si el token no es valid el result debe ser diferente a ok. Por ejemplo: "unvalid token" o algo así.

def has_prescription():
    data = request.get_json()
    value = checktoken(data['session_token'])
    if value['valid'] == 'ok': #entro si la persona que esta en la web tiene token
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
def get_prescription_meds():
    data = request.get_json()
    value = checktoken(data['session_token']) #checkeo si el usuario de la sesion tiene token
    if value['valid'] == 'ok': #si tiene token
        #busco si existe receta para el valor importado
        prescription_identifier = data['prescription_identifier']
        query = {'prescription_identifier': prescription_identifier}
        result = recipes.find_one(query) 
        
        if result: #si hay receta devuelvo los medicamentos
            meds_list = result['meds_list']
            meds_details = []

            for med_code in meds_list: #para cada medicamento de med_list
                med_query = {'national_code': str(med_code)}
                med_result = farmacs.find_one(med_query) #lo busco en farmacs
                
                if med_result:  #guardo todo y lo meto en la array que se devolverá al final
                    med_result['_id'] = str(med_result['_id'])
                    meds_details.append(med_result)
            
            response = {'result': 'ok', 'meds_details': meds_details}
            return jsonify(response)
        
        else: #si no hay receta lo notifico
            response = {'result' :'No hi ha recepta per aquest valor'}
            return jsonify(response)
    else:
        response = {'result': 'No tienes token para poder comprobar esto, espabila'}
        return jsonify(response)

#si hay dudas -> david  
def list_patient_orders():
    data = request.get_json()
    orders_per_page = data['orders_per_page']
    logging.info("##################################" + data['session_token'] + "#########################")
    page = data['page']
    value = checktoken(data['session_token']) #checkeo si el usuario de la sesion tiene token
    if value['valid'] == 'ok': #si tiene token
        patient_email = value['email'] #cojo el mail de la persona 
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
                # Encapsulate the list in a JSONObject and add other properties if needed
            response = {'result': 'success', 'orders': response, 'page': page, 'orders_per_page': orders_per_page}
        
        else:
            response = {'result': 'Aquest pacient no té cap ordre'}
    else:
        response = {'result': 'No tienes token para poder comprobar esto, espabila'}
        
    return jsonify(response)


def list_all_orders():
    data = request.get_json()
    orders_per_page = data['orders_per_page']
    logging.info("##################################" + data['session_token'] + "#########################")
    page = data['page']
    value = checktoken(data['session_token']) #checkeo si el usuario de la sesion tiene token
    if value['valid'] == 'ok': #si tiene token
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


def num_pages_patient_orders():
    data = request.get_json()
    orders_per_page = data['orders_per_page']
    logging.info("##################################" + data['session_token'] + "#########################")
    value = checktoken(data['session_token']) #checkeo si el usuario de la sesion tiene token
    if value['valid'] == 'ok': #si tiene token
        patient_email = value['email'] #cojo el mail de la persona 
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
            paginated_response, number_of_pages = paginate(response, orders_per_page)
            
            response = {'result': 'ok', 'data': paginated_response, 'number_of_pages': number_of_pages}
        
        else:
            response = {'result': 'Aquest pacient no té cap ordre'}
    else:
        response = {'result': 'Invalid token'}
        
    return jsonify(response)

def paginate(data, items_per_page):
    paginated_data = []
    total_pages = (len(data) + items_per_page - 1) // items_per_page  # calcular el número total de páginas
    
    for page in range(total_pages):
        start = page * items_per_page
        end = start + items_per_page
        paginated_data.append(data[start:end])
    
    return paginated_data, total_pages

#si hay dudas -> david
def make_order():
    data = request.get_json()
    value = checktoken(data['session_token'])
    if value['valid'] == 'ok':
        meds_list = data['medicine_identifiers']
        patient_identifier = value['email'] #cojo el mail de la persona
        meds_final = []
        
        conReceta = False 
        
        for med_code in meds_list: #se revisa si el input es correcto
            med_query = {'national_code': str(med_code)}
            med_result = farmacs.find_one(med_query) #lo busco en farmacs
            
            if med_result: 
                response = {'result': 'vas bien'}
                prescription_needed = med_result.get('prescription_needed', False)
                if prescription_needed: #si el medicamento necesita receta
                    #mirar si el user tiene receta para este med
                    prescription_given = recipes.find_one({'patient_identifier': patient_identifier}) #miro si tiene alguna receta
                    med_nationalCode = med_result['national_code']
                    if prescription_given and med_nationalCode in prescription_given['meds_list']:   
                        meds_final.append(med_result)
                        conReceta = True
                    else:
                        response = {'result': 'No ho pot fer, no té recepta per un dels medicaments', 'medicament del qual no té recepta': med_nationalCode}
                        return jsonify(response)
                else: #el medicamento no necesita receta
                    meds_final.append(med_result)
                    response = {'result': 'no tiene receta'}
            else:
                response = {'result': 'El input no son medicamentos'}
                return jsonify(response)
        
        #order_identifier empieza con 0 si es una receta
        #order_identifier empieza con 1 si es una receta
        
        if conReceta:
            max_order = orders.find_one(
                            {"order_identifier": {"$regex": "^0"}, "order_identifier": {"$ne": "0"}},
                            sort=[("order_identifier", -1)],
            )
            
            if max_order:
                last_identifier = max_order["order_identifier"]
                rest_of_value = int(last_identifier[1:])
                new_identifier = "0" + str(rest_of_value + 1)
            else:
                new_identifier = "01" 
                
        else:
            max_order = orders.find_one(
                            {"order_identifier": {"$regex": "^1"}, "order_identifier": {"$ne": "1"}},
                            sort=[("order_identifier", -1)],
            )
            
            if max_order:
                last_identifier = max_order["order_identifier"]
                rest_of_value = int(last_identifier[1:])
                new_identifier = "1" + str(rest_of_value + 1)
            else:
                new_identifier = "10"
        
        
        entry = {
            "order_identifier": new_identifier,
            "patient_email": patient_identifier,
            "approved": "yes",
            "reason": "-",
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "state": "awaiting_confirmation",
            "state_num": 1,
            "meds_list": meds_list
        }
        
        send_car()
        
        try:
            id = orders.insert_one(entry).inserted_id
            response = {'result': 'ok'}
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


