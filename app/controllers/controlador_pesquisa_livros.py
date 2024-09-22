# Material traduzido e adaptado de:
# Marco Tulio Valente. Engenharia de Software Moderna: Princípios e Práticas para Desenvolvimento de Software com Produtividade,     Editora: Independente, 2020.
# UnB-FGA-EPS-MDS

from flask import render_template, request
from app.main import app  # Importa a instância do Flask
from app.models.servico_pesquisa_livros import ServicoPesquisaLivros
from app.views.pagina_dados_livro import PaginaDadosLivro

# Inicializa os serviços
servico = ServicoPesquisaLivros()
pagina = PaginaDadosLivro()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/pesquisa', methods=['GET'])
def pesquisa():
    autor = request.args.get('autor')
    livro = servico.pesquisa_por_autor(autor)
    if livro:
        return pagina.exibe_livro(livro.titulo, livro.autor, livro.isbn)
    return "Livro não encontrado", 404
