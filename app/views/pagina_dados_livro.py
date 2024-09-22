# Material traduzido e adaptado de:
# Marco Tulio Valente. Engenharia de Software Moderna: Princípios e Práticas para Desenvolvimento de Software com Produtividade,     Editora: Independente, 2020.
# UnB-FGA-EPS-MDS

class PaginaDadosLivro:
    def exibe_livro(self, titulo, autor, isbn):
        return f"""
        <h4> Dados do Livro Pesquisado </h4>
        <ul>
            <li> Título: {titulo} </li>
            <li> Autor: {autor} </li>
            <li> ISBN: {isbn} </li>
        </ul>
        """
