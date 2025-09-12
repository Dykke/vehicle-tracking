import os
import logging

from app import app, socketio

# Configure logging for production
logging.basicConfig(level=logging.INFO)

# This file is for gunicorn production deployment
# SocketIO will be handled by gunicorn with proper worker class

if __name__ == '__main__':
    # Only used for local development
    logging.basicConfig(level=logging.DEBUG)
    port = int(os.environ.get("PORT", 5000))
    
    print(f"Starting server on port {port}")
    print(f"SocketIO async mode: {socketio.async_mode}")
    
    # Run with threading support for local development
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,  # Disable debug for production
        use_reloader=False,
        log_output=True,
        allow_unsafe_werkzeug=True
    ) 