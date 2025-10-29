import logging
import os
import psycopg2

def conectar():
    '''
    return psycopg2.connect(
        dbname='mvc_biblioteca_db',
        user='postgres',
        password='Y2k_0!#4',
        host='localhost',
        port='5434'
    )
    db_url = os.getenv("DATABASE_URL")
    return psycopg2.connect(db_url)'''


def conectar():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),          # <— serviço do Compose
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "mvc_biblioteca_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            options=f"-c search_path={os.getenv('DB_SEARCH_PATH', 'biblioteca,public')}"
        )
        return conn
    except Exception:
        logging.exception("Erro ao conectar ao Postgres (verifique variáveis DB_*).")
        raise
