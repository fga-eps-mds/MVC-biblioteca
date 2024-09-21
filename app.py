from flask import Flask
from app.controllers.controlador_pesquisa_livros import controlador

app = Flask(__name__)
app.register_blueprint(controlador)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
