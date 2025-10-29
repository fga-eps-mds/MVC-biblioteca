import psycopg2

def conectar():
    return psycopg2.connect(
        dbname='mvc_biblioteca_db',
        user='postgres',
        password='postgres',
        host='localhost',
        port='5432'
    )
