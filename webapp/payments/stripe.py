import stripe
from os import environ

stripe.api_key = environ.get('STRIPE_SECRET')

def stripe_setup(email) -> dict:
    account = stripe.Account.create(
        type = 'express',
        email = email,
        business_type = 'individual',
        business_profile = {
            'product_description' : f'{environ.get("BRAND_NAME")} is an all-in-one payment processing and e-commerce solution. Accept payments, sell digital products from your own and more, do it all with a single platform.',
            'mcc' : '5817' ## Stripe Merchant Code - Digital Goods – Applications (Excludes Games)
        }
    )
    
    account_link = stripe.AccountLink.create(
        account = account['id'],
        refresh_url = 'http://dashboard.' + environ.get('SITE_URL') + '/stripe/connect',
        return_url = 'http://dashboard.' + environ.get('SITE_URL') + '/stripe/connect/validate',
        type = 'account_onboarding'
    )

    return {
        'account_id' : account['id'],
        'account_link_uri' : account['url']
    }

def account_query(acc_id) -> object:
    return stripe.Account.retrieve(acc_id)

def disconnect_account(acc_id) -> object:
    stripe.Account.delete(acc_id)

def create_donation_checkout(id, acc_id, price, currency) -> dict:
    create = stripe.PaymentIntent.create(
        payment_method_types = ['card'],
        amount = int(str(price).replace('.', '')),
        currency = currency,
        transfer_data ={ 
            'destination' : acc_id,
        }
    )
    
    return {
        'payment_method' : 'stripe',
        'client_secret' : create['client_secret'],
        'donation_id' : id,
        'price' : price
    }

def check_stripe_intent(intent) -> object:
    return stripe.PaymentIntent.retrieve(intent)
