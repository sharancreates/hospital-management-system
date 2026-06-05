import os
import shutil
from datetime import datetime
import glob
import logging

# Set up logging for backups
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MAX_BACKUPS = 7

def backup_sqlite():
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///arogya.db')
    
    # We only automate backups for SQLite. Postgres backup is done via pg_dump.
    if not db_url.startswith('sqlite:///'):
        logger.info("Non-SQLite database configured. Skipping file-based backup.")
        return False
        
    db_relative_path = db_url.replace('sqlite:///', '')
    
    # Resolve absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Relative SQLite paths in Flask-SQLAlchemy are relative to the 'instance' folder
    if not os.path.isabs(db_relative_path):
        src_db_path = os.path.abspath(os.path.join(base_dir, 'instance', db_relative_path))
    else:
        src_db_path = os.path.abspath(db_relative_path)
    
    if not os.path.exists(src_db_path):
        logger.error(f"Source SQLite database not found at {src_db_path}")
        return False
        
    # Ensure backups directory exists
    backup_dir = os.path.join(os.path.dirname(src_db_path), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate timestamped backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest_filename = f"arogya_backup_{timestamp}.db"
    dest_path = os.path.join(backup_dir, dest_filename)
    
    try:
        # Safely copy SQLite file
        shutil.copy2(src_db_path, dest_path)
        logger.info(f"Database successfully backed up to {dest_path}")
        
        # Rotate backups (keep only the latest MAX_BACKUPS)
        backups = sorted(glob.glob(os.path.join(backup_dir, 'arogya_backup_*.db')))
        if len(backups) > MAX_BACKUPS:
            excess = backups[:-MAX_BACKUPS]
            for file_to_delete in excess:
                os.remove(file_to_delete)
                logger.info(f"Removed old backup file: {file_to_delete}")
                
        return True
    except Exception as e:
        logger.error(f"Failed to copy database: {str(e)}")
        return False

if __name__ == '__main__':
    logger.info("Starting automated SQLite backup process...")
    backup_sqlite()
