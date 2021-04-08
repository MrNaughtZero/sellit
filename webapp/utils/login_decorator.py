from functools import wraps
from flask import g, request, redirect, url_for
from flask_login import current_user
from webapp.utils.tools import get_user_ip
from webapp.models import Ticket
from os import environ

def loggedout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.home'))
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.endpoint))
        return f(*args, **kwargs)
    return decorated_function

def developer_required(f):
    ### Whilst developing, only developers are allowed access to the auth/dashboard
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if get_user_ip() != environ.get('AUTHORISED_IP'):
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function