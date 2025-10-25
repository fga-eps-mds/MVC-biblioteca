# Material traduzido e adaptado de:
# Marco Tulio Valente. Engenharia de Software Moderna: Princípios e Práticas para Desenvolvimento de Software com Produtividade, Editora: Independente, 2020.
# UnB-FGA-EPS-MDS

class PaginaDadosLivro:
    @staticmethod
    def exibe_livro(titulo, autor, isbn):
        return f"""
        <meta charset="UTF-8">
        <link rel="stylesheet" href="/static/css/style.css">
        <h1> Dados do Livro Pesquisado </h1>
        <ul>
            <li> Título: {titulo} </li>
            <li> Autor: {autor} </li>
            <li> ISBN: {isbn} </li>
        </ul>
        """
