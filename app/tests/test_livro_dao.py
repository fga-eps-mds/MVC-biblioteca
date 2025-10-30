import pytest
from types import SimpleNamespace
from app.dao.livro_dao import LivroDAO
from app.model.livro import Livro


# =========================
# mocks de banco
# =========================
class DummyDBError(Exception):
    """Exceção-Stub para simular psycopg2.Error nos testes."""


class FakeCursor:
    def __init__(self, rows=None, raise_on=None):
        """
        rows: lista de tuplas (isbn, titulo, autor) a serem retornadas por fetchall()
        raise_on: None | "execute" | "fetchall" -> onde lançar DummyDBError
        """
        self.rows = rows or []
        self.raise_on = raise_on
        self.last_sql = None
        self.last_params = None

    # Suporte ao contexto: with conn.cursor() as cur:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        # não suprime exceções
        return False

    def execute(self, sql, params=None):
        self.last_sql = " ".join(sql.split())  # normaliza espaços
        self.last_params = params
        if self.raise_on == "execute":
            raise DummyDBError("boom in execute")

    def fetchall(self):
        if self.raise_on == "fetchall":
            raise DummyDBError("boom in fetchall")
        return list(self.rows)  # copia defensiva
class FakeConn:
    def __init__(self, cursor_obj: FakeCursor, closed=0):
        self._cursor_obj = cursor_obj
        self.closed = closed  # 0 = aberta; !=0 = fechada (simula psycopg2)

    def cursor(self):
        return self._cursor_obj


# =========================
# Fixtures de apoio
# =========================
@pytest.fixture
def livro_rows():
    return [
        ("9780000000001", "Algoritmos", "Autor X"),
        ("9780000000002", "Banco de Dados", "Autor X"),
    ]


@pytest.fixture
def fake_cursor(livro_rows):
    return FakeCursor(rows=livro_rows)


@pytest.fixture
def fake_conn(fake_cursor):
    return FakeConn(fake_cursor, closed=0)


@pytest.fixture
def conectar_spy(monkeypatch, fake_conn):
    """
    Monitora e stub-a a função 'conectar' **no módulo livro_dao**.
    Retorna um dict com contagem de chamadas e a conexão fake usado no stub.
    """
    import app.dao.livro_dao as mod

    calls = {"count": 0}

    def _stub_conectar():
        calls["count"] += 1
        return fake_conn

    # patcha a função 'conectar' usada dentro de livro_dao
    monkeypatch.setattr(mod, "conectar", _stub_conectar, raising=True)
    return calls


@pytest.fixture
def patch_psycopg2_error(monkeypatch):
    """
    Garante que o bloco except do LivroDAO pegue nossa DummyDBError mesmo
    que psycopg2 não esteja disponível durante o teste.
    """
    import app.dao.livro_dao as mod
    monkeypatch.setattr(mod, "psycopg2", SimpleNamespace(Error=DummyDBError), raising=True)


# =========================
# Testes de _conn()
# =========================
def test__conn_reusa_conexao_aberta(fake_conn, conectar_spy):
    dao = LivroDAO(conexao=fake_conn)  # conexão aberta (closed=0)
    obtida = dao._conn()
    assert obtida is fake_conn
    assert conectar_spy["count"] == 0  # não deve chamar conectar()


def test__conn_chama_conectar_quando_none(conectar_spy, fake_conn):
    dao = LivroDAO(conexao=None)
    obtida = dao._conn()
    assert obtida is fake_conn
    assert conectar_spy["count"] == 1  # deve chamar conectar()


def test__conn_chama_conectar_quando_fechada(conectar_spy, fake_cursor, fake_conn):
    # simula conexão já existente mas fechada
    antiga = FakeConn(fake_cursor, closed=1)
    dao = LivroDAO(conexao=antiga)
    obtida = dao._conn()
    # deve ter substituído pela conexão aberta do stub
    assert obtida is fake_conn
    assert conectar_spy["count"] == 1


def test__conn_sem_atributo_closed_tambem_reconecta(conectar_spy, fake_cursor, fake_conn):
    # conexão sem atributo 'closed' -> getattr(..., 'closed', 1) devolve 1 => reconecta
    class ConnSemClosed:
        def cursor(self):
            return fake_cursor

    dao = LivroDAO(conexao=ConnSemClosed())
    obtida = dao._conn()
    assert obtida is fake_conn
    assert conectar_spy["count"] == 1


# =========================
# Testes de pesquisar_por_autor()
# =========================
def test_pesquisar_por_autor_retorna_lista_de_Livro(fake_conn, fake_cursor):
    dao = LivroDAO(conexao=fake_conn)

    resultado = dao.pesquisar_por_autor("Autor X")

    # 1) valida retorno
    assert isinstance(resultado, list)
    assert len(resultado) == 2
    assert all(isinstance(l, Livro) for l in resultado)
    assert resultado[0].isbn == "9780000000001"
    assert resultado[0].titulo == "Algoritmos"
    assert resultado[0].autor == "Autor X"

    # 2) valida SQL e parâmetros
    assert "WHERE autor ILIKE %s" in fake_cursor.last_sql
    assert "ORDER BY titulo" in fake_cursor.last_sql
    assert fake_cursor.last_params == ("%Autor X%",)


def test_pesquisar_por_autor_sem_linhas_retorna_lista_vazia():
    cursor_vazio = FakeCursor(rows=[])
    conn_vazio = FakeConn(cursor_vazio, closed=0)
    dao = LivroDAO(conexao=conn_vazio)

    resultado = dao.pesquisar_por_autor("Ninguem")

    assert resultado == []
    # mesmo sem linhas, SQL e params devem ter sido passados
    assert "ILIKE %s" in cursor_vazio.last_sql
    assert cursor_vazio.last_params == ("%Ninguem%",)


def test_pesquisar_por_autor_trata_excecao_e_retorna_vazio(
    patch_psycopg2_error, fake_conn, capsys
):
    # faz o execute estourar um erro de banco
    fake_conn._cursor_obj.raise_on = "execute"
    dao = LivroDAO(conexao=fake_conn)

    resultado = dao.pesquisar_por_autor("Autor X")

    # retorna vazio e imprime mensagem de erro
    assert resultado == []
    out, err = capsys.readouterr()
    assert "Erro no banco de dados:" in out