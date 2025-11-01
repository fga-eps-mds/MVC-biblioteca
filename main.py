"""
Servidor HTTP mínimo para o projeto mvc-biblioteca.

Este módulo expõe um manipulador (handler) baseado em BaseHTTPRequestHandler
que oferece:
- Renderização simples de templates HTML a partir de um diretório configurável;
- Roteamento básico para páginas e busca de livros (controller);
- Servir arquivos estáticos de maneira segura (evitando path traversal);
- Um utilitário `respond()` para padronizar respostas HTTP.

⚠️ Observação: este servidor é adequado para desenvolvimento/ensino.
"""

import mimetypes
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Raiz dos arquivos estáticos (ex.: CSS, JS, imagens). Mantida fora da pasta
# de templates para separação de responsabilidades.
STATIC_ROOT = Path(__file__).resolve().parent / "app" / "static"


class BibliotecaMVCHandler(BaseHTTPRequestHandler):
    """Manipulador de requisições HTTP do mvc-biblioteca.

    A classe herda de BaseHTTPRequestHandler e implementa métodos auxiliares
    para:
    - Resolver o diretório de templates com fallback para variáveis de ambiente;
    - Renderizar um template HTML e devolvê-lo ao cliente;
    - Roteamento básico por caminho em `do_GET`;
    - Servir arquivos estáticos com detecção de MIME;
    - Padronizar o envio de respostas via `respond`.
    """

    # ---------------------------------------------------------------------
    # Templates
    # ---------------------------------------------------------------------
    def resolve_templates_dir(self) -> Path:
        """Resolve o diretório de templates com múltiplos fallbacks.

        Ordem de resolução:
        1) Variável de ambiente `TEMPLATES_DIR` (útil em testes e containers);
        2) Caminho '/app/app/templates' (compatível com layout em Docker);
        3) Pasta local 'templates' ao lado deste arquivo.
        """
        env_dir = os.getenv('TEMPLATES_DIR')
        if env_dir:
            return Path(env_dir).resolve()

        # Fallback para um caminho usado frequentemente em imagens Docker
        cand = Path('/app/app/templates')
        if cand.exists():
            return cand.resolve()

        # Por fim, usa a pasta local de templates
        base = Path(__file__).resolve().parent
        return (base / 'templates').resolve()

    def render_template(self, filename: str) -> None:
        """Renderiza um arquivo HTML de `templates` e envia ao cliente.

        - Garante que apenas o *nome* do arquivo seja utilizado (mitiga
          tentativas de path traversal fornecendo um caminho absoluto);
        - Define `Content-Type` adequado para HTML com charset UTF-8;
        - Em caso de ausência do arquivo, responde com 404.
        """
        try:
            templates_dir = self.resolve_templates_dir()
            # Usa somente o nome do arquivo para evitar que subcaminhos escapem
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

    # ---------------------------------------------------------------------
    # Roteamento
    # ---------------------------------------------------------------------
    def do_GET(self) -> None:
        """Roteamento simples para requisições GET.

        Rotas suportadas:
        - `/static/*`: arquivos estáticos;
        - `/pesquisa?autor=...`: lista livros pelo autor (controller);
        - `/` ou `/index`: página inicial via template `index.html`.
        Outros caminhos retornam 404.
        """
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path.startswith('/static/'):
            self.serve_static(path)
            return

        if path.startswith('/pesquisa'):
            # Extrai o parâmetro `autor` (padrão vazio se ausente)
            query = parse_qs(parsed_path.query)
            autor = query.get('autor', [''])[0]

            # Import tardio para manter dependências locais ao ponto de uso
            from app.controller.livro_controller import listar_livro  # type: ignore

            html = listar_livro(autor)
            self.respond(html)
            return

        if path in ('/', '/index'):
            self.render_template('index.html')
            return

        self.send_error(404, 'Página não encontrada')

    # ---------------------------------------------------------------------
    # Arquivos estáticos
    # ---------------------------------------------------------------------
    def serve_static(self, path: str) -> None:
        """Serve arquivos estáticos de forma segura.

        - Remove o prefixo `/static/` e resolve o caminho relativo dentro de
          `STATIC_ROOT`;
        - Garante que o caminho final esteja *dentro* de `STATIC_ROOT` para
          evitar *path traversal* (ex.: `../../etc/passwd`);
        - Detecta o MIME via `mimetypes.guess_type` e faz o streaming do arquivo.
        """
        # Remove o prefixo '/static/' e resolve o caminho relativo
        rel = path[len('/static/'):] if path.startswith('/static/') else path
        wanted = (STATIC_ROOT / rel).resolve()
        root = STATIC_ROOT.resolve()

        # Evita fuga do diretório estático e serve o arquivo
        if wanted.is_file() and str(wanted).startswith(str(root)):
            self.send_response(200)
            mime, _ = mimetypes.guess_type(str(wanted))
            self.send_header('Content-Type', mime or 'application/octet-stream')
            self.end_headers()
            self.wfile.write(wanted.read_bytes())
            return

        self.send_error(404, 'Arquivo estático não encontrado')

    # ---------------------------------------------------------------------
    # Utilitário de resposta
    # ---------------------------------------------------------------------
    def respond(
        self,
        content: str | bytes | tuple[str, int] | tuple[int, str],
        status: int = 200,
        content_type: str = 'text/html; charset=utf-8',
    ) -> None:
        """Envia uma resposta HTTP padronizada.

        Parâmetros
        -----------
        content:
            Pode ser:
            - `str`  → corpo em texto; status padrão 200 e Content-Type HTML;
            - `bytes` → corpo binário (já codificado);
            - `(html:str, status:int)` ou `(status:int, html:str)` → tupla
              com status e corpo (ordem flexível para ergonomia).
        status:
            Código HTTP quando `content` não for tupla.
        content_type:
            Cabeçalho `Content-Type` enviado quando o corpo é texto.
        """
        # Concilia assinaturas flexíveis via tupla (html, status) ou (status, html)
        if isinstance(content, tuple):
            if len(content) == 2:
                a, b = content
                if isinstance(a, int):
                    status, content = a, b  # (status, html)
                else:
                    content, status = a, b  # (html, status)
            else:
                # Fallback defensivo: usa o primeiro elemento como corpo
                content = content[0]

        # Garante bytes para escrita no `wfile`
        if isinstance(content, str):
            content = content.encode('utf-8')

        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(content)


if __name__ == '__main__':
    # Configuração do endereço/porta do servidor. Em contêineres, 0.0.0.0
    # permite aceitar conexões externas. Em ambiente local, use 127.0.0.1.
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, BibliotecaMVCHandler)
    print('Servidor rodando em http://localhost:8080')
    httpd.serve_forever()
