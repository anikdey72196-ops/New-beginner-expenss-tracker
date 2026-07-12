from flask import Flask
from datetime import timedelta
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

from extensions import db, jwt
from auth import auth_bp
from expenses import expenses_bp

def create_app():
    app = Flask(__name__)
    
    # Configure MySQL database
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD_RAW = os.environ.get('DB_PASSWORD', '')
    DB_PASSWORD = urllib.parse.quote_plus(DB_PASSWORD_RAW)
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'expense_tracker')
    DB_PORT = os.environ.get('DB_PORT', '3306') # <-- Add this line
    db_uri = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    if DB_HOST != 'localhost' and DB_HOST != '127.0.0.1':
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'ssl': ctx}}
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configure JWT
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', os.urandom(24).hex())
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(expenses_bp)

    # Create the database tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
