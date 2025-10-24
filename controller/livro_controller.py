# Material traduzido e adaptado de:
# Marco Tulio Valente. Engenharia de Software Moderna: Princípios e Práticas para Desenvolvimento de Software com Produtividade, Editora: Independente, 2020.
# UnB-FGA-EPS-MDS

from dao.db_connection import conectar
from dao.livro_dao import LivroDAO

def listar_livro(autor):
    conn = conectar()
    dao = LivroDAO(conn)
    livros = dao.pesquisar_por_autor(autor)
    conn.close()
    html = '<h4>Dados do Livro Pesquisado</h4><ul>'
    if livros:
        for livro in livros:
            html += (f'<li>Título: {livro.titulo}</li>'
                     f'</li>Autor: {livro.autor}</li>'
                     f'</li>ISBN: {livro.isbn}</li>')
        html += '</ul>'
        return html
    return "Livro não encontrado", 404