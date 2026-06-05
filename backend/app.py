from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, request, redirect, flash, send_from_directory
from config import Config
from dotenv import load_dotenv
import os

load_dotenv()
from models import Department, User, Doctor, Patient
from extensions import db, cors, mail, limiter, migrate, socketio
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from routes import register_bp
from flask_wtf.csrf import CSRFProtect, generate_csrf
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy import event
import logging
from logging.handlers import RotatingFileHandler

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout = 30000")
    except Exception:
        pass
    finally:
        cursor.close()

@event.listens_for(Engine, "begin")
def do_begin(conn):
    if conn.dialect.name == "sqlite":
        try:
            dbapi_conn = conn.connection.dbapi_connection
            if dbapi_conn is not None and not dbapi_conn.in_transaction:
                conn.exec_driver_sql("BEGIN IMMEDIATE")
        except Exception:
            pass

def create_app(config_class=Config):
    # Serve static files from the compiled React build folder
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
    app.config.from_object(config_class)  
    
    # Configure application file and console logging
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(os.path.join(log_dir, 'app.log'), maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app)
    
    # Configure strict CORS for production
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    cors.init_app(app, resources={r"/*": {"origins": frontend_url}}, supports_credentials=True)
    
    csrf = CSRFProtect()
    csrf.init_app(app)

    @app.before_request
    def enforce_https():
        if os.environ.get('FLASK_ENV') == 'production':
            if not request.is_secure and request.headers.get('X-Forwarded-Proto', 'http') != 'https':
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)

    @app.after_request
    def set_csrf_cookie(response):
        # Double-submit cookie pattern CSRF
        # Use dynamic secure flag from config
        secure_flag = app.config.get('SESSION_COOKIE_SECURE', False)
        response.set_cookie('XSRF-TOKEN', generate_csrf(), secure=secure_flag, samesite='Lax')
        
        # Inject standard security headers
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "frame-ancestors 'none';"
        )
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response

    from flask_wtf.csrf import CSRFError
    from flask import jsonify

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        app.logger.warning(f"CSRF validation failed: {e.description}")
        return jsonify({"message": f"CSRF error: {e.description}", "status": "error"}), 400

    login_manager = LoginManager()
    login_manager.init_app(app)
    @login_manager.unauthorized_handler
    def unauthorized():
        return {"message": "Unauthorized", "status": "error"}, 401

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    register_bp(app)

    # Initialize upcoming appointment reminders background scheduler
    if not app.config.get('TESTING') and os.environ.get('FLASK_ENV') != 'testing' and os.environ.get('NO_DAEMON') != '1':
        from services.reminders import start_reminder_daemon
        start_reminder_daemon(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)