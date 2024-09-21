from flask import Flask, render_template, request

# Inicializa a aplicação Flask
app = Flask(__name__)

# Importe seus serviços e views
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

# Se você estiver rodando o script diretamente, pode adicionar isso:
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
