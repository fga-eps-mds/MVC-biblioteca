# tests/test_livro_model.py
from dataclasses import is_dataclass

# >>> AJUSTE O IMPORT PARA O LOCAL DO MODELO <<<
import app.model.livro as sut


def test_livro_inicializa_campos_corretamente():
    livro = sut.Livro(isbn="123", autor="Autor", titulo="Título")
    assert livro.isbn == "123"
    assert livro.autor == "Autor"
    assert livro.titulo == "Título"


def test_livro_permite_keywords_em_ordem_diferente():
    livro = sut.Livro(titulo="Título", autor="Autor", isbn="123")
    assert (livro.isbn, livro.autor, livro.titulo) == ("123", "Autor", "Título")