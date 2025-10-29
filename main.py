import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from pathlib import Path
import mimetypes

STATIC_ROOT = Path(__file__).resolve().parent / "app" / "static"

class BibliotecaMVCHandler(BaseHTTPRequestHandler):

    def _resolve_templates_dir(self) -> Path:
        env_dir = os.getenv('TEMPLATES_DIR')
        if env_dir:
            return Path(env_dir).resolve()
        cand = Path('/app/app/templates')
        if cand.exists():
            return cand.resolve()
        base = Path(__file__).resolve().parent
        return (base / 'templates').resolve()

    def render_template(self, filename: str):
        try:
            templates_dir = self._resolve_templates_dir()
            safe_name = Path(filename).name
            path = (templates_dir / safe_name).resolve()
            if not path.is_file():
                raise FileNotFoundError(path)
            content = path.read_text(encoding='utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, 'Template não encontrado')

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        if path.startswith('/static/'):
            self.serve_static(path)
        elif path.startswith('/pesquisa'):
            query = parse_qs(parsed_path.query)
            autor = query.get('autor', [''])[0]
            from app.controller.livro_controller import listar_livro
            html = listar_livro(autor)
            self.respond(html)
        elif path == '/' or path == '/index':
            self.render_template('index.html')
        else:
            self.send_error(404, 'Página não encontrada')

    def serve_static(self, path):

        # Remove o prefixo '/static/' e resolve o caminho relativo
        rel = path[len('/static/'):] if path.startswith('/static/') else path
        wanted = (STATIC_ROOT / rel).resolve()
        root = STATIC_ROOT.resolve()

        # (opcional) log didático para ver o caminho mapeado
        print(f"[STATIC] req={path} -> {wanted}")

        # Evita path traversal e serve o arquivo
        if wanted.is_file() and str(wanted).startswith(str(root)):
            self.send_response(200)
            mime, _ = mimetypes.guess_type(str(wanted))
            self.send_header('Content-Type', mime or 'application/octet-stream')
            self.end_headers()
            self.wfile.write(wanted.read_bytes())
        else:
            self.send_error(404, 'Arquivo estático não encontrado')

    def respond(self, content, status: int = 200, content_type: str = 'text/html; charset=utf-8'):

        if isinstance(content, tuple):
            if len(content) == 2:
                a, b = content
                if isinstance(a, int):
                    status, content = a, b  # (status, html)
                else:
                    content, status = a, b  # (html, status)
            else:
                # fallback: usa o primeiro elemento como corpo
                content = content[0]

        # Garante bytes
        if isinstance(content, str):
            content = content.encode('utf-8')

        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(content)


if __name__ == '__main__':
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, BibliotecaMVCHandler)
    print('Servidor rodando em http://localhost:8080')
    httpd.serve_forever()
