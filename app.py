from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, request, redirect, flash
from config import Config
from models import Department, User, Doctor, Patient
from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from routes import register_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route('/')
    def index():
        return render_template('base.html')

    register_bp(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)