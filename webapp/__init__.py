from webapp.celery import create_celery
from webapp.utils.filters import timestamp_to_human, list_to_string, currency_to_symbol, timestamp_to_hours_minutes
from dotenv import load_dotenv
from flask import Flask, Blueprint
from flask_qrcode import QRcode
from os import urandom, environ, path

app = Flask(__name__)
app.secret_key = urandom(25)
QRcode(app)

celery = create_celery(app)

root = path.join(path.dirname(__file__), '..')
load_dotenv(path.join(root, '.env'))

if environ.get('ENVIRONMENT') == 'PRODUCTION':
    app.config['SERVER_NAME'] = 'www.domain.com'
else:
    app.config["SERVER_NAME"] = environ.get('SITE_URL')

from webapp.routes import auth, main, dashboard, admin, payment, shop, order, donate, developer
 
app.register_blueprint(auth.auth_bp) 
app.register_blueprint(main.main_bp) 
app.register_blueprint(dashboard.dashboard_bp) 
app.register_blueprint(admin.admin_bp)
app.register_blueprint(payment.payment_bp)
app.register_blueprint(shop.shop_bp)
app.register_blueprint(order.order_bp)
app.register_blueprint(donate.donate_bp)
app.register_blueprint(developer.developer_bp)

app.jinja_env.filters['timestamp_to_human'] = timestamp_to_human
app.jinja_env.filters['list_to_string'] = list_to_string
app.jinja_env.filters['currency_to_symbol'] = currency_to_symbol
app.jinja_env.filters['timestamp_to_hours_minutes'] = timestamp_to_hours_minutes

from webapp.database import setup_db

setup_db(app)

from flask_login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)

from webapp.models import User

@login_manager.user_loader
def load_user(uuid):
    return User.query.get(uuid)