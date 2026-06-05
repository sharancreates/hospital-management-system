from flask import Blueprint, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from services import auth_service
from routes.utils import validate_email, sanitize_string, validate_password_complexity
from extensions import limiter

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return {"message": "Already logged in", "role": current_user.role, "status": "success"}

    data = request.get_json()
    if not data:
        return {"message": "Invalid data", "status": "error"}, 400
        
    try:
        email = validate_email(data.get('email'))
        password = sanitize_string(data.get('password'), min_len=1, max_len=100, field_name="Password")
    except ValueError as val_err:
        return {"message": str(val_err), "status": "error"}, 400

    user = auth_service.authenticate_user(email, password)
    
    if user:
        login_user(user)
        current_app.logger.warning(f"Successful login for user: {email}")
        return {"message": "Logged in successfully", "role": user.role, "status": "success"}
    else:
        current_app.logger.warning(f"Failed login attempt for user: {email}")
        return {"message": "Invalid email or password", "status": "error"}, 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    email = current_user.email
    logout_user()
    current_app.logger.warning(f"Logged out user: {email}")
    return {"message": "Logged out successfully", "status": "success"}

@auth_bp.route('/status', methods=['GET'])
def auth_status():
    if current_user.is_authenticated:
        return {"isAuthenticated": True, "role": current_user.role, "email": current_user.email, "status": "success"}
    return {"isAuthenticated": False, "status": "success"}

@auth_bp.route("/reset_password", methods=['POST'])
@limiter.limit("3 per hour")
def reset_request():
    if current_user.is_authenticated:
        return {"message": "Already logged in", "status": "info"}
    
    data = request.get_json()
    if not data:
        return {"message": "Email is required", "status": "error"}, 400
        
    try:
        email = validate_email(data.get('email'))
    except ValueError as val_err:
        return {"message": str(val_err), "status": "error"}, 400
        
    auth_service.generate_reset_link(email)
    
    # Do not reveal if email exists
    return {
        "message": "If an account with that email exists, a password reset link has been generated.",
        "status": "success"
    }

@auth_bp.route("/reset_password/<token>", methods=['POST'])
@limiter.limit("3 per hour")
def reset_token(token):
    if current_user.is_authenticated:
        return {"message": "Already logged in", "status": "info"}
        
    data = request.get_json()
    if not data or not data.get('password'):
        return {"message": "Password is required", "status": "error"}, 400
        
    try:
        is_ok, err_msg = validate_password_complexity(data.get('password'))
        if not is_ok:
            raise ValueError(err_msg)
        password = sanitize_string(data.get('password'), min_len=8, max_len=100, field_name="Password")
    except ValueError as val_err:
        return {"message": str(val_err), "status": "error"}, 400

    success = auth_service.reset_user_password(token, password)
    
    if success:
        return {"message": "Your password has been updated! You can now log in.", "status": "success"}
    else:
        return {"message": "That is an invalid or expired token", "status": "error"}, 400