from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, request, redirect, flash
from config import Config
from models import Department, User, Doctor, Patient
from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from routes import register_bp
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  
    db.init_app(app)
    csrf = CSRFProtect()
    csrf.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route('/')
    def index():    
        return render_template('index.html')

    register_bp(app)

    @app.route('/init-db')
    def init_db():
        try:
            db.create_all()
            existing_admin = User.query.filter_by(role='admin').first()
            
            if not existing_admin:
                admin_user = User(email='admin@arogya.com', role='admin')
                admin_user.set_password('admin$Arogya077')
                db.session.add(admin_user)
                db.session.commit()
                return "<h1>Success! Tables created & Admin user 'admin@arogya.com' added.</h1>"
            else:
                return "<h1>Tables exist. Admin user already exists.</h1>"
                
        except Exception as e:
            return f"<h1>Error: {str(e)}</h1>"

    @app.route('/fix-db')
    def fix_db():
        try:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(500);'))
                conn.commit()
            return "<h1>Success! Password column resized to 256 characters.</h1>"
        except Exception as e:
            return f"<h1>Error: {str(e)}</h1>"

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)