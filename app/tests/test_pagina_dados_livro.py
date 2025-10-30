# app/tests/test_pagina_dados_livro.py
import pytest
from app.view.pagina_dados_livro import PaginaDadosLivro


def _normalize(html: str) -> str:
    """
    Normaliza HTML para comparações robustas:
    - remove todos os espaços em branco (espaços, quebras de linha, tabs),
      para não depender de indentação/quebras.
    """
    return "".join(html.split())


def test_exibe_livro_estrutura_basica_html():
    saida = PaginaDadosLivro.exibe_livro("Livro A", "Autor A", "123-ABC")

    # Tags de estrutura principais
    assert "<meta" in saida.lower() and "charset" in saida.lower()
    assert '<link' in saida.lower() and 'rel="stylesheet"' in saida.lower()
    assert "<h1>" in saida and "</h1>" in saida
    assert "<ul>" in saida and "</ul>" in saida

    # Conteúdo do título (H1)
    assert "Dados do Livro Pesquisado" in saida

    # Itens da lista
    norm = _normalize(saida)
    assert _normalize("<li>Título: Livro A</li>") in norm
    assert _normalize("<li>Autor: Autor A</li>") in norm
    assert _normalize("<li>ISBN: 123-ABC</li>") in norm


def test_exibe_livro_ordem_dos_itens():
    saida = PaginaDadosLivro.exibe_livro("L", "A", "I")
    norm = _normalize(saida)

    li_titulo = _normalize("<li>Título: L</li>")
    li_autor = _normalize("<li>Autor: A</li>")
    li_isbn = _normalize("<li>ISBN: I</li>")

    pos_titulo = norm.find(li_titulo)
    pos_autor  = norm.find(li_autor)
    pos_isbn   = norm.find(li_isbn)

    # Todos devem existir
    assert pos_titulo != -1 and pos_autor != -1 and pos_isbn != -1
    # Ordem: Título -> Autor -> ISBN
    assert pos_titulo < pos_autor < pos_isbn


def test_exibe_livro_meta_charset_utf8():
    saida = PaginaDadosLivro.exibe_livro("X", "Y", "Z")
    low = saida.lower()
    # Tolerante a aspas simples/duplas
    assert "meta" in low and "charset" in low and "utf-8" in low


def test_exibe_livro_link_stylesheet_presente():
    saida = PaginaDadosLivro.exibe_livro("X", "Y", "Z")
    # Caminho do CSS declarado na view
    assert "/static/css/style.css" in saida


def test_exibe_livro_preserva_caracteres_especiais():
    saida = PaginaDadosLivro.exibe_livro(
        titulo="*Negrito*",
        autor="_Itálico_",
        isbn="`inline-code`",
    )
    # O HTML não escapa esses caracteres (eles aparecem como texto dentro do <li>)
    assert "*Negrito*" in saida
    assert "_Itálico_" in saida
    assert "`inline-code`" in saida


@pytest.mark.parametrize(
    "titulo,autor,isbn",
    [
        (123, 456, 789),          # inteiros
        (None, "Autor", "X"),     # None
        ("Título", None, "X"),
        ("Título", "Autor", None),
    ],
)
def test_exibe_livro_converte_argumentos_para_string(titulo, autor, isbn):
    saida = PaginaDadosLivro.exibe_livro(titulo, autor, isbn)
    norm = _normalize(saida)

    # f-string converte para str(...) implicitamente
    assert _normalize(f"<li>Título: {str(titulo)}</li>") in norm
    assert _normalize(f"<li>Autor: {str(autor)}</li>") in norm
    assert _normalize(f"<li>ISBN: {str(isbn)}</li>") in norm