from controllers.controller_user import *
from controllers.controller_pacients import *
from controllers.controller_meds import *
from controllers.controller_cotxes import *
from controllers.controller_mqtt import *
from controllers.controller_routes import *
from controllers.controller_drones import *
from controllers.controller_orders import *
from controllers.controller_paypal import *


def routes_user(app):
    app.route("/api/login", methods=['POST'])(login)
    app.route("/api/register", methods=['POST'])(register)
    app.route("/api/manager_create_account", methods=['POST'])(register_premium)
    app.route("/api/checktoken", methods=['POST'])(check_token)
    app.route("/api/user_info", methods=['POST'])(get_user_info)
    app.route("/api/logout", methods=['POST'])(logout)
    app.route("/api/set_user_info", methods=['POST'])(set_user_info)
    
def routes_meds(app):
    app.route("/api/list_available_medicines", methods=['POST'])(search_farmacs)
    
def routes_pacients(app):
    app.route("/api/has_prescription", methods=['POST'])(has_prescription)
    app.route("/api/get_prescription_meds", methods=['POST'])(get_prescription_meds)
    app.route("/api/list_patient_orders", methods=['POST'])(list_patient_orders)
    app.route("/api/list_all_orders", methods=['POST'])(list_all_orders)
    app.route("/api/num_pages_patient_orders", methods=['POST'])(num_pages_patient_orders)
    app.route("/api/make_order",methods=['POST'])(make_order)
    app.route("/api/cancel_patient_order", methods=['POST'])(cancel_order)
    

def routes_orders(app):
    app.route("/api/doctor_confirm_order",methods=['POST'])(doctor_confirm_order)
    app.route("/api/list_doctor_approved_confirmations",methods=['POST'])(list_doctor_approved_confirmations)
    app.route("/api/list_doctor_pending_confirmations",methods=['POST'])(list_doctor_pending_confirmations)
    app.route("/api/confirm_patient_order",methods=['POST'])(confirm_patient_order)
    app.route("/api/cancel_patient_order",methods=['POST'])(cancel_patient_order)
    app.route("/api/check_order",methods=['POST'])(check_order)
    app.route("/api/num_pages_doctor_pending_confirmations",methods=['POST'])(num_pending_confirmations)
    app.route("/api/num_pages_doctor_approved_confirmations",methods=['POST'])(num_approved_confirmations)


def routes_cotxes(app):
    app.route("/api/cars_full_info", methods=['POST'])(cars_full_info)
    app.route("/api/cars_pos_info", methods=['POST'])(car_pos_info)
    app.route("/api/list_available_cars", methods=['POST'])(list_available_cars)
    app.route("/api/update_order_cars", methods=['POST'])(update_order_cars)
    #app.route("/api/send_order_cars", methods=['POST'])(send_order_cars)#############################Ya está en rutas
    app.route("/api/list_orders_to_send_cars", methods=['POST'])(list_orders_to_send_cars)
    app.route("/api/prova_list_available_cars", methods=['GET','POST'])(prova_list_available_cars)

def routes_drones(app):
    app.route("/api/drones_full_info", methods=['POST'])(drons_full_info)
    app.route("/api/drones_pos_info", methods=['POST'])(drons_pos_info)
    app.route("/api/send_order_drones", methods=['POST'])(send_order_drones)
    app.route("/api/list_order_to_set_drones", methods=['POST'])(list_order_to_set_drones)
    app.route("/api/list_available_drones", methods=['POST'])(list_available_drones)
    app.route("/api/beehives_local", methods=['POST'])(beehives_local)

def routes_routes(app):
    app.route("/api/store_route", methods=['POST'])(store_route)
    app.route("/api/get_route", methods=['POST'])(get_route)
    app.route("/api/general_storage_pos", methods=['POST'])(general_storage_pos)
    app.route("/api/send_order_cars", methods=['POST'])(send_order_cars)
    
def routes_mqtt(app):
    app.route("/api/mqtt", methods=['POST'])(mqtt)
    app.route("/api/UPDATELOCATION", methods=['POST'])(UPDATELOCATION)#nidea del hastag la verdad
    app.route("/api/UPDATESTATUS", methods=['POST'])(UPDATESTATUS)#nidea del hastag la verdad
    app.route("/api/TOCLOUD_UPDATESTATUS", methods=['POST'])(TOCLOUD_UPDATESTATUS)#nidea del hastag la verdad
    app.route("/api/TOCLOUD_UPDATELOCATION", methods=['POST'])(TOCLOUD_UPDATELOCATION)#nidea del hastag la verdad

def routes_paypal(app):
    app.route("/api/create_payment", methods=['POST'])(create_payment)
    app.route("/api/execute_payment", methods=['GET'])(execute_payment)
 
def routes_proves(app):
    app.route("/api/list_orders_to_send_cars", methods=['POST'])(proves)   
