from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import (OrdersCaptureRequest,
                                      OrdersCreateRequest, OrdersGetRequest)
from os import environ

environment = SandboxEnvironment(client_id=environ.get('PP_CLIENT'), client_secret=environ.get('PP_SECRET'))
client = PayPalHttpClient(environment)

def create_paypal_order(currency, price, quantity, order_id, receiver, product_name, product_id) -> dict:
    request = OrdersCreateRequest()
    request.prefer('return=representation')

    request.request_body (
    {
        "intent": "CAPTURE",
        "application_context": {
            "return_url": f"http://{environ.get('SITE_URL')}/order/payment/complete/{order_id}",
            "cancel_url": f"http://{environ.get('SITE_URL')}/order/{order_id}",
            "brand_name": environ.get('BRAND_NAME'),
            "landing_page" : "BILLING",
            "shipping_preference" : "NO_SHIPPING"
        },
        "purchase_units": [
                    {
                        "amount": {
                            "currency_code": currency,
                            "value": str(int(quantity) * int(price)),
                            "breakdown": {
                                "item_total" : {
                                     "currency_code" : currency,
                                        "value" : str(int(quantity) * int(price))
                                }
                            }
                        },
                        "items": [
                            {
                                "name": product_name,
                                "sku": ' ' + product_id,
                                "unit_amount": {
                                    "currency_code": currency,
                                    "value": price
                                },
                                "quantity": quantity,
                                "category": "DIGITAL_GOODS"
                            }
                        ],
                        "payee": {
                            "email_address": receiver
                        }
                    }
                ]
    }
    )

    try:
        response = client.execute(request)
        return {
            'address' : response.result.links[1].href,
            'transaction_id' : response.result.id
        }
    except Exception as e:
        with open('logging/log.txt', 'a') as l:
            l.write(str(e) + '\n')
            l.close()

def create_paypal_donation(currency, amount, donation_id, receiver, referrer) -> dict:
    request = OrdersCreateRequest()
    request.prefer('return=representation')

    request.request_body (
    {
        "intent": "CAPTURE",
        "application_context": {
            "return_url": f"http://{environ.get('SITE_URL')}/donation/check/{donation_id}",
            "cancel_url": f"http://{environ.get('SITE_URL')}/donation/cancel/{donation_id}",
            "brand_name": environ.get('BRAND_NAME'),
            "landing_page" : "BILLING",
            "shipping_preference" : "NO_SHIPPING"
        },
        "purchase_units": [
                    {
                        "amount": {
                            "currency_code": currency,
                            "value": amount,
                            "breakdown": {
                                "item_total" : {
                                     "currency_code" : currency,
                                        "value" : amount
                                }
                            }
                        },
                        "payee": {
                            "email_address": receiver
                        }
                    }
                ]
    }
    )

    try:
        response = client.execute(request)
        
        return {
            'payment_address' : response.result.links[1].href,
            'transaction_id' : response.result.id
        }
    except Exception as e:
        with open('logging/log.txt', 'a') as l:
            l.write(str(e) + '\n')
            l.close()

def capture_paypal_order(token) -> str:
    request = OrdersCaptureRequest(token)
    
    try:
        response = client.execute(request)
        order = response.result.id
        return order
    except Exception as e:
        with open('logging/log.txt', 'a') as l:
            l.write(str(e) + '\n')
            l.close()
            return False

def get_paypal_order(token) -> dict:
    request = OrdersGetRequest(token)
    response = client.execute(request)
    
    return {
        'buyer_email' : response.result.payer['email_address'],
        'payment_status' : response.result.status
    }

def check_paypal_success(token) -> bool:
    if capture_paypal_order(token):
        if get_paypal_order(token)['payment_status'] == 'COMPLETED':
            return True
    else:
        return False
