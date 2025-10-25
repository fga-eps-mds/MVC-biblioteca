import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


class BibliotecaMVCHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        '''if self.path.startswith("/pesquisa"):
            query = parse_qs(urlparse(self.path).query)
            autor = query.get("autor", [""])[0]
            from controller.livro_controller import listar_livro
            html = listar_livro(autor)
            self.respond(html)
        elif self.path == '/' or self.path == '/index':
            self.render_template('index.html')
        else:
            self.send_error(404, 'Página não encontrada')'''
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path.startswith("/static/"):
            self.serve_static(path)
        elif path.startswith("/pesquisa"):
            query = parse_qs(parsed_path.query)
            autor = query.get("autor", [""])[0]
            from controller.livro_controller import listar_livro
            html = listar_livro(autor)
            self.respond(html)
        elif path == "/" or path == "/index":
            self.render_template("index.html")
        else:
            self.send_error(404, "Página não encontrada")

    def render_template(self, filename):
        try:
            with open(f'templates/{filename}', 'r', encoding='utf-8') as f:
                content = f.read()
            self.respond(content)
        except FileNotFoundError:
            self.send_error(404, 'Template não encontrado')

    def serve_static(self, path):
        file_path = path.lstrip("/")
        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            if file_path.endswith(".css"):
                self.send_header("Content-type", "text/css")
            elif file_path.endswith(".js"):
                self.send_header("Content-type", "application/javascript")
            elif file_path.endswith(".png"):
                self.send_header("Content-type", "image/png")
            elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
                self.send_header("Content-type", "image/jpeg")
            else:
                self.send_header("Content-type", "application/octet-stream")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "Arquivo estático não encontrado")

    def respond(self, content):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))


if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, BibliotecaMVCHandler)
    print('Servidor rodando em http://localhost:8080')
    httpd.serve_forever()





