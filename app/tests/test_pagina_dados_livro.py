# tests/test_pagina_dados_livro.py
import re

import app.view.pagina_dados_livro as sut


def compacta_ws(s: str) -> str:
    """
    Auxiliar para tornar asserções mais robustas a respeito de espaços/indentação.
    Converte qualquer sequência de whitespace em um único espaço e faz strip nas pontas.
    """
    return re.sub(r"\s+", " ", s).strip()


def test_exibe_livro_renderiza_campos_basicos():
    html = sut.PaginaDadosLivro.exibe_livro(
        titulo="Clean Code",
        autor="Robert C. Martin",
        isbn="9780132350884"
    )

    # Asserções diretas por substrings (independem de indentação)
    assert "Dados do Livro Pesquisado" in html
    assert "Título: Clean Code" in html
    assert "Autor: Robert C. Martin" in html
    assert "ISBN: 9780132350884" in html

    # Garante que usa tags HTML escapadas (&lt; ... &gt;)
    assert "&lt;meta charset=\"UTF-8\"&gt;" in html
    assert "&lt;link rel=\"stylesheet\" href=\"/static/css/style.css\"&gt;" in html
    assert "&lt;h1&gt;" in html and "&lt;/h1&gt;" in html
    assert "&lt;ul&gt;" in html and "&lt;/ul&gt;" in html
    assert "&lt;li&gt;" in html and "&lt;/li&gt;" in html


def test_exibe_livro_layout_minimo_com_whitespace_variavel():
    html = sut.PaginaDadosLivro.exibe_livro("A", "B", "C")
    # Normalizamos espaços para evitar fragilidade com identação da f-string
    html_norm = compacta_ws(html)

    # Verificações mais "estruturais"
    assert '&lt;meta charset="UTF-8"&gt;' in html_norm
    assert 'href="/static/css/style.css"' in html_norm
    assert "&lt;h1&gt; Dados do Livro Pesquisado &lt;/h1&gt;" in html_norm

    # Lista com três itens esperados
    assert "Título: A" in html_norm
    assert "Autor: B" in html_norm
    assert "ISBN: C" in html_norm


def test_exibe_livro_suporta_caracteres_especiais_e_html_no_conteudo():
    titulo = 'Algoritmos & Estruturas <Dados> "Avançado"'
    autor = "José da Silva & Filhos <Org.>"
    isbn = "ISBN-13: 978-85-7522-000-0"

    html = sut.PaginaDadosLivro.exibe_livro(titulo, autor, isbn)
    html_norm = compacta_ws(html)

    # Os valores fornecidos são inseridos literalmente no corpo de texto (o template usa &lt;...&gt;)
    # Assim, garantimos que os caracteres apareçam como fornecidos.
    assert f"Título: {titulo}" in html_norm
    assert f"Autor: {autor}" in html_norm
    assert f"ISBN: {isbn}" in html_norm


def test_exibe_livro_e_staticmethod():
    # Garante que é um metodo estático (pode ser chamado sem instância)
    assert isinstance(sut.PaginaDadosLivro.__dict__["exibe_livro"], staticmethod)

    # E que a chamada sem instância funciona
    out = sut.PaginaDadosLivro.exibe_livro("T", "A", "I")
    assert isinstance(out, str) and "Título: T" in out