# Material traduzido e adaptado de:
# Marco Tulio Valente. Engenharia de Software Moderna: Princípios e Práticas para Desenvolvimento de Software com Produtividade,     Editora: Independente, 2020.
# UnB-FGA-EPS-MDS

from dao.db_connection import conectar
from dao.livro_dao import LivroDAO

def listar_livros():
    conn = conectar()
    dao = LivroDAO(conn)
    livros = dao.listar()
    conn.close()
    html = '<h1>Lista de Livros</h1><ul>'
    if livros:
        for livro in livros:
            html += f'<li>{livro.titulo} - {livro.autor}</li>'
        html += '</ul>'
        return html
    return "Livro não encontrado", 404