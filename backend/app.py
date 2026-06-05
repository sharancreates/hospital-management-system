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
    # Only run SQLite PRAGMA commands on SQLite connections
    if 'sqlite' in type(dbapi_connection).__module__.lower():
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
    raw_frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    frontend_origins = []
    for origin in raw_frontend_url.split(','):
        cleaned = origin.strip().rstrip('/')
        if cleaned:
            frontend_origins.append(cleaned)
            # If it has https, also allow http just in case, and vice versa
            if cleaned.startswith("https://"):
                frontend_origins.append(cleaned.replace("https://", "http://"))
            elif cleaned.startswith("http://"):
                frontend_origins.append(cleaned.replace("http://", "https://"))

    # Always ensure localhost development origins are allowed
    development_origins = [
        "http://localhost:5173", "https://localhost:5173",
        "http://127.0.0.1:5173", "https://127.0.0.1:5173",
        "http://localhost:3000", "https://localhost:3000"
    ]
    for dev_origin in development_origins:
        if dev_origin not in frontend_origins:
            frontend_origins.append(dev_origin)

    cors.init_app(app, resources={r"/*": {
        "origins": frontend_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "X-CSRF-Token", "X-XSRF-TOKEN", "Authorization"],
        "expose_headers": ["Content-Type", "X-CSRF-Token", "X-XSRF-TOKEN"],
        "supports_credentials": True
    }})
    
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
        samesite_flag = app.config.get('SESSION_COOKIE_SAMESITE', 'Lax')
        response.set_cookie('XSRF-TOKEN', generate_csrf(), secure=secure_flag, samesite=samesite_flag)
        
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

    @login_manager.request_loader
    def load_user_from_request(request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '', 1)
            from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired
            s = Serializer(app.config['SECRET_KEY'])
            try:
                data = s.loads(token, salt='auth-token-salt', max_age=86400)  # 1 day expiration
                user_id = data.get('user_id')
                if user_id:
                    return User.query.get(int(user_id))
            except (BadSignature, SignatureExpired):
                pass
        return None

    @app.before_request
    def exempt_api_headers_from_csrf():
        if request.path.startswith('/api/'):
            request.csrf_exempt = True
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    register_bp(app)

    # Auto-initialize and auto-seed database if empty on startup
    if not app.config.get('TESTING') and os.environ.get('FLASK_ENV') != 'testing':
        from seed import auto_seed_database_if_empty
        try:
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            masked_uri = db_uri
            if '@' in db_uri:
                parts = db_uri.split('@')
                prefix = parts[0].split(':')
                if len(prefix) > 2:
                    masked_uri = f"{prefix[0]}:{prefix[1]}:***@{parts[1]}"
            app.logger.warning(f"Starting database initialization check with URI: {masked_uri}")
            auto_seed_database_if_empty(app)
        except Exception as e:
            app.logger.error(f"Error during auto-initialization/seeding: {str(e)}")

    # Initialize upcoming appointment reminders background scheduler
    if not app.config.get('TESTING') and os.environ.get('FLASK_ENV') != 'testing' and os.environ.get('NO_DAEMON') != '1':
        from services.reminders import start_reminder_daemon
        start_reminder_daemon(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)