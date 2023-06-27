from flask import jsonify, request
from pymongo.errors import PyMongoError
import os, requests, json

from utils.utils import get_url_edge

# Models
from models.models import orders
from models.models import camions
from models.models import drons
from models.models import is_local, cloud_api

import logging
logging.basicConfig(level = logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Return status
OK      = { 'value': "ok" }
FAILED  = { 'value': "fail" }

# CAR / ORDER STATUS

CAR_WAITS = 5
CAR_UNLOADING = 2
CAR_DELIVERING = 3
ORDER_CAR_SENT = 3
CAR_SENT = 'car_sent'

DRON_DELIVERING = 3
ORDER_DRON_SENT = 4
DRON_SENT = 'dron_sent'

DRON_WAITING = 4
ORDER_DELIVERED_AWAITING = 5
DELIVERED_AWAITING = 'delivered_awaiting'

DRON_DELIVERED = 9
ORDER_DELIVERED = 6
DELIVERED = 'delivered'

DRON_NOT_DELIVERED = 10
ORDER_DELIVERY_FAILED = 7
DELIVERY_FAILED = 'delivery_failed'

# Dudas -> Joa
# Filtra el coche/dron con id = id_car/id_dron y actualiza todos los campos especificados
def update_location():

    data = request.get_json()
    update_fields = {
        'location_act'  :   data['location_act'],
        'status'        :   data['status'],
        'battery'       :   data['battery'],
        'autonomy'      :   data['autonomy'],
        'status_num'    :   data['status_num']
    }

    try:

        if is_local == 0:
            result = camions.update_one(
                {'id_car'   : data['id_car']}, 
                {'$set'     : update_fields }
            )

        else:
            result = drons.update_one(
                {'id_dron'  : data['id_dron']},
                {'$set'     : update_fields}
            )

        if result.modified_count > 0:
            logging.info("Documento actualizado correctamente.")
            return jsonify(OK), 200
        
        else:
            logging.info("UPDATELOCATION | El documento no se actualizó. Puede que no se encontrara el id_car/id_dron especificado.")
            return jsonify(FAILED), 404
        
    except PyMongoError as e:
        logging.error("Ocurrió un error al actualizar el documento:", str(e))
        return jsonify(FAILED), 500


# Dudas -> Joa
# Actualiza el estado del coche con id = id_car
# En caso de estado:
#   2 : se copian todos los pedidos a la colmena destino y la bd orders del edge correspondiente
#   3 : se actualizan todos los pedidos que transporta el coche al estado ORDER_CAR_SENT
def update_status():
    
    data = request.get_json()
    update_fields = {
        'status'        : data['status'],
        'status_num'    : data['status_num']
    }
    
    try:

        # cars
        if is_local == 0:

            result = camions.update_one(
                {'id_car'   : data['id_car']},
                {'$set'     : update_fields }  
            )   

            # update status orders transported by car <id_car>
            if data['status_num'] == CAR_DELIVERING:

                orders_car = camions.find_one(
                    {'id_car'       : data['id_car']}, 
                    {'packages'     : 1}
                )
                orders_car = orders_car["packages"]

                for order in orders_car:

                    update_fields = {
                        'state'     : CAR_SENT,
                        'state_num' : ORDER_CAR_SENT
                    }
                    response = orders.update_one(
                        { 'order_identifier' : order['order_identifier'] }, 
                        { '$set'             : update_fields } 
                    )

                    if response.modified_count > 0:
                        logging.info("ORDER | Documento actualizado correctamente")

                    else:
                        logging.info("ORDER | El documento no se actualizó. Puede que no se encontrara el order_identifier especificado.")
            
            # copy orders transported by car <id_car> to edge db            
            elif data['status_num'] == CAR_UNLOADING:
                
                orders_car = camions.find_one(
                    {'id_car'       : data['id_car']}, 
                    {'packages'     : 1}
                )
                orders_car = orders_car["packages"]

                full_orders = []
                for order in orders_car:
                    full_orders.append(orders.find_one(
                        { 'order_identifier' : order['order_identifier'] }
                    ))
                
                id_beehive = camions.find_one({ 'id_car' : data['id_car'] })['beehive']
                payload = {
                    "session_token" : 'internal',
                    "id_beehive"    : id_beehive,
                    "orders"        : full_orders,
                }

                payloadJSON = json.dumps(payload, default=str)
                edge_api = get_url_edge(id_beehive)

                if edge_api != -1:
                    url = edge_api + "/api/unload_car"
                    response = requests.post(url, json=payloadJSON)
                    
                    if response.status_code == 200:
                        return jsonify(OK), 200
                    else:
                        logging.info("update_status | /api/unload_car failed")
                        return jsonify(FAILED), 500
                
                else:
                    logging.info("update_status | No se ha encontrado la colmena en el edge")
                    return jsonify(FAILED), 404
                
            # remove id_route from car <id_car> at the end of the route
            elif data['status_num'] == CAR_WAITS:
                
                update_fields = { 'id_route'  : -1 }
                result = camions.update_one(
                    {'id_car'   : data['id_car']},
                    {'$set'     : update_fields }  
                )
                
                if result.modified_count > 0:
                    logging.info("update_car | Documento actualizado correctamente")

                else:
                    logging.info("update_car | El documento no se actualizó. Puede que no se encontrara el id_car especificado.")

            
            if result.modified_count:
                logging.info("CAR | Documento actualizado correctamente")
                return jsonify(OK), 200
            
            else:
                logging.info("update_status | El documento no se actualizó. Puede que no se encontrara el id_car especificado.")
                return jsonify(FAILED), 404

        # drons  
        else:

            result = drons.update_one(
                {'id_dron'  : data['id_dron']},
                {'$set'     : update_fields }  
            )

            order_dron = drons.find_one(
                { 'id_dron'          : data['id_dron'] }, 
                { 'order_identifier' : 1 }
            )
            # 1 order per dron
            order_identifier = order_dron["order_identifier"]

            if data['status_num'] == DRON_DELIVERING:
                res = update_status_cloud_edge(DRON_SENT, ORDER_DRON_SENT, order_identifier)
                
                if res == 'ok':
                    return jsonify(OK), 200
                else:
                    return jsonify(FAILED), 404

            if data['status_num'] == DRON_WAITING:
                res = update_status_cloud_edge(DELIVERED_AWAITING, ORDER_DELIVERED_AWAITING, order_identifier)
                
                if res == 'ok':
                    return jsonify(OK), 200
                else:
                    return jsonify(FAILED), 404
                
            if data['status_num'] == DRON_DELIVERED:
                res = update_status_cloud_edge(DELIVERED, ORDER_DELIVERED, order_identifier)
                
                if res == 'ok':
                    return jsonify(OK), 200
                else:
                    return jsonify(FAILED), 404
                
            if data['status_num'] == DRON_NOT_DELIVERED:
                res = update_status_cloud_edge(DELIVERY_FAILED, ORDER_DELIVERY_FAILED, order_identifier)
                
                if res == 'ok':
                    return jsonify(OK), 200
                else:
                    return jsonify(FAILED), 404
                
            else:
                if result.modified_count:
                    logging.info("DRON | Documento actualizado correctamente")
                    return jsonify(OK), 200
                
                else:
                    logging.info("update_status | El documento no se actualizó. Puede que no se encontrara el id_dron especificado.")
                    return jsonify(FAILED), 404
                

    except PyMongoError as e:
        logging.error("Ocurrió un error al actualizar el documento:", str(e))
        return jsonify(FAILED), 500


def update_status_cloud_edge(state, state_num, order_identifier):

    # --- UPDATE ORDERS DB EDGE ----- #

    update_fields = {
        'state'     : state,
        'state_num' : state_num
    }
    response = orders.update_one(
        { 'order_identifier' : order_identifier }, 
        { '$set'             : update_fields } 
    )
    if response.modified_count > 0:
        logging.info("ORDER | EDGE | Documento actualizado correctamente")
    else:
        logging.info("ORDER | EDGE |  El documento no se actualizó. Puede que no se encontrara el order_identifier especificado.")

    # --- UPDATE ORDERS DB CLOUD ----- #

    payload = {
        'session_token'     : 'internal',
        'order_identifier'  : order_identifier,
        'state'             : state,
        'state_num'         : state_num
    }
    url = cloud_api + "/api/update_status_order"
    response = requests.post(url, json=payload).json()

    if response['result'] == 'ok':
        logging.info("ORDER | CLOUD | Documento actualizado correctamente")
    else:
        logging.info("ORDER | CLOUD | El documento no se actualizó. Puede que no se encontrara el order_identifier especificado.")

    return response['result'] 