# Material traduzido e adaptado de:
# Marco Tulio Valente. Engenharia de Software Moderna: Princípios e Práticas para Desenvolvimento de Software com Produtividade,     Editora: Independente, 2020.
# UnB-FGA-EPS-MDS

from flask import Flask

# Cria a instância da aplicação Flask
app = Flask(__name__)

# Importe as rotas do seu controlador aqui
from app.controllers.controlador_pesquisa_livros import *

