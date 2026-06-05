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
socketio = SocketIO(cors_allowed_origins="*")