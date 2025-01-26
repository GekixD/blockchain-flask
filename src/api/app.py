from flask import Flask
from src.api.routes import routes


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.register_blueprint(routes)

# Running the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
