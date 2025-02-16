import pm4py
import pandas as pd
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from collections import defaultdict
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pygraphviz as pgv


codigo_para_nome = {

    "QXD0001": "Fund. de Programação",
    "QXD0108": "Introdução à CC", 
    "QXD0005": "Arq. de Computadores", 
    "QXD0056": "Matem. Básica",
    "QXD0109": "Pré-Cálculo", 
    "QXD0103": "Ética, Dir. e Legislação",

    
    "QXD0007": "Program. Orient. a Objet.",
    "QXD0010": "Estrut. de dados",
    "QXD0008": "Matem. Discreta",
    "QXD0006": "Cálc. Difer. e Integ. I",
    "QXD0013": "Sist. Operacionais",
    
    
    "QXD0114": "Program. Funcional",
    "QXD0115": "Estrut. de Dados Avanç.",
    "QXD0040": "Ling. Form. e Autômatos",
    "QXD0017": "Lógica p/ Computação",
    "QXD0012": "Probab. de Estatística",

    "QXD0016": "Ling. de Programação",
    "QXD0041": "Proj. e Anál. de Algorit.",
    "QXD0011": "Fund. de Banco de Dados",
    "QXD0014": "Análise e Proj. de Sist.",
    "QXD0116": "Álgebra Linear",


    "QXD0020": "Des. de Software p/ Web",
    "QXD0119": "Computação Gráfica",
    "QXD0120": "Matem. Computacional",
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


# Carregar o log de eventos
df_final = pd.read_csv('./data/logfinal.csv')
df_final['timestamp'] = pd.to_datetime(
    df_final['timestamp'], format='%Y-%m-%d')
netCC, initial_marking, final_marking = pnml_importer.apply(
    "./data/MODELAGEMCOMPLETACC_sem_reprovacoes.pnml")

# Gerando a visualização
gviz = pn_visualizer.apply(netCC, initial_marking, final_marking)

# Salvando a imagem como PNG
pn_visualizer.save(gviz, "./app/images/rede_petri.png")


def visualizar_turma_heatmap(petri_net, initial_marking, final_marking, reached_marking_result):
    """
    Visualiza a rede de Petri com coloração em heatmap nos lugares de acordo com a quantidade de tokens.
    :param petri_net: Rede de Petri.
    :param initial_marking: Marcador inicial.
    :param final_marking: Marcador final.
    :param reached_marking_result: Dicionário com os tokens restantes por lugar.
    :param output_path: Caminho para salvar a imagem gerada.
    """
    # Obter valores de tokens e normalizar
    token_values = list(reached_marking_result.values())
    max_tokens = max(token_values)
    min_tokens = min(token_values)

    # Normalização entre 0 e 1
    norm = mcolors.Normalize(vmin=min_tokens, vmax=max_tokens)
    cmap = plt.cm.Blues  # Escolha o esquema de cores

    # Criar o grafo
    G = pgv.AGraph(strict=False, directed=True)

    # Adicionar lugares com coloração de heatmap
    for place in petri_net.places:
        token_count = reached_marking_result.get(place, 0)
        normalized_value = norm(token_count)
        color = mcolors.to_hex(cmap(normalized_value))

        # Diferenciar marcadores iniciais e finais
        if place in initial_marking:
            G.add_node(place.name, shape="circle", label=f"{place.name}\nTokens: {
                       token_count}", style="filled", fillcolor="lightblue")
        elif place in final_marking:
            G.add_node(place.name, shape="circle", label=f"{place.name}\nTokens: {
                       token_count}", style="filled", fillcolor="lightgreen")
        else:
            G.add_node(place.name, shape="circle", label=f"{place.name}\nTokens: {
                       token_count}", style="filled", fillcolor=color)

    # Adicionar transições e arcos
    for transition in petri_net.transitions:
        G.add_node(transition.name, shape="box",
                   label=transition.label, color="gray")

    for arc in petri_net.arcs:
        G.add_edge(arc.source.name, arc.target.name)

    nome_arquivo = 'petri_net_heatmap.png'

    G.layout(prog='dot')
    G.draw('app/images/{}'.format(nome_arquivo))

    return nome_arquivo


def consolidate_reached_markings(replayed_traces):
    """
    Consolida as informações de reached_marking de todos os traces no replayed_traces.

    :param replayed_traces: Lista de traces com informações de reached_marking.
    :return: Um dicionário consolidado com os lugares e o total de tokens por lugar.
    """
    consolidated_markings = defaultdict(int)

    for trace in replayed_traces:
        reached_marking = trace.get("reached_marking", {})
        for place, tokens in reached_marking.items():
            consolidated_markings[place] += tokens

    return dict(consolidated_markings)


def visualizar_fluxograma_tokens(
    petri_net, tokens_por_disciplina, cmap_nome="Blues", titulo="Fluxograma de Tokens"
):
    """
    Gera um fluxograma com base nos tokens consolidados por disciplina.

    :param petri_net: Rede de Petri.
    :param tokens_por_disciplina: Dicionário consolidado com os tokens por disciplina.
    :param cmap_nome: Nome do colormap a ser usado.
    :param titulo: Título do fluxograma.
    """
    # Normalizar valores dos tokens para o colormap
    token_values = list(tokens_por_disciplina.values())
    max_tokens = max(token_values) if token_values else 1
    min_tokens = min(token_values) if token_values else 0
    norm = mcolors.Normalize(vmin=min_tokens, vmax=max_tokens)
    cmap = plt.get_cmap(cmap_nome)

    # Disciplinas organizadas por blocos
    disciplinas = [
        ["QXD0001", "QXD0108", "QXD0005", "QXD0109", "QXD0103", "QXD0056"],
        ["QXD0007", "QXD0010", "QXD0013", "QXD0006", "QXD0008"],
        ["QXD0115", "QXD0017", "QXD0114", "QXD0012", "QXD0040"],
        ["QXD0011", "QXD0014", "QXD0016", "QXD0041", "QXD0116"],
        ["QXD0020", "QXD0021", "QXD0025", "QXD0119", "QXD0120"],
        ["QXD0019", "QXD0037", "QXD0038", "QXD0043", "QXD0046"],
        ["QXD0029", "QXD0110"],
    ]

    transicoes = {
        "QXD0001": ["QXD0007", "QXD0010"],
        "QXD0005": ["QXD0013"],
        "QXD0056": ["QXD0008", "QXD0012"],
        "QXD0109": ["QXD0006"],
        "QXD0007": ["QXD0016", "QXD0020", "QXD0014", "QXD0019"],
        "QXD0010": ["QXD0115", "QXD0041"],
        "QXD0008": ["QXD0040", "QXD0041"],
        "QXD0013": ["QXD0043"],
        "QXD0116": ["QXD0119", "QXD0120"],
        "QXD0046": ["QXD0110"],
    }

    # Criar o gráfico
    G = pgv.AGraph(strict=False, directed=True, rankdir='TB')
    G.graph_attr['splines'] = 'ortho'
    G.graph_attr['nodesep'] = '0.6'
    G.graph_attr['ranksep'] = '0.7'


    subgraphs = []
    for i, linha in enumerate(disciplinas):
        with G.subgraph(name="cluster_" + str(i)) as s:
            s.graph_attr['rank'] = 'same'
            s.graph_attr['color'] = 'transparent'
            for disciplina in linha:
                tokens = tokens_por_disciplina.get(
                    disciplina, 0)  # Obter tokens da disciplina
                cor = mcolors.to_hex(cmap(norm(tokens)))
                nome_disciplina = codigo_para_nome.get(
                    disciplina, "Desconhecido")  # Obter nome da disciplina
                label = f"{disciplina}\n{nome_disciplina}\nTokens: {
                    tokens}"  # Exibir código, nome e tokens
                s.add_node(
                    disciplina,
                    shape='box',
                    style='filled',
                    fillcolor=cor,
                    fontsize=19,  # Font size padrão para fallback
                    fontname='Arial',  # Fonte principal
                    label=label,  # Label formatado com HTML-like
                    fixedsize=True,
                    width=3,
                    height=1.8
                )
            subgraphs.append(s)

    # Adicionar transições (arestas)
    for origem, destinos in transicoes.items():
        for destino in destinos:
            G.add_edge(origem, destino, directed=True,
                       arrowhead='normal', constraint=False)

    # Adicionar arestas invisíveis para alinhar blocos
    for i in range(len(subgraphs) - 1):
        node1 = list(subgraphs[i].nodes())[0]
        node2 = list(subgraphs[i + 1].nodes())[0]
        G.add_edge(node1, node2, style='invis', weight=10)

    # Nome do arquivo
    nome_arquivo = "fluxograma_tokens.png"

    G.layout(prog='dot')
    G.draw('app/images/{}'.format(nome_arquivo))

    return nome_arquivo


