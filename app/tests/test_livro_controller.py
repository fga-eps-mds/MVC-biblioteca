import pytest
from mockito import mock, when, verify, verifyZeroInteractions
import app.controller.livro_controller as sut
from types import SimpleNamespace


def test_listar_livro_encontrado(monkeypatch):
    # Mock da conexão
    conn = mock()
    when(conn).close().thenReturn(None)
    monkeypatch.setattr(sut, "conectar", lambda: conn)

    # Mock do DAO retornado pelo construtor LivroDAO(conn)
    dao = mock()
    livro = SimpleNamespace(titulo="Clean Code", autor="Robert C. Martin", isbn="9780132350884")
    when(dao).pesquisar_por_autor("Robert C. Martin").thenReturn([livro])

    # Substitui o símbolo LivroDAO no módulo por uma factory que devolve nosso mock
    def fake_livrodao(c):
        assert c is conn
        return dao
    monkeypatch.setattr(sut, "LivroDAO", fake_livrodao)

    # Mock da página/renderer
    pagina = mock()
    when(pagina).exibe_livro(livro.titulo, livro.autor, livro.isbn).thenReturn(("<html>OK</html>", 200))
    monkeypatch.setattr(sut, "PaginaDadosLivro", pagina)

    # --- Act ---
    resultado = sut.listar_livro("Robert C. Martin")

    # --- Assert ---
    assert resultado == ("<html>OK</html>", 200)
    verify(dao).pesquisar_por_autor("Robert C. Martin")
    verify(conn).close()
    verify(pagina).exibe_livro(livro.titulo, livro.autor, livro.isbn)


def test_listar_livro_nao_encontrado(monkeypatch):
    conn = mock()
    when(conn).close().thenReturn(None)
    monkeypatch.setattr(sut, "conectar", lambda: conn)

    dao = mock()
    when(dao).pesquisar_por_autor("Autor Desconhecido").thenReturn([])  # sem resultados
    monkeypatch.setattr(sut, "LivroDAO", lambda c: dao)

    # mock para garantir que exibe_livro NÃO é chamado
    pagina = mock()
    monkeypatch.setattr(sut, "PaginaDadosLivro", pagina)

    # --- Act ---
    resultado = sut.listar_livro("Autor Desconhecido")

    # --- Assert ---
    assert resultado == ("Livro não encontrado", 404)
    verify(dao).pesquisar_por_autor("Autor Desconhecido")
    verify(conn).close()
    # Garante que não houve chamadas na página
    verifyZeroInteractions(pagina)


def test_listar_livro_erro_no_dao_propagado_e_conexao_nao_fechada(monkeypatch):
    """
    Este teste evidencia o comportamento atual: se o DAO lança exceção,
    a conexão NÃO é fechada (pois o close ocorre depois da chamada).
    Isso é útil para motivar um ajuste com try/finally no código de produção.
    """
    conn = mock()
    when(conn).close().thenReturn(None)
    monkeypatch.setattr(sut, "conectar", lambda: conn)

    dao = mock()
    when(dao).pesquisar_por_autor("Falha").thenRaise(RuntimeError("Erro no banco"))
    monkeypatch.setattr(sut, "LivroDAO", lambda c: dao)

    pagina = mock()
    monkeypatch.setattr(sut, "PaginaDadosLivro", pagina)

    # --- Act & Assert ---
    with pytest.raises(RuntimeError, match="Erro no banco"):
        sut.listar_livro("Falha")

    # Confirma que close NÃO foi chamado (comportamento atual)
    verify(conn, times=0).close()
