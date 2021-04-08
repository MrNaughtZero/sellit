from datetime import datetime
from random import choice
import hashlib
from hashlib import sha256
import pytz
import string
import time
from ipapi import location

def hash_string(string):
    return sha256(string.encode('utf-8')).hexdigest()

def generate_string(length):
    generate = string.digits + string.ascii_lowercase + string.ascii_uppercase
    return ''.join(choice(generate) for i in range(length))

def timestamp(seconds):
    return str(time.time() + seconds).split('.')[0]

def logging(log):
    pass

def date_rearrange(date):
    ''' convert date from YYYY:MM:DD to DD:MM:YYYY '''
    if not date:
        return None
    date_strip = date.split('-')
    return f'{date_strip[2]}-{date_strip[1]}-{date_strip[0]}'

def check_coupon_dates(date, timezone, value):
    ''' get the current date based off the users timezone, and check if the coupon is available/expired '''
    current_date = datetime.now(pytz.timezone(timezone)).strftime('%d-%m-%Y')
    current_date_obj = datetime.strptime(current_date, '%d-%m-%Y')

    date_time_obj = datetime.strptime(date, '%d-%m-%Y')

    if value == 'start':
        if current_date_obj >= date_time_obj:
            return True
        else:
            return False
    if value == 'end':
        if current_date_obj > date_time_obj:
            return False

    return True

def convert_currency_symbol(currency_code):
    return currency_code.replace('GBP', '£').replace('USD', '$').replace('EUR', '€')

def get_user_ip():
    return location(output='ip')