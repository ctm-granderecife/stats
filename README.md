<p align="center">
   <img src="https://raw.githubusercontent.com/ctm-granderecife/cdn-imgs/refs/heads/main/commons/logo_grande_recife.svg" alt="Logo do projeto" width="600">
</p>

# Estatísticas dos Repositórios do Grande Recife

## Sobre o Projeto

Este repositório contém um sistema automatizado para coletar e exibir estatísticas dos repositórios do Grande Recife. As estatísticas são atualizadas diariamente através de um workflow do GitHub Actions.

## Funcionalidades

- Coleta de dados dos repositórios via API do GitHub
- Exibição dos top usuários por número de commits
- Estatísticas detalhadas de cada repositório (linhas adicionadas, removidas, etc.)
- Top 5 commits de cada repositório

## Visualização

As estatísticas podem ser visualizadas através do [GitHub Pages](https://ctm-granderecife.github.io/stats/).

## Atualização

As estatísticas são atualizadas automaticamente todos os dias à meia-noite (UTC) ou quando há um push para a branch main.

## Como Funciona

O sistema utiliza a API do GitHub para coletar dados dos repositórios da organização Grande Recife. Os dados são processados e armazenados em um arquivo JSON, que é usado para gerar o HTML com as estatísticas.

## Tecnologias Utilizadas

- Python
- GitHub Actions
- API do GitHub
- HTML/CSS
- GitHub Pages

## Configuração

### Execução Local

Para executar o script localmente, siga os passos abaixo:

1. Clone o repositório
2. Instale as dependências: `pip install requests python-dotenv`
3. Crie um arquivo `.env` com seu token do GitHub:
   ```
   GITHUB_TOKEN=seu_token_aqui
   ```
   É necessário criar um token pessoal (PAT) com permissões para acessar os repositórios da organização.
   Você pode criar um token em: https://github.com/settings/tokens
4. Execute o script: `python update_stats.py`

### Configuração no GitHub Actions

Para que o workflow do GitHub Actions funcione corretamente, é necessário configurar um secret chamado `REPO_TOKEN` com um token pessoal do GitHub que tenha permissões para acessar os repositórios da organização.

Para configurar o secret:

1. Acesse as configurações do repositório no GitHub
2. Vá para a seção "Settings" > "Secrets and variables" > "Actions"
3. Clique em "New repository secret"
4. Nome: `REPO_TOKEN`
5. Valor: Cole seu token pessoal do GitHub
6. Clique em "Add secret"

Com isso, o workflow poderá acessar os dados dos repositórios da organização e atualizar as estatísticas automaticamente.

