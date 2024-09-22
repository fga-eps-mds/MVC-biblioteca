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

## Explicação da Arquitetura MVC
O padrão MVC separa as responsabilidades da aplicação em três componentes principais:

1. Visão (View)
A Visão é responsável pela apresentação da interface gráfica ao usuário. Ela inclui elementos visuais como formulários, janelas, botões e menus. As classes de visão não possuem lógica de negócios, focando apenas em como os dados são exibidos.

Exemplo no código:

```html
<!-- templates/index.html -->
<form action="/pesquisa" method="get">
    <label for="autor">Nome do Autor:</label>
    <input type="text" id="autor" name="autor">
    <input type="submit" value="Pesquisar">
</form>
```
Neste exemplo, a página HTML exibe um formulário simples, onde o usuário pode pesquisar livros pelo nome do autor. A visão não realiza nenhum processamento de dados, ela apenas apresenta o formulário e recebe a entrada do usuário.

2. Controladoras (Controllers)
As Controladoras são responsáveis por tratar e interpretar eventos gerados por dispositivos de entrada (teclado, mouse, etc.). Elas capturam as ações do usuário, como cliques ou inserções de texto, e podem alterar o estado da Visão ou do Modelo, conforme necessário.

Exemplo no código:

```python
### app/controllers/controlador_pesquisa_livros.py
@app.route('/pesquisa', methods=['GET'])
def pesquisa():
    autor = request.args.get('autor')
    livro = servico.pesquisa_por_autor(autor)
    if livro:
        return pagina.exibe_livro(livro.titulo, livro.autor, livro.isbn)
    return "Livro não encontrado", 404
Aqui, o controlador recebe a requisição do usuário (pesquisa por autor), processa os dados com a ajuda do Modelo e, então, utiliza a Visão para exibir o resultado. Ele atua como intermediário entre o usuário e a lógica da aplicação.
```

3. Modelo (Model)
O Modelo gerencia os dados e a lógica de negócios da aplicação. Ele lida com a persistência dos dados e contém métodos para manipular esses dados. O Modelo não possui conhecimento da interface gráfica ou de como os dados serão exibidos.

Exemplo no código:

```python
# app/models/livro.py
class Livro:
    def __init__(self, titulo, autor, isbn):
        self.titulo = titulo
        self.autor = autor
        self.isbn = isbn
```
O Modelo define as entidades da aplicação (neste caso, o livro) e é responsável por manipular os dados de forma lógica. Ele é independente da interface do usuário e das controladoras.

Resumo do Fluxo de Funcionamento
O usuário interage com a Visão (HTML), por exemplo, preenchendo um formulário de pesquisa.
A Controladora captura essa ação, processa o pedido e, se necessário, interage com o Modelo para obter ou modificar dados.
O Modelo retorna os dados para a Controladora, que, então, usa a Visão para exibir o resultado ao usuário.

  
Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para abrir um issue ou enviar um pull request.