def consolidar_tokens_por_disciplina(petri_net, reached_marking_result):
    """
    Consolida os tokens em lugares intermediários entre as transições QXD001 -> QXD001_APROVADO.

    :param petri_net: Rede de Petri.
    :param reached_marking_result: Dicionário com os tokens em cada lugar.
    :return: Dicionário consolidado com os tokens por disciplina.
    """
    tokens_por_disciplina = defaultdict(int)

    for place in petri_net.places:
        # Verificar se o lugar está conectado entre "QXD001" e "QXD001_APROVADO"
        entrada_disciplinas = [
            arc.source.label for arc in place.in_arcs if arc.source.label and arc.source.label.startswith("QXD")
        ]
        saida_disciplinas = [
            arc.target.label for arc in place.out_arcs if arc.target.label and arc.target.label.endswith("_APROVADO")
        ]

        # Consolidar tokens se as condições forem atendidas
        if entrada_disciplinas and saida_disciplinas:
            for entrada in entrada_disciplinas:
                disciplina = entrada
                tokens_por_disciplina[disciplina] += reached_marking_result.get(
                    place, 0)

    return dict(tokens_por_disciplina)

def generate_process_mining_grafico_barra(replayed_traces):
    metricas = ["trace_fitness", "missing_tokens", "consumed_tokens", "remaining_tokens"]
    titulos = ["Média do Trace Fitness", "Média de Missing Tokens", "Média de Consumed Tokens", "Média de Remaining Tokens"]

    traces_results = []

    for trace_result in replayed_traces:
        # Verificar se o aluno se formou (presença da transição 'verificador' nas transições ativadas)
        aluno_formado = any(transition.label == 'verificador' for transition in trace_result['activated_transitions'])

        traces_results.append({
            'trace_type': 'Aluno Formado' if aluno_formado else 'Aluno Não Formado',
            'trace_fitness': trace_result['trace_fitness'],
            'missing_tokens': trace_result['missing_tokens'],
            'consumed_tokens': trace_result['consumed_tokens'],
            'remaining_tokens': trace_result['remaining_tokens'],
            'produced_tokens': trace_result['produced_tokens']
        })

    df_traces = pd.DataFrame(traces_results)

    # Separar os dados em dois grupos
    formados = df_traces[df_traces['trace_type'] == 'Aluno Formado']
    nao_formados = df_traces[df_traces['trace_type'] == 'Aluno Não Formado']

    # Calcular estatísticas descritivas para cada grupo
    estatisticas_formados = formados.describe()
    estatisticas_nao_formados = nao_formados.describe()

    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    cores = ["blue", "red"]

    for i, ax in enumerate(axes.flatten()):
        ax.bar(["Formados", "Não Formados"],
            [estatisticas_formados[metricas[i]].mean(), estatisticas_nao_formados[metricas[i]].mean()],
            color=cores)
        ax.set_title(titulos[i])
        ax.set_ylabel("Valor")

    plt.tight_layout()
    # plt.show()

    # Definir as métricas e títulos
    metricas = ["trace_fitness", "missing_tokens", "consumed_tokens", "remaining_tokens"]
    titulos = ["Média do Trace Fitness", "Média de Missing Tokens", "Média de Consumed Tokens", "Média de Remaining Tokens"]

    nome_arquivo = "grafico_barras.png"

    plt.savefig('app/images/{}'.format(nome_arquivo))
    print("salvooou")
    return nome_arquivo




