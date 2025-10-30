# app/tests/test_livro_controller.py
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
    """DAO fake que encontra livros por autor."""
    def __init__(self, conexao):
        self.conexao = conexao
        self.ultimo_autor = None
    def pesquisar_por_autor(self, autor):
        self.ultimo_autor = autor
        # O controller acessa [0].titulo/.autor/.isbn
        return [
            SimpleNamespace(titulo="Livro A", autor="Autor A", isbn="123-ABC"),
            SimpleNamespace(titulo="Livro B", autor="Autor A", isbn="456-DEF"),
        ]


class FakeLivroDAONotFound:
    """DAO fake sem resultados."""
    def __init__(self, conexao):
        self.conexao = conexao
    def pesquisar_por_autor(self, autor):
        return []


class FakeLivroDAOReturnsNone(FakeLivroDAONotFound):
    """Alguns DAOs podem retornar None quando não encontram resultados."""
    def pesquisar_por_autor(self, autor):
        return None


class FakePagina:
    """View fake usada pelo controller."""
    @staticmethod
    def exibe_livro(titulo, autor, isbn):
        return f"EXIBE::{titulo}|{autor}|{isbn}"


# ---------- Helper para montar o ambiente (patches) ----------

def _patch_ambiente(monkeypatch, dao_cls, conexoes_registradas):
    """Patches em conectar, LivroDAO e PaginaDadosLivro no módulo do controller."""
    def fake_conectar():
        conn = FakeConexao()
        conexoes_registradas.append(conn)
        return conn

    monkeypatch.setattr(lc, "conectar", fake_conectar, raising=True)
    monkeypatch.setattr(lc, "LivroDAO", dao_cls, raising=True)
    monkeypatch.setattr(lc, "PaginaDadosLivro", FakePagina, raising=True)


# ---------- Testes ----------

def test_listar_livro_quando_encontrado(monkeypatch):
    conexoes = []
    _patch_ambiente(monkeypatch, FakeLivroDAOFound, conexoes)

    saida = lc.listar_livro("Autor A")

    # Retorno da view fake com os campos do primeiro resultado
    assert saida == "EXIBE::Livro A|Autor A|123-ABC"
    # Conexão deve ser fechada no caminho de sucesso
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


def test_listar_livro_parametros_corretos_para_view(monkeypatch):
    conexoes = []
    _patch_ambiente(monkeypatch, FakeLivroDAOFound, conexoes)

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
    """Comportamento atual: se o DAO lança, a exceção é propagada (não é capturada)."""
    class FakeDAOErro:
        def __init__(self, conn): pass
        def pesquisar_por_autor(self, autor):
            raise RuntimeError("falha no DAO")

    conexoes = []
    _patch_ambiente(monkeypatch, FakeDAOErro, conexoes)

    with pytest.raises(RuntimeError):
        lc.listar_livro("Autor X")
    # Observação: sem try/finally no controller, a conexão pode não fechar em erro.
    # Se desejar garantir fechamento, alterar o controller para usar try/finally.
