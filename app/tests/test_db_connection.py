import pytest
from mockito import when, verify, mock
import psycopg2

import app.dao.db_connection as sut

def test_conectar_chama_psycopg2_com_parametros_corretos(monkeypatch):
    fake_conn = mock()
    # Stub do psycopg2.connect
    when(psycopg2).connect(
        dbname='mvc_biblioteca_db',
        user='postgres',
        password='Y2k_0!#4',
        host='localhost',
        port='5434'
    ).thenReturn(fake_conn)

    # Act
    conn = sut.conectar()

    # Assert
    assert conn is fake_conn
    verify(psycopg2).connect(
        dbname='mvc_biblioteca_db',
        user='postgres',
        password='Y2k_0!#4',
        host='localhost',
        port='5434'
    )


def test_conectar_lanca_excecao_em_falha(monkeypatch):
    # Simula erro de conexão
    when(psycopg2).connect(...).thenRaise(psycopg2.OperationalError("Falha na conexão"))

    with pytest.raises(psycopg2.OperationalError, match="Falha na conexão"):
        sut.conectar()