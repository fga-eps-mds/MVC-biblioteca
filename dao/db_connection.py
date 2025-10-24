import psycopg2

def conectar():
    return psycopg2.connect(
        dbname='mvc_biblioteca_db',
        user='postgres',
        password='Y2k_0!#4',
        host='localhost',
        port='5432'
    )
