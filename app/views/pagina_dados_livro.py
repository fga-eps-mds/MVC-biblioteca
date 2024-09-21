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