def executar_replay(faixa, tipo_visualizacao):
    print(f"Executando replay para a faixa de anos: {faixa}")
    ano_inicio, ano_fim = faixa

    # Filtrar pelo intervalo de anos
    df_filtrado = df_final[
        (df_final['timestamp'].dt.year >= ano_inicio) &
        (df_final['timestamp'].dt.year <= ano_fim)
    ].copy()

    # Transformar o df em log de eventos
    dataframelog = pm4py.format_dataframe(
        df_filtrado, case_id='id_discente', activity_key='codigo', timestamp_key='timestamp')

    # Fazer o replay
    replayed_traces = token_replay.apply(
        dataframelog, netCC, initial_marking, final_marking)



    # Prepaar os tokens
    result = consolidate_reached_markings(replayed_traces)

    # Consolidar tokens por disciplina
    tokens_por_disciplina = consolidar_tokens_por_disciplina(
        petri_net=netCC, reached_marking_result=result)

    if tipo_visualizacao == "barras":
        # Gerar o gráfico de barras
        nome_arquivo = generate_process_mining_grafico_barra(replayed_traces)

        return nome_arquivo

    if tipo_visualizacao == "petrinet":
        # Desenhar a rede de petri com a quantidade de tokens
        nome_arquivo1 = visualizar_turma_heatmap(
            petri_net=netCC,
            initial_marking=initial_marking,
            final_marking=final_marking,
            reached_marking_result=result,
        )

        return nome_arquivo1
    
    elif tipo_visualizacao == "fluxograma":
        nome_arquivo2 = visualizar_fluxograma_tokens(
            petri_net=netCC,
            tokens_por_disciplina=tokens_por_disciplina,  # Passar tokens consolidados
            cmap_nome="Blues",  # Ou outro colormap de sua escolha
            titulo="Fluxograma de Tokens"
        )

        return nome_arquivo2
    else:
        raise ValueError("Tipo de visualização inválido. Deve ser 'petrinet' ou 'fluxograma'.")
