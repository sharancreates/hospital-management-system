import os

class Config:
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///arogya.db'
    
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280
    }
    
    # Production Cookie Security
    _is_prod = (
        os.environ.get('FLASK_ENV') == 'production' or 
        'onrender.com' in database_url or
        'neon.tech' in database_url or
        'supabase' in database_url
    )
    if _is_prod and SECRET_KEY == 'dev-key-please-change':
        raise ValueError("CRITICAL: Production deployments require a secure, environment-defined SECRET_KEY.")
        
    SESSION_COOKIE_SECURE = _is_prod
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE') or ('None' if _is_prod else 'Lax')
    
    # Request constraints
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    
    # CSRF Headers for frontend API Double-Submit cookie pattern
    WTF_CSRF_ENABLED = True
    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_HEADERS = ['X-XSRF-TOKEN', 'X-CSRF-Token']

    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME