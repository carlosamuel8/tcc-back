from flask import send_file
import json

from app.utils.new_image_generate import visualizar_taxa_aprovacao_por_turma2, analisar_turma, consolidar_metricas

def generate_image(selecao):
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
      visualizar_taxa_aprovacao_por_turma2(faixa)
      img_path = f'images/turma_{faixa[0]}_{faixa[1]}_taxa_aprovacao.png'
    elif ano:
      visualizar_taxa_aprovacao_por_turma2(ano)
      img_path = f'images/turma_{ano}_taxa_aprovacao.png'
    else:
      visualizar_taxa_aprovacao_por_turma2(None)
      img_path = 'images/turma_todos_os_anos_taxa_aprovacao.png'

    # Exibir imagem
    return send_file(img_path, mimetype='image/png')
  except Exception as e:
    return str(e)

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
