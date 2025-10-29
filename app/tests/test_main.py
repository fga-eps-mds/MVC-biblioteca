# tests/test_http_handler.py
import io
import types
import sys
import pytest
from mockito import mock, when, verify, ANY

import main as sut


def make_handler():
    """
    Cria uma instância do handler sem acionar BaseHTTPRequestHandler.__init__.
    Injeta atributos e métodos necessários para os testes.
    """
    h = object.__new__(sut.BibliotecaMVCHandler)
    # Saída de resposta como stream em memória
    h.wfile = io.BytesIO()

    # Métodos que o código chama: por padrão, no-ops (substituídos nos testes quando necessário)
    h.send_response = lambda code: None
    h.send_header = lambda k, v=None: None
    h.end_headers = lambda: None
    h.send_error = lambda code, msg=None: None

    # Métodos da própria classe que podemos espiar/substituir
    # (serve_static, render_template, respond) serão substituídos conforme o teste
    return h


# -------------------------
# Testes para do_GET
# -------------------------

def test_do_get_static_chama_serve_static():
    h = make_handler()
    h.path = "/static/css/style.css"

    called = {}
    def fake_serve_static(path):
        called['path'] = path
    h.serve_static = fake_serve_static

    h.do_GET()

    assert called['path'] == "/static/css/style.css"


def test_do_get_pesquisa_importa_listar_livro_e_responde(monkeypatch):
    # Injeta módulo fake "controller.livro_controller" com listar_livro
    mod_name = "controller.livro_controller"
    fake_mod = types.ModuleType(mod_name)

    captured = {}
    def fake_listar_livro(autor):
        captured['autor'] = autor
        return f"<html>Autor: {autor}</html>"

    fake_mod.listar_livro = fake_listar_livro
    sys.modules[mod_name] = fake_mod  # injeta no sistema de import

    h = make_handler()
    h.path = "/pesquisa?autor=Ana%20Silva"

    # Vamos verificar que respond foi chamado com o HTML retornado
    resp_mock = mock()
    when(resp_mock).__call__(ANY).thenReturn(None)
    h.respond = resp_mock

    h.do_GET()

    # autor deve ter sido decodificado e passado corretamente
    assert captured['autor'] == "Ana Silva"
    verify(resp_mock).__call__("<html>Autor: Ana Silva</html>")


@pytest.mark.parametrize("path", ["/", "/index"])
def test_do_get_root_ou_index_renderiza_index_html(path):
    h = make_handler()
    h.path = path

    rend_mock = mock()
    when(rend_mock).__call__(ANY).thenReturn(None)
    h.render_template = rend_mock

    h.do_GET()

    verify(rend_mock).__call__("index.html")


def test_do_get_rota_desconhecida_retorna_404():
    h = make_handler()
    h.path = "/rota-que-nao-existe"

    err = mock()
    when(err).__call__(ANY, ANY).thenReturn(None)
    h.send_error = err

    h.do_GET()

    verify(err).__call__(404, "Página não encontrada")


# -------------------------
# Testes para render_template
# -------------------------

def test_render_template_sucesso_lendo_arquivo_e_respondendo(tmp_path, monkeypatch):
    # Prepara diretório de trabalho temporário com templates/index.html
    monkeypatch.chdir(tmp_path)
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "index.html").write_text("<h1>OK</h1>", encoding="utf-8")

    h = make_handler()

    resp_mock = mock()
    when(resp_mock).__call__(ANY).thenReturn(None)
    h.respond = resp_mock

    h.render_template("index.html")

    verify(resp_mock).__call__("<h1>OK</h1>")


def test_render_template_template_inexistente_retorna_404(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # sem criar arquivo

    h = make_handler()

    err = mock()
    when(err).__call__(ANY, ANY).thenReturn(None)
    h.send_error = err

    h.render_template("missing.html")

    verify(err).__call__(404, "Template não encontrado")


# -------------------------
# Testes para serve_static
# -------------------------

@pytest.mark.parametrize(
    "filename,content_type",
    [
        ("style.css", "text/css"),
        ("app.js", "application/javascript"),
        ("img.png", "image/png"),
        ("photo.jpg", "image/jpeg"),
        ("photo.jpeg", "image/jpeg"),
        ("file.bin", "application/octet-stream"),
    ],
)
def test_serve_static_retorna_200_com_tipo_correto_e_corpo(tmp_path, monkeypatch, filename, content_type):
    # Prepara um arquivo real em tmp_path/static/<filename>
    monkeypatch.chdir(tmp_path)
    (tmp_path / "static").mkdir()
    data = b"conteudo-binario"
    (tmp_path / "static" / filename).write_bytes(data)

    h = make_handler()

    # Mocks para cabeçalhos e status usando mockito (callables)
    sr = mock()
    sh = mock()
    eh = mock()
    when(sr).__call__(ANY).thenReturn(None)
    when(sh).__call__(ANY, ANY).thenReturn(None)
    when(eh).__call__().thenReturn(None)

    h.send_response = sr
    h.send_header = sh
    h.end_headers = eh

    # Executa
    h.serve_static(f"/static/{filename}")

    # Verifica status e cabeçalhos
    verify(sr).__call__(200)
    verify(sh).__call__("Content-type", content_type)
    verify(eh).__call__()

    # Verifica corpo
    h.wfile.seek(0)
    body = h.wfile.read()
    assert body == data


def test_serve_static_arquivo_inexistente_retorna_404(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    h = make_handler()

    err = mock()
    when(err).__call__(ANY, ANY).thenReturn(None)
    h.send_error = err

    h.serve_static("/static/nao-tem.css")

    verify(err).__call__(404, "Arquivo estático não encontrado")


# -------------------------
# Testes para respond
# -------------------------

def test_respond_envia_200_cabecalhos_e_corpo():
    h = make_handler()

    # Mocks de métodos de cabeçalho/estado
    sr = mock()
    sh = mock()
    eh = mock()
    when(sr).__call__(ANY).thenReturn(None)
    when(sh).__call__(ANY, ANY).thenReturn(None)
    when(eh).__call__().thenReturn(None)
    h.send_response = sr
    h.send_header = sh
    h.end_headers = eh

    # Act
    conteudo = "Olá, mundo!"
    h.respond(conteudo)

    # Assert chamadas de headers e status
    verify(sr).__call__(200)
    verify(sh).__call__('Content-type', 'text/html')
    verify(eh).__call__()

    # Assert corpo em bytes
    h.wfile.seek(0)
    assert h.wfile.read() == conteudo.encode("utf-8")
