from flask import send_file

from app.utils.process_csv import process
from app.utils.alunos import visualizar_taxa_aprovacao_por_turma2

def generate_image(year):
    filename = 'turma_{}_taxa_aprovacao.png'.format(year)

    result = process()
    visualizar_taxa_aprovacao_por_turma2(result, year, filename)
    
    return send_file(filename, mimetype='image/png')
