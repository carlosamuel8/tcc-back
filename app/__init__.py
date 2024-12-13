from flask import Flask
from flask_cors import CORS

def get_app():
  app = Flask(__name__)
  app.config.from_object(__name__)
  CORS(app, resources={r'/*': {'origins': '*'}})

  return app

server = get_app()

from app import routes
