from coinpayments import CoinPaymentsAPI
from os import environ

api = CoinPaymentsAPI(public_key=environ.get('CP_PUBLIC'), private_key=environ.get('CP_PRIVATE'))

def create_coin_transaction(price, currency, coin) -> dict:
    create_transaction = api.create_transaction(price=amount, currency1=currency, currency2=coin)   

    return {
        'address' : create_transaction['result']['address'],
        'amount' : create_transaction['result']['amount'],
        'txn' : create_transaction['result']['txn_id'],
    }

def check_coin_transaction(txid) -> object:
    return api.get_tx_info(txid=txid)