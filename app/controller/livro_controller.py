# Material traduzido e adaptado de:
# Marco Tulio Valente. Engenharia de Software Moderna: Princípios e Práticas para Desenvolvimento de Software com Produtividade, Editora: Independente, 2020.
# UnB-FGA-EPS-MDS

from app.dao.db_connection import conectar
from app.dao.livro_dao import LivroDAO
from app.view.pagina_dados_livro import PaginaDadosLivro


def listar_livro(autor):
    conn = conectar()
    dao = LivroDAO(conn)
    livro_pesquisado = dao.pesquisar_por_autor(autor)
    conn.close()
    if livro_pesquisado:
        return PaginaDadosLivro.exibe_livro(livro_pesquisado[0].titulo, livro_pesquisado[0].autor, livro_pesquisado[0].isbn)
    return "Livro não encontrado", 404