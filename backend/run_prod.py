from waitress import serve
from app import app
import os
import logging

if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)

    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Waitress production server on http://0.0.0.0:{port}...")
    serve(app, host='0.0.0.0', port=port)
