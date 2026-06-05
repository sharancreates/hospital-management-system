import os
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_socketio import SocketIO

db = SQLAlchemy()
cors = CORS()
mail = Mail()
limiter = Limiter(key_func=get_remote_address, default_limits=[])
migrate = Migrate()

# Utilize Redis message broker backplane for Socket.IO if REDIS_URL is set
redis_url = os.environ.get('REDIS_URL')
if redis_url:
    socketio = SocketIO(cors_allowed_origins="*", message_queue=redis_url)
else:
    socketio = SocketIO(cors_allowed_origins="*")