import pandas as pd
import pygraphviz as pgv
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

df_final = pd.read_csv('data/logfinal.csv')
df_final['timestamp'] = pd.to_datetime(df_final['timestamp'], format='%Y-%m-%d')

codigo_para_nome = {
    "QXD0001": "Fund. de Programação",

    "QXD0001": "Fund. de Programação",
    "QXD0108": "Introdução à CC", 
    "QXD0005": "Arquitet. de Computadores", 
    "QXD0056": "Matemática Básica",
    "QXD0109": "Pré-Cálculo", 
    "QXD0103": "Ética, Direito e Legislação",

    
    "QXD0007": "Program. Orient. a Objetos",
    "QXD0010": "Estrutura de dados",
    "QXD0008": "Matemática Discreta",
    "QXD0006": "Cálc. Diferencial e Integral I",
    "QXD0013": "Sistemas Operacionais",
    
    
    "QXD0114": "Program. Funcional",
    "QXD0115": "Estrutura de Dados Avanç.",
    "QXD0040": "Ling. Formais e Autômatos",
    "QXD0017": "Lógica para Computação",
    "QXD0012": "Probabilidade de Estatística",

    "QXD0016": "Linguagens de Program.",
    "QXD0041": "Proj. e Análise de Algoritmo",
    "QXD0011": "Fund. de Banco de Dados",
    "QXD0014": "Análise e Proj. de Sistemas",
    "QXD0116": "Álgebra Linear",


    "QXD0020": "Desenv. de Software p/ Web",
    "QXD0119": "Computação Gráfica",
    "QXD0120": "Matemática Computacional",
    "QXD0025": "Compiladores",
    "QXD0021": "Redes de Computadores",

    "QXD0046": "Teoria da Computação",
    "QXD0037": "Inteligência Artificial",
    "QXD0019": "Engenharia de Software",
    "QXD0038": "Interf. Humano-Comp.",
    "QXD0043": "Sistemas Distribuídos",

    "QXD0110": "Proj. Pesq. Científ. e Tec.",
    "QXD0029": "Empreendedorismo",
}

def taxa_aprovacao_periodo(df_final, faixa_anos):
    """
    Calcula a taxa de aprovação de cada disciplina para um intervalo de anos ou um ano específico.

    Parâmetros:
    - df_final: DataFrame com as informações de atividades dos alunos.
    - faixa_anos: Lista contendo dois elementos [ano_inicio, ano_fim].

    Retorno:
    - total_aprovacoes: Série com o total de aprovações por disciplina.
    - total_alunos: Série com o total de alunos por disciplina.
    """
    if not isinstance(faixa_anos, list) or len(faixa_anos) != 2:
        raise ValueError("faixa_anos deve ser uma lista com dois elementos [ano_inicio, ano_fim].")

    # Filtrar o DataFrame para o intervalo de anos fornecido
    df_selecao = df_final[df_final['timestamp'].dt.year.between(faixa_anos[0], faixa_anos[1])].copy()

    # Criar a coluna 'disciplina'
    df_selecao.loc[:, 'disciplina'] = df_selecao['codigo'].str.split('_').str[0]

    # Filtrar apenas atividades relevantes
    atividades_relevantes = df_selecao[~df_selecao['codigo'].isin(['Iniciou', 'verificador'])].copy()

    # Verificar aprovações
    atividades_relevantes.loc[:, 'aprovado'] = atividades_relevantes['codigo'].str.contains('_APROVADO', na=False)

    # Contar total de aprovações e total de alunos por disciplina
    total_aprovacoes = atividades_relevantes[atividades_relevantes['aprovado']].groupby('disciplina').size()
    total_alunos = atividades_relevantes.groupby('disciplina')['id_discente'].nunique()

    return total_aprovacoes, total_alunos

