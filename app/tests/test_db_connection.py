# app/tests/test_db_connection.py
import os
import pytest
import psycopg2
from mockito import when, verify, mock, unstub, any as ANY

import app.dao.db_connection as sut


@pytest.fixture(autouse=True)
def _cleanup():
    """Garante que os stubs do mockito não vazem entre testes."""
    yield
    unstub()


def test_conectar_usa_defaults_quando_env_nao_definido(monkeypatch):
    # Garante que não há variáveis de ambiente que influenciem
    for var in ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_SEARCH_PATH"]:
        monkeypatch.delenv(var, raising=False)

    fake_conn = mock()

    # O conectar() do sut inclui 'options' com search_path default
    when(psycopg2).connect(
        host="db",
        port="5432",
        dbname="mvc_biblioteca_db",
        user="postgres",
        password="postgres",
        options="-c search_path=biblioteca,public",
    ).thenReturn(fake_conn)

    # Act
    conn = sut.conectar()

    # Assert
    assert conn is fake_conn
    verify(psycopg2).connect(
        host="db",
        port="5432",
        dbname="mvc_biblioteca_db",
        user="postgres",
        password="postgres",
        options="-c search_path=biblioteca,public",
    )


def test_conectar_respeita_variaveis_de_ambiente(monkeypatch):
    # Define variáveis de ambiente personalizadas
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5434")
    monkeypatch.setenv("DB_NAME", "mvc_biblioteca_db")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "Y2k_0!#4")
    monkeypatch.setenv("DB_SEARCH_PATH", "biblioteca,public")  # ajuste se quiser outro search_path

    fake_conn = mock()

    when(psycopg2).connect(
        host="localhost",
        port="5434",
        dbname="mvc_biblioteca_db",
        user="postgres",
        password="Y2k_0!#4",
        options="-c search_path=biblioteca,public",
    ).thenReturn(fake_conn)

    conn = sut.conectar()

    assert conn is fake_conn
    verify(psycopg2).connect(
        host="localhost",
        port="5434",
        dbname="mvc_biblioteca_db",
        user="postgres",
        password="Y2k_0!#4",
        options="-c search_path=biblioteca,public",
    )

def test_conectar_lanca_excecao_em_falha(monkeypatch):
    # Não importa os valores, vamos fazer o connect levantar erro
    when(psycopg2).connect(...).thenRaise(psycopg2.OperationalError("Falha na conexão"))

    with pytest.raises(psycopg2.OperationalError, match="Falha na conexão"):
        sut.conectar()