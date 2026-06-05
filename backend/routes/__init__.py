from .auth_routes import auth_bp
from .admin_routes import admin_bp
from .doctor_routes import doctor_bp
from .patient_routes import patient_bp
from .health_routes import health_bp
from .enterprise_routes import enterprise_bp

def register_bp(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(enterprise_bp)