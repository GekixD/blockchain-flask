from flask import Flask
from src.api.routes import routes
from src.utils.logger import setup_logger

logger = setup_logger('api.app')

app = Flask(__name__)
logger.info("Initializing Flask application")
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.register_blueprint(routes)
logger.info("Routes registered successfully")

# Running the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
