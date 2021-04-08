from flask_sqlalchemy import SQLAlchemy
from os import environ

db = SQLAlchemy()

def setup_db(app):
    if environ.get('ENVIRONMENT') == 'PRODUCTION':
        db_path = 'LIVE_PRODUCTION_DB_PATH'
    else:
        db_path = environ.get('DB_PATH')
    
    app.config["SQLALCHEMY_DATABASE_URI"] = db_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()