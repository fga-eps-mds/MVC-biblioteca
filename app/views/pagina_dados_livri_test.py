import unittest
from pagina_dados_livro import PaginaDadosLivro

class TestPaginaDadosLivro(unittest.TestCase):

    def setUp(self):
        self.pagina = PaginaDadosLivro()

    def test_exibe_livro(self):
        titulo = "O Senhor dos Anéis"
        autor = "J.R.R. Tolkien"
        isbn = "978-3-16-148410-0"

        resultado = self.pagina.exibe_livro(titulo, autor, isbn)

        # Verifica se a saída contém os dados corretos
        self.assertIn("<h4> Dados do Livro Pesquisado </h4>", resultado)
        self.assertIn("<li> Título: O Senhor dos Anéis </li>", resultado)
        self.assertIn("<li> Autor: J.R.R. Tolkien </li>", resultado)
        self.assertIn("<li> ISBN: 978-3-16-148410-0 </li>", resultado)

    def test_exibe_livro_com_dados_vazios(self):
        resultado = self.pagina.exibe_livro("", "", "")

        # Verifica se a saída contém campos vazios
        self.assertIn("<li> Título:  </li>", resultado)
        self.assertIn("<li> Autor:  </li>", resultado)
        self.assertIn("<li> ISBN:  </li>", resultado)

if __name__ == '__main__':
    unittest.main()
