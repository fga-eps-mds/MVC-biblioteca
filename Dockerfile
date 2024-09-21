# Dockerfile

FROM python:3.9-slim

# Instalar dependências
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Definir a variável de ambiente para ativar o modo de depuração
ENV FLASK_ENV=development
ENV FLASK_APP=app.controllers.controlador_pesquisa_livros  

# Comando para rodar o Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

RUN chmod -R 755 /app  
