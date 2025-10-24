import psycopg2
from model.livro import Livro

class LivroDAO:
    def __init__(self, conexao):
        self.conexao = conexao

    def pesquisar_por_autor(self, autor):
        global cursor
        try:
            cursor = self.conexao.cursor()
            cursor.execute("SELECT isbn, autor, titulo FROM livros WHERE LOWER(autor) LIKE %s", (f"%{autor.lower()}%",))
            rows = cursor.fetchall()

            if rows:
                isbn, autor, titulo = rows
                #return [Livro(id=row[0], titulo=row[1], autor=row[2]) for row in rows]
                return Livro(isbn, autor, titulo)
            return None
        except psycopg2.Error as e:
            print(f"Erro no banco de dados: {e}")
            return None
        finally:
            if self.conexao:
                cursor.close()