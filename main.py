from http.server import BaseHTTPRequestHandler, HTTPServer

class MVCHandler(BaseHTTPRequestHandler):
    def do_get(self):
        if self.path == '/' or self.path == '/index':
            self.render_template('index.html')
        elif self.path == '/livros':
            from controller.livro_controller import listar_livros
            html = listar_livros()
            self.respond(html)
        else:
            self.send_error(404, 'Página não encontrada')

    def render_template(self, filename):
        try:
            with open(f'templates/{filename}', 'r', encoding='utf-8') as f:
                content = f.read()
            self.respond(content)
        except FileNotFoundError:
            self.send_error(404, 'Template não encontrado')

    def respond(self, content):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, MVCHandler)
    print('Servidor rodando em http://localhost:8080')
    httpd.serve_forever()
