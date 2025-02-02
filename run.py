import argparse
from src.api.app import app
from src.utils.logger import setup_logger
import signal
import sys

logger = setup_logger('application.server')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Flask app PORT argument')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Flask app HOST argument')
    parser.add_argument('--debug', action='store_true', help='Enable Flask debug mode')
    args = parser.parse_args()
    
    logger.info(f"Starting server on {args.host}:{args.port}")
    try:
        app.run(host=args.host, port=args.port, debug=args.debug)
    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}")
        raise

def signal_handler(sig, frame):
    logger.info("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    main()