def calcular_taxa_aprovacao_primeira_vez(selecao):
    """
    Função para calcular a taxa de aprovação de cada disciplina com base em um ano específico, 
    uma faixa de anos ou todos os anos.

    Parâmetros:
    - df_final: DataFrame com as informações de atividades dos alunos.
    - selecao: Pode ser um ano específico (int), uma faixa de anos (list) ou None (todos os anos).

    Retorna:
    - total_aprovacoes: Série com o total de aprovações por disciplina.
    - total_alunos: Série com o total de alunos por disciplina.
    """
    if isinstance(selecao, list):  # Faixa de anos
        alunos_selecao = df_final[
            (df_final['codigo'] == 'Iniciou') & 
            (df_final['timestamp'].dt.year.between(selecao[0], selecao[1]))
        ]['id_discente'].unique()
    elif isinstance(selecao, int):  # Ano específico
        alunos_selecao = df_final[
            (df_final['codigo'] == 'Iniciou') & 
            (df_final['timestamp'].dt.year == selecao)
        ]['id_discente'].unique()
    else:  # Todos os anos
        alunos_selecao = df_final[
            df_final['codigo'] == 'Iniciou'
        ]['id_discente'].unique()

    # Filtrar o DataFrame para os alunos e disciplinas relevantes
    df_selecao = df_final[df_final['id_discente'].isin(alunos_selecao)].copy()

    # Criar a coluna 'disciplina'
    df_selecao.loc[:, 'disciplina'] = df_selecao['codigo'].str.split('_').str[0]

    # Filtrar apenas as atividades relevantes (excluir "Iniciou" e "verificador")
    disciplinas = df_selecao[~df_selecao['codigo'].isin(['Iniciou', 'verificador'])]

    # Ordenar o DataFrame por aluno, disciplina e timestamp
    disciplinas = disciplinas.sort_values(by=['id_discente', 'disciplina', 'timestamp'])

    # Identificar a segunda ocorrência para cada aluno e disciplina
    disciplinas['ocorrencia'] = disciplinas.groupby(['id_discente', 'disciplina']).cumcount() + 1
    segunda_ocorrencia = disciplinas[disciplinas['ocorrencia'] == 2].copy()

    # Verificar se essa segunda ocorrência foi uma aprovação
    segunda_ocorrencia.loc[:, 'aprovado'] = segunda_ocorrencia['codigo'].str.contains('_APROVADO', na=False)

    # Calcular total de aprovações e total de alunos por disciplina
    total_aprovacoes = segunda_ocorrencia.groupby('disciplina')['aprovado'].sum()
    total_alunos = segunda_ocorrencia.groupby('disciplina')['id_discente'].nunique()

    return total_aprovacoes, total_alunos

