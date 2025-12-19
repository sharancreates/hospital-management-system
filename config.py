from dotenv import load_dotenv

load_dotenv()

import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///hms.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False