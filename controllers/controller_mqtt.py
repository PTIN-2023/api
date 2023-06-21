from flask import jsonify, request
from pymongo.errors import PyMongoError

# Models
from models.models import orders
from models.models import camions
from models.models import drons

import logging
logging.basicConfig(level = logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Return status
OK      = { 'value': "ok" }
FAILED  = { 'value': "fail" }

# CAR / ORDER STATUS

CAR_DELIVERING = 3
ORDER_CAR_SENT = 3
CAR_SENT = 'car_sent'

# Dudas -> Joa
# Filtra el coche con id = id_car y actualiza todos los campos especificados
def UPDATELOCATION():

    data = request.get_json()
    update_fields = {
        'location_act'  :   data['location_act'],
        'status'        :   data['status'],
        'battery'       :   data['battery'],
        'autonomy'      :   data['autonomy'],
        'status_num'    :   data['status_num']
    }

    try:
        result = camions.update_one(
            {'id_car'   : data['id_car']}, 
            {'$set'     : update_fields }
        )

        if result.modified_count > 0:
            logging.info("Documento actualizado correctamente.")
            return jsonify(OK), 200
        
        else:
            logging.info("UPDATELOCATION | El documento no se actualizó. Puede que no se encontrara el id_car especificado.")
            return jsonify(FAILED), 404
    
    except PyMongoError as e:
        logging.error("Ocurrió un error al actualizar el documento:", str(e))
        return jsonify(FAILED), 500


# Dudas -> Joa
# Actualiza el estado del coche con id = id_car
# En caso de estado:
#   3 : se actualizan todos los pedidos que transporta el coche al estado ORDER_CAR_SENT
def UPDATESTATUS():
    
    data = request.get_json()
    update_fields = {
        'status'        : data['status'],
        'status_num'    : data['status_num']
    }
    
    try:
        result = camions.update_one(
            {'id_car'   : data['id_car']},
            {'$set'     : update_fields }  
        )   

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

        if result.modified_count * response.modified_count > 0:
            logging.info("Documento actualizado correctamente")
            return jsonify(OK), 200
        
        else:
            logging.info("UPDATELOCATION | El documento no se actualizó. Puede que no se encontrara el id_car / order_identifier especificado.")
            return jsonify(FAILED), 404
            
    except PyMongoError as e:
        logging.error("Ocurrió un error al actualizar el documento:", str(e))
        return jsonify(FAILED), 500




# FUNCIONES DRON!!!! FALTA ACABARLAS!!
def TOCLOUD_UPDATELOCATION():
    data = request.get_json()
    update_fields = {
        'location_act'  :   data['location_act'],
        'status'        :   data['status'],
        'battery'       :   data['battery'],
        'autonomy'      :   data['autonomy'],
        'status_num'    :   data['status_num']
    }

    try:
        result = drons.update_one(
            {'id_dron'   : data['id_dron']}, 
            {'$set'     : update_fields }
        )

        if result.modified_count > 0:
            logging.info("Documento actualizado correctamente.")
            return jsonify(OK), 200
        
        else:
            logging.info("drones | El documento no se actualizó. Puede que no se encontrara el id_dron especificado.")
            return jsonify(FAILED), 404
    
    except PyMongoError as e:
        logging.error("Ocurrió un error al actualizar el documento:", str(e))
        return jsonify(FAILED), 500

def TOCLOUD_UPDATESTATUS():
    data = request.get_json()
    update_fields = {
        'status'        : data['status'],
        'status_num'    : data['status_num']
    }
    
    try:
        result = drons.update_one(
            {'id_dron'   : data['id_car']},
            {'$set'     : update_fields }  
        ) 
        if result.modified_count > 0:
            logging.info("Documento actualizado correctamente.")
            return jsonify(OK), 200
        
        else:
            logging.info("drones | El documento no se actualizó. Puede que no se encontrara el id_dron especificado.")
            return jsonify(FAILED), 404
    except PyMongoError as e:
        logging.error("Ocurrió un error al actualizar el documento:", str(e))
        return jsonify(FAILED), 500