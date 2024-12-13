import pandas as pd
import pygraphviz as pgv
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import os

def calcular_taxa_aprovacao_primeira_vez(df_final, ano):
    """
    Função para calcular a taxa de aprovação de cada disciplina no ano selecionado.

    Parâmetros:
    - df_final: DataFrame com as informações de atividades dos alunos.
    - ano: Ano da turma a ser considerada.

    Retorna:
    - taxa_aprovacao: DataFrame com a taxa de aprovação por disciplina.
    - alunos_por_disciplina: Contagem de alunos que cursaram cada disciplina.
    """
    # Filtrar apenas os alunos que começaram no ano especificado
    alunos_ano = df_final[(df_final['codigo'] == 'Iniciou') & (df_final['timestamp'].dt.year == ano)]['id_discente'].unique()

    # Filtra o DataFrame para os alunos e disciplinas relevantes
    df_ano = df_final[df_final['id_discente'].isin(alunos_ano)]

    # Criar a coluna 'disciplina' para capturar o código base da atividade
    df_ano['disciplina'] = df_ano['codigo'].str.split('_').str[0]

    # Filtrar apenas as atividades relevantes (excluir "Iniciou" e "verificador")
    disciplinas = df_ano[~df_ano['codigo'].isin(['Iniciou', 'verificador'])]

    # Ordenar o DataFrame por aluno, disciplina e timestamp
    disciplinas = disciplinas.sort_values(by=['id_discente', 'disciplina', 'timestamp'])

    # Identificar a segunda ocorrência para cada aluno e disciplina (primeira com resultado)
    disciplinas['ocorrencia'] = disciplinas.groupby(['id_discente', 'disciplina']).cumcount() + 1
    segunda_ocorrencia = disciplinas[disciplinas['ocorrencia'] == 2]

    # Verificar se essa segunda ocorrência foi uma aprovação
    segunda_ocorrencia['aprovado'] = segunda_ocorrencia['codigo'].str.contains('_APROVADO', na=False)

    # Calcular a taxa de aprovação por disciplina
    taxa_aprovacao = (
        segunda_ocorrencia.groupby('disciplina')['aprovado']
        .mean()  # Calcular a média de aprovações
        .sort_values(ascending=False)
    )

    # Contar o número de alunos que cursaram cada disciplina
    alunos_por_disciplina = df_ano.groupby('disciplina')['id_discente'].nunique()

    return taxa_aprovacao, alunos_por_disciplina


