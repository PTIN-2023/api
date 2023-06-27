from controllers.controller_user import *
from controllers.controller_pacients import *
from controllers.controller_meds import *
from controllers.controller_cotxes import *
from controllers.controller_mqtt import *
from controllers.controller_routes import *
from controllers.controller_drones import *
from controllers.controller_orders import *
from controllers.controller_paypal import *
from controllers.controller_managers import *
from controllers.controller_colmenes import *
from controllers.controller_prescriptions import *


def routes_user(app):
    app.route("/api/login", methods=['POST'])(login)
    app.route("/api/register", methods=['POST'])(register)
    app.route("/api/manager_create_account", methods=['POST'])(register_premium)
    app.route("/api/checktoken", methods=['POST'])(check_token)
    app.route("/api/user_info", methods=['POST'])(get_user_info)
    app.route("/api/logout", methods=['POST'])(logout)
    app.route("/api/set_user_info", methods=['POST'])(set_user_info)
    app.route("/api/user_position", methods=['POST'])(get_user_position)
    
def routes_meds(app):
    app.route("/api/list_available_medicines", methods=['POST'])(search_client_farmacs)
    app.route("/api/list_inventory_meds", methods=['POST'])(search_farmacs)
    app.route("/api/list_available_medicines_num", methods=['POST'])(num_search_client_farmacs)
    app.route("/api/list_inventory_meds_num", methods=['POST'])(num_search_farmacs)
    app.route("/api/get_meds_prescription", methods=['POST'])(get_meds_prescription)
    
def routes_pacients(app):
    app.route("/api/has_prescription", methods=['POST'])(has_prescription)
    app.route("/api/get_prescription_meds", methods=['POST'])(get_meds_prescription)
    app.route("/api/list_patient_orders", methods=['POST'])(list_patient_orders)
    app.route("/api/num_pages_patient_orders", methods=['POST'])(num_pages_patient_orders)
    app.route("/api/make_order",methods=['POST'])(make_order)
    app.route("/api/cancel_patient_order", methods=['POST'])(cancel_order)
    
def routes_managers(app):
    app.route("/api/list_all_orders", methods=['POST'])(list_all_orders)
    app.route("/api/manager_list_doctors", methods=['POST'])(manager_list_doctors)
    app.route("/api/list_assigned_doctors", methods=['POST'])(list_assigned_doctors)
    app.route("/api/manager_assign_doctors", methods=['POST'])(manager_assign_doctors)
    app.route("/api/delete_assignations_doctor", methods=['POST'])(delete_assignations_doctor)
    app.route("/api/stats", methods=['POST'])(stats)
    app.route("/api/add_medicine", methods=['POST'])(add_medicine)
    app.route("/api/update_medicine", methods=['POST'])(update_medicine)


def routes_prescriptions(app):
    app.route("/api/doctor_create_prescription", methods=['POST'])(doctor_create_prescription)
    app.route("/api/get_patient_prescription_history", methods=['POST'])(get_patient_prescription_history)

def routes_orders(app):
    app.route("/api/doctor_confirm_order",methods=['POST'])(doctor_confirm_order)
    app.route("/api/list_doctor_approved_confirmations",methods=['POST'])(list_doctor_approved_confirmations)
    app.route("/api/list_doctor_pending_confirmations",methods=['POST'])(list_doctor_pending_confirmations)
    app.route("/api/confirm_patient_order",methods=['POST'])(confirm_patient_order)
    app.route("/api/cancel_patient_order",methods=['POST'])(cancel_patient_order)
    app.route("/api/check_order",methods=['POST'])(check_order)
    app.route("/api/num_pages_doctor_pending_confirmations",methods=['POST'])(num_pending_confirmations)
    app.route("/api/num_pages_doctor_approved_confirmations",methods=['POST'])(num_approved_confirmations)
    app.route("/api/info_clients_for_doctor",methods=['POST'])(info_clients_for_doctor)
    app.route("/api/update_status_order", methods=['POST'])(update_status_order)


def routes_cotxes(app):
    app.route("/api/cars_full_info", methods=['POST'])(cars_full_info)
    app.route("/api/cars_pos_info", methods=['POST'])(car_pos_info)
    app.route("/api/list_available_cars", methods=['POST'])(list_available_cars)
    app.route("/api/send_order_cars", methods=['POST'])(send_order_cars)
    app.route("/api/list_orders_to_send_cars", methods=['POST'])(list_orders_to_send_cars)
    app.route("/api/prova_list_available_cars", methods=['GET','POST'])(prova_list_available_cars)

def routes_drones(app):
    app.route("/api/drones_full_info", methods=['POST'])(drons_full_info)
    app.route("/api/drones_pos_info", methods=['POST'])(drons_pos_info)
    app.route("/api/send_order_drones", methods=['POST'])(send_order_drones)
    app.route("/api/list_orders_to_send_drones", methods=['POST'])(list_orders_to_send_drones)
    app.route("/api/list_available_drones", methods=['POST'])(list_available_drones)

def routes_colmenes(app):
    app.route("/api/beehives_local", methods=['POST'])(beehives_local)
    app.route("/api/beehives_global", methods=['POST'])(beehives_global)
    app.route("/api/unload_car", methods=['POST'])(unload_car)

def routes_routes(app):
    app.route("/api/store_route", methods=['POST'])(store_route)
    app.route("/api/get_route", methods=['POST'])(get_route)
    app.route("/api/general_storage_pos", methods=['POST'])(general_storage_pos)
    app.route("/api/update_order_cars", methods=['POST'])(update_order_cars)
    app.route("/api/update_order_drones", methods=['POST'])(update_order_drones)


    
def routes_mqtt(app):
    app.route("/api/mqtt", methods=['POST'])(mqtt)
    app.route("/api/update_location", methods=['POST'])(update_location)#nidea del hastag la verdad
    app.route("/api/update_status", methods=['POST'])(update_status)#nidea del hastag la verdad
    app.route("/api/TOCLOUD_UPDATESTATUS", methods=['POST'])(TOCLOUD_UPDATESTATUS)#nidea del hastag la verdad
    app.route("/api/TOCLOUD_UPDATELOCATION", methods=['POST'])(TOCLOUD_UPDATELOCATION)#nidea del hastag la verdad

def routes_paypal(app):
    app.route("/api/create_payment", methods=['POST'])(create_payment)
    app.route("/api/execute_payment", methods=['GET'])(execute_payment)
 
def routes_proves(app):
    app.route("/api/list_orders_to_send_cars", methods=['POST'])(proves)   
