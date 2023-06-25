from flask import jsonify, request
from pymongo.errors import PyMongoError
import os

# Models
from models.models import orders
from models.models import camions
from models.models import drons

import logging
logging.basicConfig(level = logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

is_local = int(os.environ.get('IS_LOCAL'))

# Return status
OK      = { 'value': "ok" }
FAILED  = { 'value': "fail" }

# CAR / ORDER STATUS

CAR_WAITS = 5
CAR_UNLOADING = 1
CAR_DELIVERING = 3
ORDER_CAR_SENT = 3
CAR_SENT = 'car_sent'

# Dudas -> Joa
# Filtra el coche con id = id_car y actualiza todos los campos especificados
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
#   3 : se actualizan todos los pedidos que transporta el coche al estado ORDER_CAR_SENT
def update_status():
    
    data = request.get_json()
    update_fields = {
        'status'        : data['status'],
        'status_num'    : data['status_num']
    }
    
    try:

        if is_local == 0:

            result = camions.update_one(
                {'id_car'   : data['id_car']},
                {'$set'     : update_fields }  
            )   

            if result.modified_count:
                logging.info("CAR | Documento actualizado correctamente")
            
            else:
                logging.info("update_status | El documento no se actualizó. Puede que no se encontrara el id_car especificado.")
                return jsonify(FAILED), 404

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

                for order in orders_car:

                    full_orders = orders.find_one({ 'order_identifier' : order['order_identifier'] })
                    

            
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
                    logging.info("update_car | El documento no se actualizó. Puede que no se encontrara el order_identifier especificado.")
            
        return jsonify(OK), 200

            
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