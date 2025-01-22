from flask import request
from app import server

from app.controllers.visualizacao import generate_image

from app.controllers.process_v2 import generate_image as generate_image_v2, controller_analise_turmas

@server.route("/")
def index():
  return "Hello World!"

@server.route('/v1/visualizacao/csv', methods=['GET'])
def visualizacao_csv():
  year = int(request.args.get('year'))
  return generate_image(year)


@server.route('/v2/visualizacao/image', methods=['GET'])
def visualizacao_v2():
  selecao = request.args.get('selecao')
  
  return generate_image_v2(selecao)

@server.route('/v2/visualizacao/analise_turmas', methods=['GET'])
def analise_turmas():
  selecao = request.args.get('selecao')
  
  return controller_analise_turmas(selecao)
  