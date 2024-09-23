import unittest
from unittest.mock import patch, MagicMock
from app.models.livro import Livro
from app.models.servico_pesquisa_livros import ServicoPesquisaLivros

class TestServicoPesquisaLivros(unittest.TestCase):

    @patch('psycopg2.connect')
    #Simula a busca por um autor e verifica se o retorno não é None e se o ISBN está correto.
    def test_pesquisa_por_autor_sucesso(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ('123456789', 'Autor Teste', 'Título Teste')

        servico = ServicoPesquisaLivros()
        resultado = servico.pesquisa_por_autor('Autor Teste')

        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.isbn, '123456789')

    @patch('psycopg2.connect')
    #Simula a busca por um autor que não existe e verifica se o retorno é None.
    def test_pesquisa_por_autor_sem_resultados(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        servico = ServicoPesquisaLivros()
        resultado = servico.pesquisa_por_autor('Autor Inexistente')

        self.assertIsNone(resultado)

if __name__ == '__main__':
    unittest.main()
