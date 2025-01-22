from flask import request
from app import server

from app.controllers.process_v2 import generate_image, controller_tabelas

@server.route("/")
def index():
  return "Hello World!"

@server.route('/v2/visualizacao/image', methods=['GET'])
def visualizacao_v2():
  selecao1 = request.args.get('selecao')
  selecao2 = request.args.get('selecao2')
  tipo_visualizacao = request.args.get('type')

  if selecao2:
    selecao = (int(selecao1), int(selecao2))
  else:
    selecao = selecao1
  
  return generate_image(selecao, tipo_visualizacao)

@server.route('/v2/visualizacao/tabelas', methods=['GET'])
def analise_turmas():
  selecao1 = request.args.get('selecao')
  selecao2 = request.args.get('selecao2')

  print(selecao2)

  if selecao2:
    selecao = (int(selecao1), int(selecao2))
  else:
    selecao = selecao1
  
  return controller_tabelas(selecao)
  