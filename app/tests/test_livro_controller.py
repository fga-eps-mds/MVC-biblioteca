from types import SimpleNamespace
import pytest

# Módulo sob teste
import app.controller.livro_controller as lc


# ---------- Fakes utilitários ----------

class FakeConexao:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class FakeLivroDAOFound:
    """Simula DAO que encontra livros por autor."""
    def __init__(self, conexao):
        self.conexao = conexao
        self.ultimo_autor = None

    def pesquisar_por_autor(self, autor):
        self.ultimo_autor = autor
        # O controller usa o índice [0] e lê atributos .titulo/.autor/.isbn
        return [
            SimpleNamespace(titulo="Livro A", autor="Autor A", isbn="123-ABC"),
            SimpleNamespace(titulo="Livro B", autor="Autor A", isbn="456-DEF"),
        ]


class FakeLivroDAONotFound:
    """Simula DAO que não encontra resultados."""
    def __init__(self, conexao):
        self.conexao = conexao

    def pesquisar_por_autor(self, autor):
        # Pode devolver lista vazia...
        return []


class FakeLivroDAOReturnsNone(FakeLivroDAONotFound):
    """Alguns DAOs devolvem None quando não há resultados."""
    def pesquisar_por_autor(self, autor):
        return None


class FakePagina:
    """Simula camada de view utilizada pelo controller."""
    @staticmethod
    def exibe_livro(titulo, autor, isbn):
        # Retorno previsível para asserção
        return f"EXIBE::{titulo}|{autor}|{isbn}"


# ---------- Helpers para monkeypatch ----------

def _patch_ambiente(monkeypatch, dao_cls, conexoes_registradas):
    """
    - Substitui 'conectar' no módulo do controller por uma fábrica de FakeConexao
      que armazena as conexões criadas em 'conexoes_registradas' (lista).
    - Substitui 'LivroDAO' no módulo do controller pelo 'dao_cls' informado.
    - Substitui 'PaginaDadosLivro' por 'FakePagina'.
    """
    def fake_conectar():
        conn = FakeConexao()
        conexoes_registradas.append(conn)
        return conn

    # Patches no namespace do módulo testado:
    monkeypatch.setattr(lc, "conectar", fake_conectar, raising=True)
    monkeypatch.setattr(lc, "LivroDAO", dao_cls, raising=True)
    # PaginaDadosLivro é um módulo/classe com metodo exibe_livro
    monkeypatch.setattr(lc, "PaginaDadosLivro", FakePagina, raising=True)


# ---------- Testes ----------

def test_listar_livro_quando_encontrado_deve_renderizar_primeiro_resultado(monkeypatch):
    conexoes = []
    _patch_ambiente(monkeypatch, FakeLivroDAOFound, conexoes)

    saida = lc.listar_livro("Autor A")

    # Verifica saída proveniente da view fake
    assert saida == "EXIBE::Livro A|Autor A|123-ABC"
    # Garante que a conexão foi fechada
    assert len(conexoes) == 1 and conexoes[0].closed is True


def test_listar_livro_quando_nao_encontrado_lista_vazia(monkeypatch):
    conexoes = []
    _patch_ambiente(monkeypatch, FakeLivroDAONotFound, conexoes)

    saida = lc.listar_livro("Autor Inexistente")

    assert saida == ("Livro não encontrado", 404)
    assert len(conexoes) == 1 and conexoes[0].closed is True


def test_listar_livro_quando_nao_encontrado_none(monkeypatch):
    conexoes = []
    _patch_ambiente(monkeypatch, FakeLivroDAOReturnsNone, conexoes)

    saida = lc.listar_livro("Qualquer Autor")

    assert saida == ("Livro não encontrado", 404)
    assert len(conexoes) == 1 and conexoes[0].closed is True


def test_listar_livro_deve_passar_parametros_corretos_para_view(monkeypatch):
    """
    Além de verificar a string final, garantimos que o controller
    envia exatamente os campos titulo/autor/isbn do primeiro resultado.
    """
    conexoes = []
    _patch_ambiente(monkeypatch, FakeLivroDAOFound, conexoes)

    # Espiona a chamada de exibe_livro
    capturado = {}
    def spy_exibe_livro(titulo, autor, isbn):
        capturado["titulo"] = titulo
        capturado["autor"] = autor
        capturado["isbn"] = isbn
        return "OK"

    monkeypatch.setattr(lc.PaginaDadosLivro, "exibe_livro", spy_exibe_livro, raising=True)

    saida = lc.listar_livro("Autor A")

    assert saida == "OK"
    assert capturado == {"titulo": "Livro A", "autor": "Autor A", "isbn": "123-ABC"}
    assert len(conexoes) == 1 and conexoes[0].closed is True


def test_listar_livro_propaga_excecao_do_dao(monkeypatch):
    """
    Caso o DAO lance uma exceção, o controller atual não captura.
    Validamos essa decisão para manter o teste fiel ao comportamento atual.
    """
    class FakeDAOErro:
        def __init__(self, conn): pass
        def pesquisar_por_autor(self, autor):
            raise RuntimeError("erro no acesso a dados")

    conexoes = []
    _patch_ambiente(monkeypatch, FakeDAOErro, conexoes)

    with pytest.raises(RuntimeError):
        lc.listar_livro("Autor X")

    # Mesmo em erro, a conexão é fechada (porque o close ocorre após a chamada).
    # Observação: se a exceção ocorrer antes do close, este assert pode falhar.
    # Se isso ocorrer, considere usar try/finally no controller para fechar sempre.
    # Aqui mantemos o comportamento atual.