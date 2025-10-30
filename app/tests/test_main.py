# app/tests/test_main.py
import io
import sys
import types
from pathlib import Path
import pytest

import main as app_main  # importa o módulo sob teste


# -----------------------------------------------------------------------------
# Helpers para montar um handler "fake" sem abrir socket/HTTP de verdade
# -----------------------------------------------------------------------------

def _make_handler(monkeypatch):
    """
    Cria uma instância "crua" de BibliotecaMVCHandler, sem rodar o __init__ da
    BaseHTTPRequestHandler. Patchamos métodos de envio de resposta/headers/erros
    para capturar o que seria enviado ao cliente.
    """
    captured = {"status": None, "headers": [], "error": None}

    def fake_send_response(self, code, message=None):
        captured["status"] = code

    def fake_send_header(self, key, value):
        captured["headers"].append((key, value))

    def fake_end_headers(self):
        # nada a fazer; só garante que não quebre
        pass

    def fake_send_error(self, code, message=None):
        captured["status"] = code
        captured["error"] = message

    # Aplica patches *no tipo* para afetar a instância criada abaixo
    monkeypatch.setattr(app_main.BibliotecaMVCHandler, "send_response", fake_send_response, raising=False)
    monkeypatch.setattr(app_main.BibliotecaMVCHandler, "send_header", fake_send_header, raising=False)
    monkeypatch.setattr(app_main.BibliotecaMVCHandler, "end_headers", fake_end_headers, raising=False)
    monkeypatch.setattr(app_main.BibliotecaMVCHandler, "send_error", fake_send_error, raising=False)

    # Cria instância "crua" e injeta atributos mínimos
    h = app_main.BibliotecaMVCHandler.__new__(app_main.BibliotecaMVCHandler)
    h.rfile = io.BytesIO()
    h.wfile = io.BytesIO()
    h.client_address = ("127.0.0.1", 0)
    h.server = None
    h.command = "GET"
    h.request_version = "HTTP/1.1"
    h.path = "/"

    return h, captured


# -----------------------------------------------------------------------------
# Testes do respond()
# -----------------------------------------------------------------------------

def test_respond_str_default_headers_status(monkeypatch):
    h, cap = _make_handler(monkeypatch)
    h.respond("hello")

    body = h.wfile.getvalue()
    assert cap["status"] == 200
    assert ("Content-Type", "text/html; charset=utf-8") in cap["headers"]
    assert body == b"hello"


def test_respond_tuple_status_html(monkeypatch):
    h, cap = _make_handler(monkeypatch)
    h.respond((404, "NF"))
    assert cap["status"] == 404
    assert h.wfile.getvalue() == b"NF"


def test_respond_tuple_html_status(monkeypatch):
    h, cap = _make_handler(monkeypatch)
    h.respond(("OK", 201))
    assert cap["status"] == 201
    assert h.wfile.getvalue() == b"OK"


# -----------------------------------------------------------------------------
# Testes do render_template() e _resolve_templates_dir()
# -----------------------------------------------------------------------------

def test_render_template_sucesso(monkeypatch, tmp_path, monkeypatch_context=None):
    # Cria um template temporário e força o uso via TEMPLATES_DIR
    templates = tmp_path / "tpl"
    templates.mkdir()
    (templates / "index.html").write_text("<h1>Index</h1>", encoding="utf-8")

    monkeypatch.setenv("TEMPLATES_DIR", str(templates))

    h, cap = _make_handler(monkeypatch)
    h.render_template("index.html")

