import datetime

def timestamp_to_human(date):
    ''' convert unix timestamp to Month Day, Year '''
    return datetime.datetime.fromtimestamp(int(date)).strftime('%b %d, %Y')

def timestamp_to_hours_minutes(date):
    timestamp_converted = datetime.datetime.fromtimestamp(date)

    date = timestamp_converted.strftime('%H:%M')

    if timestamp_converted.date() < datetime.datetime.today().date():
        if timestamp_converted.date().year < datetime.datetime.today().year:
            date = timestamp_converted.strftime('%d/%B/%y')
        else:
            date = timestamp_converted.strftime('%b %d')

    return date

def list_to_string(content):
    ''' convert list to string for edit product -> this enables you to set the value of the textarea as a string instead of looping in Jinja'''
    return '\n'.join(content)

def currency_to_symbol(currency):
    currency = currency.replace('GBP', '£').replace('USD', '$').replace('EUR', '€')
    return currency