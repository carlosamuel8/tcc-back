from flask import jsonify
import pandas as pd
from datetime import datetime

def criar_timestamp(row):
  if row['periodo'] == 1:
    return f"01/02/{row['ano']}"
  elif row['periodo'] == 2:
    return f"01/08/{row['ano']}"
  
def ajustar_timestamp(ts):
  # Converte a string para um objeto datetime
  data = datetime.strptime(ts, "%d/%m/%Y")
  # Se for fevereiro, mudar para junho
  if data.month == 2:
    data = data.replace(month=6)
  # Se for agosto, mudar para dezembro
  elif data.month == 8:
    data = data.replace(month=12)
  return data.strftime("%d/%m/%Y")

# Função para adicionar 1 dia a uma data
def adicionar_um_dia(data_str):
    dia, mes, ano = map(int, data_str.split('/'))
    if dia < 28:
      dia += 1
    else:
      # Verificar o número de dias no mês
      if mes == 2:  # Fevereiro
        dia = 1 if dia == 28 else dia + 1
        if dia == 1:
          mes += 1
      elif mes in [4, 6, 9, 11]:  # Abril, Junho, Setembro, Novembro
        dia = 1 if dia == 30 else dia + 1
        if dia == 1:
          mes += 1
      else:  # Janeiro, Março, Maio, Julho, Agosto, Outubro, Dezembro
        dia = 1 if dia == 31 else dia + 1
        if dia == 1:
          mes = 1 if mes == 12 else mes + 1
          ano += 1 if mes == 1 else 0
    return f"{dia:02d}/{mes:02d}/{ano}"

def process():
  data = pd.read_csv('data/dados_CC_ORIGINAL.csv')
  df = pd.DataFrame(data)
  df = df.drop_duplicates()
  df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
  df_filtrado = df[df['ano'] < 2024]
  
  codigos_filtrar = [
    "QXD0001", "QXD0005", "QXD0056", "QXD0103", "QXD0108", "QXD0109",
    "QXD0006", "QXD0007", "QXD0008", "QXD0010", "QXD0013",
    "QXD0012", "QXD0017", "QXD0040", "QXD0114", "QXD0115",
    "QXD0011", "QXD0014", "QXD0016", "QXD0041", "QXD0116",
    "QXD0020", "QXD0021", "QXD0025", "QXD0119", "QXD0120",
    "QXD0019", "QXD0037", "QXD0038", "QXD0221", "QXD0043", "QXD0046",
    "QXD0029", "QXD0110",
  ]

  # Filtrar o dataframe
  df_filtrado = df_filtrado[df_filtrado['codigo'].isin(codigos_filtrar)]
  df_filtrado['codigo'] = df_filtrado['codigo'].replace('QXD0221', 'QXD0038')
  
  df_filtrado['resultado'] = df_filtrado['resultado'].str.replace('REP. FALTA', 'REPFALTA', regex=False)
  
  df_filtrado['timestamp'] = df_filtrado.apply(criar_timestamp, axis=1)
  
  df_filtrado = df_filtrado[['id_discente', 'codigo', 'resultado', 'timestamp']]
  
  nova_linha = df_filtrado.copy()
  
  # Ajustando o código e o timestamp da nova linha
  nova_linha['codigo'] = nova_linha['codigo'] + '_' + nova_linha['resultado'].str.replace(' ', '', regex=False)
  nova_linha['resultado'] = '-'  # Definindo o resultado como "-"
  nova_linha['timestamp'] = nova_linha['timestamp'].apply(ajustar_timestamp)

  # Concatenando as novas linhas ao DataFrame original
  df_final = pd.concat([df_filtrado, nova_linha], ignore_index=True)
  
  df_final = df_final.drop(columns=['resultado'])
  
  # Filtrar os alunos com pelo menos 33 aprovações apenas uma vez
  alunos_com_mais_33 = df_final[df_final['codigo'].str.contains("_APROVADO", na=False)].groupby('id_discente')['codigo'].nunique()
  alunos_com_mais_33 = alunos_com_mais_33[alunos_com_mais_33 >= 33].index

  # Adicionar 'verificador' para cada aluno
  verificador_linhas = []
  for id_discente in alunos_com_mais_33:
    # Encontrar a última data de aprovação para o aluno
    ultima_data = df_final[(df_final['id_discente'] == id_discente) & (df_final['codigo'].str.endswith('_APROVADO'))]['timestamp'].max()

    # Adicionar 1 dia à data
    nova_data = adicionar_um_dia(ultima_data)

    # Criar uma nova linha
    verificador_linhas.append({
      'id_discente': id_discente,
      'codigo': 'verificador',
      'timestamp': nova_data
    })

  # Adicionar todas as novas linhas de uma vez para evitar duplicidades
  df_verificadores = pd.DataFrame(verificador_linhas)
  df_final = pd.concat([df_final, df_verificadores], ignore_index=True)
  
  # ----------------
  # Garantir que o timestamp é datetime
  df_final['timestamp'] = pd.to_datetime(df_final['timestamp'], format="%d/%m/%Y", errors='coerce')

  # Garantir que apenas uma atividade "Iniciou" é adicionada por aluno
  novas_linhas = []

  for id_discente, group in df_final.groupby('id_discente'):
    # Ordenar as atividades do aluno pelo timestamp
    group = group.sort_values(by='timestamp', ascending=True)

    # Data da primeira atividade do aluno
    primeira_data = group.iloc[0]['timestamp']

    # Ajustar a data para 'um mês antes', sem ultrapassar o início do mesmo ano
    iniciou_data = (
      primeira_data - pd.DateOffset(months=1)
      if primeira_data.month > 1 else
      primeira_data.replace(month=1, day=1)
    )

    # Adicionar nova linha para a atividade "Iniciou"
    novas_linhas.append({'id_discente': id_discente, 'codigo': 'Iniciou', 'timestamp': iniciou_data})

  # Adicionar as novas linhas ao DataFrame
  df_novas_linhas = pd.DataFrame(novas_linhas)
  df_final = pd.concat([df_final, df_novas_linhas], ignore_index=True)

  # Ordenar novamente
  df_final = df_final.sort_values(by=['id_discente', 'timestamp']).reset_index(drop=True)
  
  df_final['timestamp'] = pd.to_datetime(df_final['timestamp'], format='%d/%m/%Y')

  return df_final
