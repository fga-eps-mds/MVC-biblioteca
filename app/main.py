from flask import Flask

# Cria a instância da aplicação Flask
app = Flask(__name__)

# Importe as rotas do seu controlador aqui
from app.controllers.controlador_pesquisa_livros import *

