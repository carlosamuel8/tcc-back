from flask import send_file
import json

from app.utils.new_image_generate import visualizar_disciplinas_por_metrica, analisar_turma, consolidar_metricas
from app.utils.process_mining import executar_replay

def generate_image(selecao, tipo_visualizacao):
  if isinstance(selecao, (tuple, list)) and len(selecao) == 2:
    faixa = list(selecao)  # Converte para lista, se necessário
    ano = None
  elif selecao == "Todos as turmas" or selecao is None:
    faixa = None
    ano = None
  elif selecao.isnumeric():
    faixa = None
    ano = int(selecao)
  else:
    raise ValueError("Seleção inválida. Deve ser um ano (int), faixa de anos (tuple/list) ou None (todos os anos).")
  
  try:
    if faixa:
      image_name = visualizar_disciplinas_por_metrica(faixa, tipo_visualizacao)
    elif ano:
      image_name = visualizar_disciplinas_por_metrica(ano, tipo_visualizacao)
    else:
      image_name = visualizar_disciplinas_por_metrica(None, tipo_visualizacao)

    img_path = f'images/{image_name}'

    # Exibir imagem
    return send_file(img_path, mimetype='image/png')
  except Exception as e:
    return str('e')

def controller_tabelas(selecao):
  if isinstance(selecao, (tuple, list)) and len(selecao) == 2:
    faixa = list(selecao)  # Converte para lista, se necessário
    ano = None
  elif selecao == "Todos as turmas" or selecao is None:
    faixa = None
    ano = None
  elif selecao.isnumeric():
    faixa = None
    ano = int(selecao)
  else:
    raise ValueError("Seleção inválida. Deve ser um ano (int), faixa de anos (tuple/list) ou None (todos os anos).")

  analise_turma_result = analisar_turma(ano)

  df_consolidado = None
  if faixa:
    df_consolidado = consolidar_metricas(faixa)
  elif ano:
    df_consolidado = consolidar_metricas(ano)
  else:
    df_consolidado = consolidar_metricas(None)

  return ({
    'analise_turma': analise_turma_result,
    'df_consolidado': json.loads(df_consolidado),
  })
 

def generate_process_mining_fluxograma(selecao, tipo_visualizacao):
  if isinstance(selecao, (tuple, list)) and len(selecao) == 2:
    faixa = list(selecao) 
    image_name = executar_replay(faixa, tipo_visualizacao)

    img_path = f'images/{image_name}'

    return send_file(img_path, mimetype='image/png')
  
  return "Seleção inválida. Deve ser um intervalo de anos (tuple/list)."



def generate_process_mining_petrinet(selecao, tipo_visualizacao):
  if isinstance(selecao, (tuple, list)) and len(selecao) == 2:
    faixa = list(selecao) 
    image_name = executar_replay(faixa, tipo_visualizacao)

    img_path = f'images/{image_name}'

    return send_file(img_path, mimetype='image/png')
  
  return "Seleção inválida. Deve ser um intervalo de anos (tuple/list)."