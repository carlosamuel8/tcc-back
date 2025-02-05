from datetime import datetime
import pandas as pd

def processar_csv(df):
    """
    Processa um DataFrame contendo dados acadêmicos, aplicando as transformações necessárias:
    - Remove duplicatas e filtra dados irrelevantes.
    - Ajusta códigos de disciplinas e resultados.
    - Cria colunas de timestamp e activity.
    - Adiciona eventos "Iniciou" e "Verificador".

    Parâmetros:
        df (pd.DataFrame): DataFrame original com os dados acadêmicos.
    
    Retorna:
        pd.DataFrame: DataFrame transformado.
    """
    # Remover duplicatas
    df = df.drop_duplicates()

    # Converter a coluna 'ano' para numérico e filtrar anos abaixo de 2024
    df.loc[:, 'ano'] = pd.to_numeric(df['ano'], errors='coerce')
    df = df[df['ano'] < 2024]

    # Lista de códigos obrigatórios
    codigos_obrigatorios = [
        "QXD0001", "QXD0005", "QXD0056", "QXD0103", "QXD0108", "QXD0109",
        "QXD0006", "QXD0007", "QXD0008", "QXD0010", "QXD0013",
        "QXD0012", "QXD0017", "QXD0040", "QXD0114", "QXD0115",
        "QXD0011", "QXD0014", "QXD0016", "QXD0041", "QXD0116",
        "QXD0020", "QXD0021", "QXD0025", "QXD0119", "QXD0120",
        "QXD0019", "QXD0037", "QXD0038", "QXD0221", "QXD0043", "QXD0046",
        "QXD0029", "QXD0110",
    ]

    # Filtrar apenas disciplinas obrigatórias
    df = df[df['codigo'].isin(codigos_obrigatorios)]

    # Substituir código 'QXD0221' por 'QXD0038'
    df['codigo'] = df['codigo'].replace('QXD0221', 'QXD0038')

    # Ajustar resultados
    df['resultado'] = df['resultado'].str.replace('REP. FALTA', 'REPFALTA', regex=False)

    # Criar timestamps no formato 'dd/mm/yyyy'
    df['timestamp'] = df.apply(lambda row: f"01/{'02' if row['periodo'] == 1 else '08'}/{row['ano']}", axis=1)

    # Selecionar colunas relevantes
    df = df[['id_discente', 'codigo', 'resultado', 'timestamp']]

    # Ajustar timestamps para junho e dezembro
    def ajustar_timestamp(ts):
        data = datetime.strptime(ts, "%d/%m/%Y")
        return data.replace(month=6 if data.month == 2 else 12).strftime("%d/%m/%Y")

    # Criar nova linha com códigos ajustados
    df_extra = df.copy()
    df_extra['codigo'] = df_extra['codigo'] + '_' + df_extra['resultado'].str.replace(' ', '', regex=False)
    df_extra['resultado'] = '-'
    df_extra['timestamp'] = df_extra['timestamp'].apply(ajustar_timestamp)

    # Concatenar novas linhas e remover 'resultado'
    df_final = pd.concat([df, df_extra], ignore_index=True).drop(columns=['resultado'])

    # Função para adicionar um dia a uma data
    df_final['timestamp'] = pd.to_datetime(df_final['timestamp'], errors='coerce')

    # Filtrar alunos com pelo menos 33 aprovações
    alunos_aprovados = df_final[df_final['codigo'].str.contains("_APROVADO", na=False)]
    alunos_com_mais_33 = alunos_aprovados.groupby('id_discente')['codigo'].nunique()
    alunos_com_mais_33 = alunos_com_mais_33[alunos_com_mais_33 >= 33].index

    # Criar eventos 'Verificador'
    df_verificadores = pd.DataFrame([
        {'id_discente': id_discente, 'codigo': 'verificador', 'timestamp': df_final.loc[
            (df_final['id_discente'] == id_discente) & 
            (df_final['codigo'].str.endswith('_APROVADO')), 'timestamp'].max() + pd.Timedelta(days=1)}
        for id_discente in alunos_com_mais_33
    ])

    df_final = pd.concat([df_final, df_verificadores], ignore_index=True).sort_values(by='timestamp').reset_index(drop=True)

    # Criar evento "Iniciou" para cada aluno
    df_iniciou = pd.DataFrame([
        {'id_discente': id_discente, 'codigo': 'Iniciou', 'timestamp': group.iloc[0]['timestamp'] - pd.DateOffset(months=1) if group.iloc[0]['timestamp'].month > 1 else group.iloc[0]['timestamp'].replace(month=1, day=1)}
        for id_discente, group in df_final.groupby('id_discente')
    ])

    df_final = pd.concat([df_final, df_iniciou], ignore_index=True).sort_values(by=['id_discente', 'timestamp']).reset_index(drop=True)

    # Renomear coluna para 'activity'
    df_final = df_final.rename(columns={'codigo': 'activity'})

    return df_final
