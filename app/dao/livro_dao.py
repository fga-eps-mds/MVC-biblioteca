from app.dao.db_connection import conectar
from app.model.livro import Livro
import psycopg2

class LivroDAO:
    def __init__(self, conexao=None):
        self.conexao = conexao

    def _conn(self):
        if self.conexao is None or getattr(self.conexao, "closed", 1) != 0:
            self.conexao = conectar()
        return self.conexao

    def pesquisar_por_autor(self, autor: str):
        sql = """
            SELECT isbn, titulo, autor
              FROM biblioteca.livros
             WHERE autor ILIKE %s
             ORDER BY titulo
        """
        params = (f"%{autor}%",)
        try:
            conn = self._conn()
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
            return [Livro(isbn=r[0], titulo=r[1], autor=r[2]) for r in rows] if rows else []
        except psycopg2.Error as e:
            print(f"Erro no banco de dados: {e}")
            return []