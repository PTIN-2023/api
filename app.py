from flask import Flask
from routes.route import routes_user, routes_prescriptions, routes_pacients, routes_meds, routes_mqtt, routes_cotxes, routes_drones, routes_routes, routes_colmenes, routes_orders, routes_paypal, routes_managers
import paypalrestsdk
import os

app = Flask(__name__, template_folder='/opt/templates/')
routes_cotxes(app)
routes_drones(app)
routes_meds(app)
routes_mqtt(app)
routes_orders(app)
routes_pacients(app)
routes_routes(app)
routes_user(app)
routes_paypal(app)
routes_managers(app)
routes_colmenes(app)
routes_prescriptions(app)

paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
    "client_secret":os.environ.get('PAYPAL_SECRET')
})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
