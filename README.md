# Projeto MVC em Python 
Este projeto é uma implementação do padrão MVC (Model-View-Controller) usando Python, Flask e PostgreSQL. Ele foi desenvolvido para servir como exemplo didático para uma aplicação de pesquisa de livros já feita em [Java](https://replit.com/@engsoftmoderna/ExemploArquiteturaMVC#templates/index.html)

## Requisitos

- Python 3.11 ou superior
- Flask 3.0.3
- PostgreSQL
- Docker

## Como Rodar o Projeto

1. **Clone o repositório:**
   ```bash
   git clone <URL do repositório>
   ```

2. **Vá para a pasta do projeto:**
   ```bash
   cd MVC-biblioteca
   ```
  
3. **Rodar o Docker:** Certifique-se de que o Docker está instalado e em execução. Use o seguinte comando para iniciar os serviços definidos no docker-compose.yml:
   ```bash
    docker-compose up --build
   ```
4. **Acessar a aplicação:** Após iniciar os serviços, abra o navegador e acesse: http://localhost:5000

## Funcionamento
- O usuário acessa a página inicial, onde pode realizar pesquisas de livros.
- A pesquisa é processada pelo controlador, que interage com o modelo para buscar os dados no banco de dados.
- Os resultados são apresentados pela visão (HTML) ao usuário.
- Os livros disponíveis para pesquisa são limitados conforme o script de inicialização do banco de dados (init.sql).
  
Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para abrir um issue ou enviar um pull request.