def disciplinas_com_maior_gargalo(selecao=None):
    """
    Identifica as disciplinas com maior número de alunos que não conseguiram aprovação.

    Parâmetros:
    - selecao: Pode ser um ano específico (int), uma faixa de anos (list) ou None (todos os anos).

    Retorno:
    - DataFrame: Gargalos por disciplina, nomes e quantidade em ordem decrescente, excluindo a atividade 'Iniciou'.
    """
    global df_final, codigo_para_nome

    # Filtrar alunos que não concluíram o curso (sem "verificador")
    alunos_nao_concluidos = df_final[~df_final['id_discente'].isin(
        df_final[df_final['codigo'] == 'verificador']['id_discente']
    )]

    # Criar uma nova coluna para extrair o código da disciplina
    alunos_nao_concluidos = alunos_nao_concluidos.copy()
    alunos_nao_concluidos['Código'] = alunos_nao_concluidos['codigo'].str.split('_').str[0]

    # Selecione alunos com base na seleção
    if isinstance(selecao, list):  # Faixa de anos
        alunos_iniciaram_anos = df_final[
            (df_final['codigo'] == 'Iniciou') & 
            (df_final['timestamp'].dt.year.between(selecao[0], selecao[1]))
        ]['id_discente']
    elif isinstance(selecao, int):  # Ano específico
        alunos_iniciaram_anos = df_final[
            (df_final['codigo'] == 'Iniciou') & 
            (df_final['timestamp'].dt.year == selecao)
        ]['id_discente']
    else:  # Todos os anos
        alunos_iniciaram_anos = df_final[df_final['codigo'] == 'Iniciou']['id_discente']

    alunos_nao_concluidos = alunos_nao_concluidos[
        alunos_nao_concluidos['id_discente'].isin(alunos_iniciaram_anos)
    ]

    def identificar_gargalos(df):
        """Identifica gargalos para cada aluno e disciplina."""
        gargalos = []
        for (id_discente, disciplina), grupo in df.groupby(['id_discente', 'Código']):
            # Se não existe "_APROVADO" nas atividades da disciplina
            if not grupo['codigo'].str.contains('_APROVADO').any():
                gargalos.append({'id_discente': id_discente, 'Código': disciplina})
        return pd.DataFrame(gargalos)

    # Identificar os gargalos
    gargalos = identificar_gargalos(alunos_nao_concluidos)

    # Verificar se gargalos está vazio
    if gargalos.empty:
        return pd.DataFrame(columns=['Código', 'Nome', 'Quantidade'])

    # Contar os gargalos por disciplina e transformar em DataFrame
    gargalos_por_disciplina = gargalos['Código'].value_counts().reset_index()
    gargalos_por_disciplina.columns = ['Código', 'Quantidade']

    # Excluir a atividade "Iniciou"
    gargalos_por_disciplina = gargalos_por_disciplina[gargalos_por_disciplina['Código'] != 'Iniciou']

    # Adicionar a coluna 'Nome' com base no mapeamento global e capitalizar a primeira letra
    gargalos_por_disciplina['Nome'] = gargalos_por_disciplina['Código'].map(codigo_para_nome).str.title()

    # Reorganizar as colunas para que 'Nome' fique como a segunda
    gargalos_por_disciplina = gargalos_por_disciplina[['Código', 'Nome', 'Quantidade']]

    return gargalos_por_disciplina


def analisar_turma(ano_inicio=None):

    # Filtrar alunos que iniciaram no ano especificado ou em todos os anos
    if ano_inicio is not None:
        alunos_iniciaram = df_final[(df_final['codigo'] == 'Iniciou') & (df_final['timestamp'].dt.year == ano_inicio)]
    else:
        alunos_iniciaram = df_final[df_final['codigo'] == 'Iniciou']
    
    alunos_iniciaram_ids = alunos_iniciaram['id_discente'].unique()

    # Filtrar alunos que se formaram (possui "verificador" na coluna 'codigo')
    alunos_formados = df_final[(df_final['id_discente'].isin(alunos_iniciaram_ids)) & (df_final['codigo'] == 'verificador')]
    formados_ids = alunos_formados['id_discente'].unique()

    # Filtrar alunos ativos (cursaram algo em 2023 e não possuem "verificador")
    alunos_ativos = df_final[(df_final['id_discente'].isin(alunos_iniciaram_ids)) &
                             (df_final['timestamp'].dt.year == 2023) &
                             (~df_final['id_discente'].isin(formados_ids))]
    ativos_ids = alunos_ativos['id_discente'].unique()

    # Filtrar alunos evadidos (não possuem "verificador" e não cursaram nada em 2023)
    alunos_evadidos_ids = set(alunos_iniciaram_ids) - set(formados_ids) - set(ativos_ids)

    # Gerar tabela com os resultados

    resultado2 = [
        {
            'Status': 'Formados',
            'Quantidade': len(formados_ids),
        },
        {
            'Status': 'Ativos',
            'Quantidade': len(ativos_ids),
        },
        {
            'Status': 'Evadidos',
            'Quantidade': len(alunos_evadidos_ids),
        }
    ]

    return resultado2

