import pytest
from types import SimpleNamespace
from mockito import mock, when, verify, ANY
import psycopg2

import app.dao.livro_dao as sut


def test_pesquisar_por_autor_quando_ha_resultados_retorna_lista_de_livros(monkeypatch):
    # Arrange
    conn = mock()
    cur = mock()
    when(conn).cursor().thenReturn(cur)
    when(cur).execute(ANY, ANY).thenReturn(None)
    rows = [
        ("9780132350884", "Clean Code", "Robert C. Martin"),
        ("9788576082675", "Código Limpo", "Robert C. Martin"),
    ]
    when(cur).fetchall().thenReturn(rows)
    when(cur).close().thenReturn(None)

    # Substitui Livro por uma classe simples para validar o mapeamento
    class FakeLivro:
        def __init__(self, isbn, titulo, autor):
            self.isbn = isbn
            self.titulo = titulo
            self.autor = autor
    monkeypatch.setattr(sut, "Livro", FakeLivro)

    dao = sut.LivroDAO(conn)

    # Act
    resultado = dao.pesquisar_por_autor("Robert C. Martin")

    # Assert
    assert isinstance(resultado, list)
    assert len(resultado) == 2
    assert resultado[0].isbn == "9780132350884"
    assert resultado[0].titulo == "Clean Code"
    assert resultado[0].autor == "Robert C. Martin"

    # Verifica SQL e parâmetros (uso de lower + like com %autor%)
    expected_sql = "SELECT isbn, titulo, autor FROM livros WHERE LOWER(autor) LIKE %s"
    expected_params = ("%robert c. martin%",)
    verify(cur).execute(expected_sql, expected_params)

    # Fecha o cursor no finally
    verify(cur).close()


def test_pesquisar_por_autor_sem_resultados_lista_vazia_retorna_none(monkeypatch):
    # Arrange
    conn = mock()
    cur = mock()
    when(conn).cursor().thenReturn(cur)
    when(cur).execute(ANY, ANY).thenReturn(None)
    when(cur).fetchall().thenReturn([])  # sem linhas
    when(cur).close().thenReturn(None)

    dao = sut.LivroDAO(conn)

    # Act
    resultado = dao.pesquisar_por_autor("Autor Desconhecido")

    # Assert
    assert resultado is None
    verify(cur).execute(ANY, ANY)
    verify(cur).fetchall()
    verify(cur).close()


def test_pesquisar_por_autor_excecao_em_execute_retorna_none_e_fecha_cursor(capsys, monkeypatch):
    """
    Simula uma falha do banco durante o execute(). O metodo deve:
      - Capturar psycopg2.Error,
      - Imprimir mensagem 'Erro no banco de dados: ...',
      - Retornar None,
      - Fechar o cursor no finally.
    """
    # Arrange
    conn = mock()
    cur = mock()
    when(conn).cursor().thenReturn(cur)
    when(cur).execute(ANY, ANY).thenRaise(psycopg2.Error("falhou"))
    when(cur).close().thenReturn(None)

    dao = sut.LivroDAO(conn)

    # Act
    resultado = dao.pesquisar_por_autor("Autor X")

    # Assert
    assert resultado is None

    out, _ = capsys.readouterr()
    assert "Erro no banco de dados:" in out

    verify(cur).close()


@pytest.mark.xfail(reason="EVIDENCIA BUG: se cursor() lançar psycopg2.Error, 'cursor' pode não existir no finally", strict=False)
def test_pesquisar_por_autor_excecao_ja_em_cursor_expoe_bug_de_cursor_nao_definido(monkeypatch):
    conn = mock()
    # self.conexao.cursor() já lança erro
    when(conn).cursor().thenRaise(psycopg2.Error("falhou cedo"))

    dao = sut.LivroDAO(conn)

    # O comportamento correto seria retornar None sem estourar outro erro;
    # este teste está como xfail até a correção do código de produção.
    resultado = dao.pesquisar_por_autor("Qualquer")
    assert resultado is None