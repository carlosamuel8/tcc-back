from flask import jsonify

# -------------------------------------------------------------------------------------------
# Importações básicas
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.petri_net.importer import importer as pnml_importer
# from IPython.display import Image

# -------------------------------------------------------------------------------------------
# Importação da Rede de Petri
# from xml.etree import ElementTree as ET
# from pm4py.objects.petri_net.importer import importer as pnml_importer
# from pm4py.objects.petri_net.exporter import exporter as pnml_exporter


# def import_petri():
#     # Caminho para o arquivo PNML
#     pnml_file = "data/MODELAGEMCOMPLETACC_sem_reprovacoes.pnml"

#     # Parse do arquivo PNML para XML
#     tree = ET.parse(pnml_file)
#     root = tree.getroot()

#     # Mapeamento de IDs de places para os textos de nome
#     id_to_text = {}
#     for place in root.findall(".//place"):
#         place_id = place.get("id")
#         text_element = place.find("./name/text")
#         if text_element is not None:
#             id_to_text[place_id] = text_element.text.strip()

#     # Importar a rede de Petri com PM4Py
#     net, initial_marking, final_marking = pnml_importer.apply(pnml_file)

#     # Atualizar os nomes dos lugares com base no mapeamento extraído
#     for place in net.places:
#         if place.name in id_to_text:
#             place.properties['custom_name'] = id_to_text[place.name]  # Adicionar como propriedade
#             place.name = id_to_text[place.name]  # Atualizar o nome diretamente

#     # Exportar a rede com os nomes atualizados
#     pnml_exporter.apply(net, initial_marking, "data/output/updated_petri_net_with_correct_names.pnml")
    
#     return jsonify({
#         "message": "Petri FN!",
#         "status": "success"
#     })
    
# -------------------------------------------------------------------------------------------
# Gerar imagem
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.visualization.petri_net import visualizer as pn_visualizer

def gen_image():
    netCC, initial_marking, final_marking = pnml_importer.apply("data/MODELAGEMCOMPLETACC_sem_reprovacoes.pnml")
    
    # Gerando a visualização
    gviz = pn_visualizer.apply(netCC, initial_marking, final_marking)

    # Salvando a imagem como PNG
    pn_visualizer.save(gviz, "./rede_petri.png")

    # Exibindo a imagem dentro do notebook
    # display(Image("/content/rede_petri.png"))
    return jsonify({
        "message": "Imagem FN!",
        "status": "success"
    })