import datetime
from flask import jsonify, redirect, request
import paypalrestsdk
from models.models import *
from utils.utils import checktoken
import os

paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
    "client_secret":os.environ.get('PAYPAL_SECRET')
})

# Crear un pago y obtener la URL de aprobación
def create_payment():
    data = request.get_json()
    token = data['session_token']
    amount = data['amount']
    description= data['order_identifier']
    if not description:
        description="TransMed"
    check = checktoken(token)
    if check['valid'] == 'ok':
        if is_local == 1:
            data['session_token'] = 'internal'
            url = cloud_api+"/api/create_payment"
            return requests.post(url, json=data).json()
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "http://147.83.159.195:24105/api/execute_payment",
                "cancel_url": "http://147.83.159.195:24105/api/execute_payment"
            },
            "transactions": [{
                "amount": {
                    "total": amount,
                    "currency": "EUR"
                },
                "description": description
            }]
        })

    if payment.create():
        return jsonify({'result':'ok','url':payment.links[1].href})
    else:
        print(payment.error)
        return jsonify({'result':'error','description' : payment.error})

# Ejecutar el pago y enviar dinero a otra cuenta
def execute_payment():
    if is_local == 1:
        data['session_token'] = 'internal'
        url = cloud_api+"/api/execute_payment"
        return requests.post(url, json=data).json()
    payer_id = request.args.get('PayerID')
    payment_id = request.args.get('paymentId')
    if not payment_id:
        print("error")
        return redirect("http://147.83.159.195:24180/checkout_error", code=302)
    else:
        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({"payer_id": payer_id}):
            # Obtener el ID de transacción del pago
            transaction_id = payment.transactions[0].related_resources[0].sale.id
            
            # Obtener el monto del pago
            amount = payment.transactions[0].amount['total']
            
            # Enviar dinero al destinatario
            payout = paypalrestsdk.Payout({
                "sender_batch_header": {
                    "sender_batch_id": "batch_001",
                    "email_subject": "Pago realizado"
                },
                "items": [
                    {
                        "recipient_type": "EMAIL",
                        "amount": {
                            "value": amount,  
                            "currency": "EUR"
                        },
                        "receiver": 'sb-ckiql26282253@business.example.com',
                        "note": "Pago realizado",
                        "sender_item_id": "item_001"
                    }
                ]
            })

            if payout.create(sync_mode=False):
                #return transaction_id, payout.batch_header.payout_batch_id
                return redirect("http://147.83.159.195:24180/myorders", code=302) #checkout_correct
            else: 
                print(payout.error)
                return redirect("http://147.83.159.195:24180/myorders", code=302) #checkout_error
        else:
            print(payment.error)
            return redirect("http://147.83.159.195:24180/myorders", code=302) #checkout_error



