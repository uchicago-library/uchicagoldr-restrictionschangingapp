from flask import flask
from ..endpoints.routes import BP

APP = Flask(__name__)
APP.register_blueprint(BP)
