from flask import request
from app import server

from app.controllers.visualizacao import generate_image

@server.route("/")
def index():
  return "Hello World!"

@server.route('/visualizacao/csv', methods=['GET'])
def visualizacao_csv():
  year = request.args.get('year')
  return generate_image(year)
  