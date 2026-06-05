from models import User
from extensions import db, mail
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app
from flask_mail import Message
import os

def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None

def generate_reset_link(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return None
    
    token = user.get_reset_token()
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    reset_url = f"{frontend_url}/reset_password/{token}"
    
    msg = Message('Password Reset Request',
                  sender=os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@arogya.in'),
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request then simply ignore this email and no changes will be made.
'''

    if current_app.config.get('TESTING'):
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.warning(f"Error sending email in test: {str(e)}")
        return user

    from threading import Thread
    app = current_app._get_current_object()
    recipient_email = user.email

    def async_send():
        with app.app_context():
            try:
                mail.send(msg)
            except Exception as e:
                app.logger.warning(f"Error sending email: {str(e)}")
                # Fallback: Write email to local file for development/testing
                try:
                    log_dir = os.path.join(app.root_path, 'instance')
                    os.makedirs(log_dir, exist_ok=True)
                    log_path = os.path.join(log_dir, 'sent_emails.txt')
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(f"--- EMAIL SENT AT {datetime.now()} ---\n")
                        f.write(f"To: {recipient_email}\n")
                        f.write(f"Subject: Password Reset Request\n")
                        f.write(f"Body:\n{msg.body}\n")
                        f.write("-" * 40 + "\n\n")
                    app.logger.info(f"[SMTP Fallback] Email content written to {log_path}")
                except Exception as log_err:
                    app.logger.error(f"Failed to write fallback log: {str(log_err)}")

    Thread(target=async_send).start()
    return user

from services.audit_service import log_audit

def reset_user_password(token, new_password):
    user = User.verify_reset_token(token)
    if not user:
        return False
    
    user.password_hash = generate_password_hash(new_password)
    log_audit("RESET_PASSWORD", "User", user.user_id)
    db.session.commit()
    return True