def visualizar_taxa_aprovacao_por_turma2(df_final, ano):
    """
    Função para visualizar a taxa de aprovação de uma turma de um determinado ano.
    O gráfico será colorido com base nas taxas de aprovação por disciplina e mostrará quantos alunos cursaram cada disciplina.

    Parâmetros:
    - df_final: DataFrame com as informações de atividades dos alunos.
    - ano: Ano da turma a ser visualizada.
    """
    # Calcular a taxa de aprovação e a quantidade de alunos por disciplina para cada disciplina do ano
    taxa_aprovacao, alunos_por_disciplina = calcular_taxa_aprovacao_primeira_vez(df_final, ano)

    # Define as disciplinas (manter a lista original de disciplinas)
    disciplinas = [
        ["QXD0001", "QXD0108", "QXD0005", "QXD0109", "QXD0103", "QXD0056"],
        ["QXD0007", "QXD0010", "QXD0013", "QXD0006", "QXD0008"],
        ["QXD0115", "QXD0017", "QXD0114", "QXD0012", "QXD0040"],
        ["QXD0011", "QXD0014", "QXD0016", "QXD0041", "QXD0116"],
        ["QXD0020", "QXD0021", "QXD0025", "QXD0119", "QXD0120"],
        ["QXD0019", "QXD0037", "QXD0038", "QXD0043", "QXD0046"],
        ["QXD0029", "QXD0110"],
    ]

    # Criar o gráfico
    G = pgv.AGraph(strict=False, directed=True, rankdir='TB')
    G.graph_attr['splines'] = 'ortho'
    G.graph_attr['nodesep'] = '0.55'
    G.graph_attr['ranksep'] = '0.5'

    subgraphs = []  # Lista para armazenar os subgrafos (linhas de disciplinas)

    # Definir o mapa de cores (degradê sensível a valores baixos)
    cmap = plt.get_cmap("RdYlBu")  # Red-Yellow-Blue, com ênfase em valores baixos (vermelho)
    norm = mcolors.Normalize(vmin=0, vmax=1)  # Normaliza as taxas entre 0 e 1

    for i, linha in enumerate(disciplinas):
        with G.subgraph(name="cluster_" + str(i)) as s:
            s.graph_attr['rank'] = 'same'  # Coloca todos os nós na mesma linha
            s.graph_attr['color'] = 'transparent'  # Remove a borda do subgrafo
            for disciplina in linha:
                # Pega a taxa de aprovação e o número de alunos para a disciplina
                taxa = taxa_aprovacao.get(disciplina, 0)  # Caso não exista taxa, atribui 0
                alunos_count = alunos_por_disciplina.get(disciplina, 0)  # Conta quantos alunos cursaram

                # Ajusta a cor com base na taxa de aprovação
                cor = mcolors.to_hex(cmap(norm(taxa)))  # Converte a taxa para uma cor

                # Debug: Mostrar a disciplina, taxa, alunos e cor atribuída
                # print(f"Disciplina: {disciplina}, Taxa de Aprovação: {taxa:.2f}, Alunos: {alunos_count}, Cor: {cor}")

                label = f"{disciplina}\n{alunos_count} alunos\n{taxa*100:.2f}%"

                # Adiciona o nó (disciplina) com a cor determinada e rótulo com a quantidade de alunos
                s.add_node(disciplina, shape='box', style='filled', fillcolor=cor, label=label)
            subgraphs.append(s)

    # Conectar os subgrafos com arestas invisíveis para criar os níveis
    for i in range(len(subgraphs) - 1):
        node1 = list(subgraphs[i].nodes())[0]  # Primeiro nó do subgrafo atual
        node2 = list(subgraphs[i + 1].nodes())[0]  # Primeiro nó do próximo subgrafo
        G.add_edge(node1, node2, style='invis', weight=10)

    G.add_edge("QXD0001", "QXD0007", directed=True, arrowhead='normal', constraint=False,)
    G.add_edge("QXD0001", "QXD0010", directed=True, arrowhead='normal', constraint=False, )

    G.add_edge("QXD0005", "QXD0013", directed=True, arrowhead='normal', constraint=False, )

    G.add_edge("QXD0056", "QXD0008", directed=True, arrowhead='normal', constraint=False, )
    G.add_edge("QXD0056", "QXD0012", directed=True, arrowhead='normal', constraint=False, )

    G.add_edge("QXD0109", "QXD0006", directed=True, arrowhead='normal', constraint=False, )

# -------------
    G.add_edge("QXD0007", "QXD0016", directed=True, arrowhead='normal', constraint=False, )
    G.add_edge("QXD0007", "QXD0020", directed=True, arrowhead='normal', constraint=False,)
    G.add_edge("QXD0007", "QXD0014", directed=True, arrowhead='normal', constraint=False, )
    G.add_edge("QXD0007", "QXD0019", directed=True, arrowhead='normal', constraint=False, )

    G.add_edge("QXD0010", "QXD0115", directed=True, arrowhead='normal', constraint=False, )
    G.add_edge("QXD0010", "QXD0041", directed=True, arrowhead='normal', constraint=False, )

    G.add_edge("QXD0008", "QXD0040", directed=True, arrowhead='normal', constraint=False, )
    G.add_edge("QXD0008", "QXD0041", directed=True, arrowhead='normal', constraint=False,)

    G.add_edge("QXD0013", "QXD0043", directed=True, arrowhead='normal', constraint=False)

#-----------
    G.add_edge("QXD0116", "QXD0119", directed=True, arrowhead='normal', constraint=False, )
    G.add_edge("QXD0116", "QXD0120", directed=True, arrowhead='normal', constraint=False, )

#----------
    G.add_edge("QXD0046", "QXD0110", directed=True, arrowhead='normal', constraint=False,)


    # Gerar o gráfico e salvar como imagem

    G.layout(prog='dot')
    G.draw('turma_{}_taxa_aprovacao.png'.format(ano))

    # Exibir a imagem gerada
    return True
