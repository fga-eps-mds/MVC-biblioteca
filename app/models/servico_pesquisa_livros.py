# Material traduzido e adaptado de:
# Marco Tulio Valente. Engenharia de Software Moderna: Princípios e Práticas para Desenvolvimento de Software com Produtividade,     Editora: Independente, 2020.
# UnB-FGA-EPS-MDS

import psycopg2
from app.models.livro import Livro

class ServicoPesquisaLivros:
    def pesquisa_por_autor(self, autor):
        try:
            con = psycopg2.connect(
                dbname="bib_db",
                user="postgres",
                password="postgres",
                host="db",  # nome do serviço no Docker Compose
                port="5432"
            )
            cursor = con.cursor()
            cursor.execute("SELECT * FROM livros WHERE autor = %s", (autor,))
            row = cursor.fetchone()
            if row:
                isbn, autor, titulo = row
                return Livro(isbn, autor, titulo)
            return None
        except psycopg2.Error as e:
            print(f"Erro no banco de dados: {e}")
            return None
        finally:
            if con:
                cursor.close()
                con.close()