def disciplinas_com_mais_supressoes(selecao=None):
    """
    Identifica as disciplinas com maior número de supressões.

    Parâmetros:
    - df_final: DataFrame com os dados dos alunos e disciplinas.
    - selecao: Pode ser:
        * Um ano específico (int) -> Visualização por turma (alunos que iniciaram no ano).
        * Uma faixa de anos (list) -> Visualização por período (supressões ocorridas no período).
        * None -> Todos os anos.

    Retorno:
    - DataFrame: Disciplinas com supressões, nomes e quantidade em ordem decrescente.
    """

    # Filtrar apenas os registros com supressão
    supressoes = df_final[df_final['codigo'].str.contains('_SUPRIMIDO', na=False)].copy()

    # Criar uma nova coluna para extrair o código da disciplina
    supressoes['Código'] = supressoes['codigo'].str.split('_').str[0]

    # Filtrar conforme o parâmetro `selecao`
    if selecao is not None:
        if isinstance(selecao, int):
            # Filtrar por ano específico (turma)
            alunos_iniciaram = df_final[
                (df_final['codigo'] == 'Iniciou') & 
                (df_final['timestamp'].dt.year == selecao)
            ]['id_discente'].unique()
            supressoes = supressoes[supressoes['id_discente'].isin(alunos_iniciaram)]

        elif isinstance(selecao, list) and len(selecao) == 2:
            # Filtrar por faixa de anos (período)
            ano_inicio, ano_fim = selecao
            supressoes = supressoes[supressoes['timestamp'].dt.year.between(ano_inicio, ano_fim)]

        else:
            raise ValueError(
                "Selecao deve ser None, um inteiro (ano específico), ou uma lista com dois elementos [ano_inicio, ano_fim]."
            )

    # Contar as supressões por disciplina
    if supressoes.empty:
        return pd.DataFrame(columns=['Código', 'Nome', 'Quantidade'])

    supressoes_por_disciplina = supressoes['Código'].value_counts().reset_index()
    supressoes_por_disciplina.columns = ['Código', 'Quantidade']

    # Adicionar a coluna 'Nome' com base no mapeamento
    supressoes_por_disciplina['Nome'] = supressoes_por_disciplina['Código'].map(codigo_para_nome)

    # Reorganizar as colunas para que 'Nome' fique no meio
    supressoes_por_disciplina = supressoes_por_disciplina[['Código', 'Nome', 'Quantidade']]

    # Retornar a tabela ordenada por número de supressões
    return supressoes_por_disciplina


def disciplinas_com_mais_trancamentos(selecao=None):
    """
    Identifica as disciplinas com maior número de trancamentos.

    Parâmetros:
    - df_final: DataFrame com os dados dos alunos e disciplinas.
    - selecao: Pode ser:
        * Um ano específico (int) -> Visualização por turma (alunos que iniciaram no ano).
        * Uma faixa de anos (list) -> Visualização por período (trancamentos ocorridos no período).
        * None -> Todos os anos.

    Retorno:
    - DataFrame: Disciplinas com trancamentos, nomes e quantidade em ordem decrescente.
    """

    # Filtrar apenas os registros com trancamentos
    trancamentos = df_final[df_final['codigo'].str.contains('_TRANCADO', na=False)].copy()

    # Criar uma nova coluna para extrair o código da disciplina
    trancamentos['Código'] = trancamentos['codigo'].str.split('_').str[0]

    # Filtrar conforme o parâmetro `selecao`
    if selecao is not None:
        if isinstance(selecao, int):
            # Filtrar por ano específico (turma)
            alunos_iniciaram = df_final[
                (df_final['codigo'] == 'Iniciou') & 
                (df_final['timestamp'].dt.year == selecao)
            ]['id_discente'].unique()
            trancamentos = trancamentos[trancamentos['id_discente'].isin(alunos_iniciaram)]

        elif isinstance(selecao, list) and len(selecao) == 2:
            # Filtrar por faixa de anos (período)
            ano_inicio, ano_fim = selecao
            trancamentos = trancamentos[trancamentos['timestamp'].dt.year.between(ano_inicio, ano_fim)]

        else:
            raise ValueError(
                "Selecao deve ser None, um inteiro (ano específico), ou uma lista com dois elementos [ano_inicio, ano_fim]."
            )

    # Contar os trancamentos por disciplina
    if trancamentos.empty:
        return pd.DataFrame(columns=['Código', 'Nome', 'Quantidade'])

    trancamentos_por_disciplina = trancamentos['Código'].value_counts().reset_index()
    trancamentos_por_disciplina.columns = ['Código', 'Quantidade']

    # Adicionar a coluna 'Nome' com base no mapeamento
    trancamentos_por_disciplina['Nome'] = trancamentos_por_disciplina['Código'].map(codigo_para_nome)

    # Reorganizar as colunas para que 'Nome' fique no meio
    trancamentos_por_disciplina = trancamentos_por_disciplina[['Código', 'Nome', 'Quantidade']]

    # Retornar a tabela ordenada por número de trancamentos
    return trancamentos_por_disciplina.sort_values(by='Quantidade', ascending=False)


