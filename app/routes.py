from flask import request
from app import server

from app.controllers.process_v2 import generate_image, controller_tabelas, generate_process_mining_fluxograma, generate_process_mining_petrinet, generate_process_mining_barras

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

  if selecao2:
    selecao = (int(selecao1), int(selecao2))
  else:
    selecao = selecao1
  
  return controller_tabelas(selecao)
  

# fazer para a aba de mineração de processos que vai retornar uma imagem
# @server.route('/v2/visualizacao/image2', methods=['GET'])
# def mineracao_processos():
#   selecao1 = request.args.get('selecao')
#   selecao2 = request.args.get('selecao2')

#   if selecao2:
#     selecao = (int(selecao1), int(selecao2))
#   else:
#     selecao = selecao1

#   return generate_process_mining(selecao)

@server.route('/v2/visualizacao/fluxograma', methods=['GET'])
def mineracao_processos_fluxograma_rota():
  selecao1 = request.args.get('selecao')
  selecao2 = request.args.get('selecao2')

  if selecao2:
    selecao = (int(selecao1), int(selecao2))
  else:
    selecao = selecao1

  return generate_process_mining_fluxograma(selecao, 'fluxograma')



@server.route('/v2/visualizacao/petrinet', methods=['GET'])
def mineracao_processos_petrinet_rota():
  selecao1 = request.args.get('selecao')
  selecao2 = request.args.get('selecao2')

  if selecao2:
    selecao = (int(selecao1), int(selecao2))
  else:
    selecao = selecao1

  return generate_process_mining_petrinet(selecao, 'petrinet')


@server.route('/v2/visualizacao/barras', methods=['GET'])
def mineracao_processos_barras_rota():
  selecao1 = request.args.get('selecao')
  selecao2 = request.args.get('selecao2')

  if selecao2:
    selecao = (int(selecao1), int(selecao2))
  else:
    selecao = selecao1

  return generate_process_mining_barras(selecao, 'barras')

