from flask_login import current_user
from models import AuditLog
from extensions import db
import json

def log_audit(action, target_type, target_id=None, changes=None):
    """
    Utility method to write an AuditLog entry.
    """
    try:
        user_id = current_user.user_id if (current_user and current_user.is_authenticated) else None
    except Exception:
        user_id = None
        
    changes_str = json.dumps(changes) if changes else None
    
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        changes=changes_str
    )
    db.session.add(log_entry)
    db.session.flush()
