from functools import wraps
from flask import jsonify
from flask_login import current_user
import re
from datetime import datetime

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"message": "Unauthorized", "status": "error"}), 401
            if current_user.role not in roles:
                return jsonify({"message": "Forbidden: Access denied", "status": "error"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Input Validation Helpers
EMAIL_REGEX = re.compile(r'^[^@]+@[^@]+\.[^@]+$')
PHONE_REGEX = re.compile(r'^\+?[0-9]{10,15}$')

def validate_email(email):
    if not email or not isinstance(email, str):
        raise ValueError("Invalid email field.")
    email = email.strip()
    if not EMAIL_REGEX.match(email):
        raise ValueError("Invalid email format.")
    return email

def validate_phone(phone):
    if not phone or not isinstance(phone, str):
        raise ValueError("Contact number is required.")
    phone = phone.strip()
    # strip spaces/dashes
    clean_phone = re.sub(r'[\s\-()]+', '', phone)
    if not PHONE_REGEX.match(clean_phone):
        raise ValueError("Contact number must be between 10 and 15 digits.")
    return clean_phone

def validate_age(age):
    try:
        val = int(age)
        if val <= 0 or val > 125:
            raise ValueError()
        return val
    except (TypeError, ValueError):
        raise ValueError("Age must be a positive number between 1 and 125.")

def validate_date(date_str, field_name="Date"):
    if not date_str or not isinstance(date_str, str):
        raise ValueError(f"{field_name} is required.")
    try:
        return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
    except ValueError:
        raise ValueError(f"{field_name} must be in YYYY-MM-DD format.")

def sanitize_string(text, min_len=1, max_len=1000, field_name="Text"):
    if not text or not isinstance(text, str):
        if min_len == 0:
            return ""
        raise ValueError(f"{field_name} is required.")
    text = text.strip()
    # Simple sanitization to escape HTML chars to protect against basic XSS
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    if len(text) < min_len:
        raise ValueError(f"{field_name} is too short (min {min_len} characters).")
    if len(text) > max_len:
        raise ValueError(f"{field_name} exceeds max length of {max_len} characters.")
    return text

def validate_password_complexity(password):
    """
    Validates that a password meets complexity rules:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character from: !@#$%^&*(),.?":{}|<>
    """
    if not password or not isinstance(password, str):
        return False, "Password must be a valid string."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""
