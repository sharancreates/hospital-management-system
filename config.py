import os

class Config:
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///arogya.db'
    
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    SQLALCHEMY_TRACK_MODIFICATIONS = False