def consolidar_metricas(selecao=None):
    """
    Consolida as métricas de gargalo, taxa de aprovação, supressões e trancamentos em uma única tabela.

    Parâmetros:
    - df_final: DataFrame com os dados de disciplinas e alunos.
    - selecao: Ano específico (int), faixa de anos (list) ou None (todos os anos).

    Retorno:
    - DataFrame consolidado com as colunas:
        - Código: Código da disciplina.
        - Nome: Nome da disciplina.
        - Gargalo: Número de alunos que enfrentaram gargalos (inteiro).
        - Taxa de Aprovação (%): Porcentagem de aprovação (2 casas decimais).
        - Supressões: Número de supressões na disciplina (inteiro).
        - Trancamentos: Número de trancamentos na disciplina (inteiro).
    """
    
    # Calcular métricas individuais
    gargalos_por_disciplina = disciplinas_com_maior_gargalo(selecao)
    supressoes_por_disciplina = disciplinas_com_mais_supressoes(selecao)
    trancamentos_por_disciplina = disciplinas_com_mais_trancamentos(selecao)
    total_aprovacoes, alunos_por_disciplina = calcular_taxa_aprovacao_primeira_vez(selecao)

    # Taxa de aprovação em porcentagem
    taxa_aprovacao = ((total_aprovacoes / alunos_por_disciplina) * 100).fillna(0).reset_index()
    taxa_aprovacao.columns = ['Código', 'Taxa de Aprovação (%)']

    # Garantir que a coluna Nome esteja em todos os DataFrames
    gargalos_por_disciplina = gargalos_por_disciplina.rename(columns={'Quantidade': 'Gargalo'})
    supressoes_por_disciplina = supressoes_por_disciplina.rename(columns={'Quantidade': 'Supressões'})
    trancamentos_por_disciplina = trancamentos_por_disciplina.rename(columns={'Quantidade': 'Trancamentos'})

    # Criar a coluna Nome com base no mapeamento, se necessário
    gargalos_por_disciplina['Nome'] = gargalos_por_disciplina['Código'].map(codigo_para_nome)
    supressoes_por_disciplina['Nome'] = supressoes_por_disciplina['Código'].map(codigo_para_nome)
    trancamentos_por_disciplina['Nome'] = trancamentos_por_disciplina['Código'].map(codigo_para_nome)
    taxa_aprovacao['Nome'] = taxa_aprovacao['Código'].map(codigo_para_nome)

    # Mesclar os resultados em uma única tabela
    consolidado = pd.merge(gargalos_por_disciplina, taxa_aprovacao, on=['Código', 'Nome'], how='outer')
    consolidado = pd.merge(consolidado, supressoes_por_disciplina, on=['Código', 'Nome'], how='outer')
    consolidado = pd.merge(consolidado, trancamentos_por_disciplina, on=['Código', 'Nome'], how='outer')

    # Preencher valores NaN com 0 (para disciplinas sem dados em alguma métrica)
    consolidado = consolidado.fillna(0)

    # Garantir tipos adequados para cada coluna
    consolidado['Gargalo'] = consolidado['Gargalo'].astype(int)
    consolidado['Supressões'] = consolidado['Supressões'].astype(int)
    consolidado['Trancamentos'] = consolidado['Trancamentos'].astype(int)
    consolidado['Taxa de Aprovação (%)'] = consolidado['Taxa de Aprovação (%)'].round(2)

    # Reordenar as colunas
    consolidado = consolidado[['Código', 'Nome', 'Gargalo', 'Taxa de Aprovação (%)', 'Supressões', 'Trancamentos']]

    return consolidado.to_json(orient='records')
