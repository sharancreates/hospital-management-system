import os

class Config:
    # 1. Get the DB URL from environment, fallback to SQLite for local testing
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///arogya.db'
    
    # 2. Fix for Render/Neon: SQLAlchemy needs 'postgresql://', but some providers give 'postgres://'
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    SQLALCHEMY_TRACK_MODIFICATIONS = False