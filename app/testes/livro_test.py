import unittest
from ..models.livro import Livro

class TestLivro(unittest.TestCase):
    
    def test_livro_init(self):
        # Testando a inicialização do objeto Livro
        livro = Livro(isbn="1234567890", autor="Autor Teste", titulo="Título Teste")
        
        # Verificando se os atributos foram definidos corretamente
        self.assertEqual(livro.isbn, "1234567890")
        self.assertEqual(livro.autor, "Autor Teste")
        self.assertEqual(livro.titulo, "Título Teste")

    def test_livro_isbn(self):
        # Testando se o ISBN está sendo armazenado corretamente
        livro = Livro(isbn="9876543210", autor="Outro Autor", titulo="Outro Título")
        self.assertEqual(livro.isbn, "9876543210")

    def test_livro_autor(self):
        # Testando se o autor está sendo armazenado corretamente
        livro = Livro(isbn="5432109876", autor="Mais Um Autor", titulo="Mais Um Título")
        self.assertEqual(livro.autor, "Mais Um Autor")

    def test_livro_titulo(self):
        # Testando se o título está sendo armazenado corretamente
        livro = Livro(isbn="3216549870", autor="Autor Final", titulo="Título Final")
        self.assertEqual(livro.titulo, "Título Final")

if __name__ == '__main__':
    unittest.main()
