from flask import Flask
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

from extensions import db, jwt
from auth import auth_bp
from expenses import expenses_bp

def create_app():
    app = Flask(__name__)
    
    # Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configure JWT
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-jwt-key')
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
