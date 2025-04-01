import os
import requests
from dotenv import load_dotenv
from collections import Counter
from datetime import datetime, timedelta

# Carregar variáveis do .env
load_dotenv()

# Token do GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAME = "ctm-granderecife"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

REPOS_BLACKLIST = [
    'site-granderecife',
    'whaticket-gr',
    '.github',
    'demo-repository',
    'cdn-imgs',
    'dados-saida-peregrinno',
    'stats'
]

# Função para pegar os repositórios da organização
def get_repos():
    repos_url = f"https://api.github.com/orgs/{ORG_NAME}/repos?page=1&per_page=20&sort=updated&direction=desc"
    response = requests.get(repos_url, headers=HEADERS)
    response.raise_for_status()
    return [repo['name'] for repo in response.json()]

# Função para pegar commits de um repositório
def get_commits(repo):
    commits_url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/commits?per_page=5"  # Limitar aos 5 commits mais recentes
    response = requests.get(commits_url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

# Função para pegar as estatísticas de um commit
def get_commit_stats(repo, sha):
    commit_url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/commits/{sha}"
    response = requests.get(commit_url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

# Função para gerar o conteúdo do README
def update_readme():
    repos = get_repos()
    
    # Contadores para ranking e estatísticas
    commit_authors = Counter()
    repo_data = {}

    # Pega os commits e as estatísticas
    for repo in repos:
        if repo not in REPOS_BLACKLIST:
            commits = get_commits(repo)
            
            if commits:
                # Armazena as estatísticas de commits por repositório
                total_additions = 0
                total_deletions = 0
                total_lines = 0
                repo_commit_data = []
                for commit in commits:
                    sha = commit['sha']
                    author = commit['commit']['author']['name']
                    date = commit['commit']['author']['date']
                    stats = get_commit_stats(repo, sha)['stats']
                    additions = stats['additions']
                    deletions = stats['deletions']
                    total_lines += stats['total']
                    
                    # Coleta os dados
                    commit_authors[author] += 1
                    repo_commit_data.append({
                        'sha': sha[:7],  # Primeiros 7 caracteres do SHA
                        'author': author,
                        'date': date,
                        'additions': additions,
                        'deletions': deletions,
                        'total_lines': stats['total']
                    })
                    total_additions += additions
                    total_deletions += deletions

                # Adiciona os dados do repositório no dicionário
                repo_data[repo] = {
                    'commits': repo_commit_data,
                    'total_additions': total_additions,
                    'total_deletions': total_deletions,
                    'total_lines': total_lines
                }
        
    # Ordena o ranking dos usuários
    top_10_users = commit_authors.most_common(10)
    
    # Atualiza o README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(f'<p align="center">\n')
        f.write(f'   <img src="https://raw.githubusercontent.com/ctm-granderecife/cdn-imgs/refs/heads/main/commons/logo_grande_recife.svg" alt="Logo do projeto" width="600">\n')
        f.write(f'</p>\n')
        
        
        f.write("# Dados estatisticos de Desenvolvimento do Grande Recife \n")

        # Informações dos commits
        f.write(f"\n## Top 10 Usuários da Última Semana\n")
        for user, commits in top_10_users:
            f.write(f"{user}: {commits} commits\n")
        
        f.write(f"\n## Repositórios e Top 5 Commits\n")
        
        for repo, data in repo_data.items():
            f.write(f"### **{repo}**\n")
            f.write(f"  - **Total de Linhas Alteradas**: {data['total_lines']} (Adições: {data['total_additions']} | Deleções: {data['total_deletions']})\n")
            f.write(f"  - **Top 5 Commits**:\n")
            
            # Tabela de commits
            f.write(f"| SHA       | Autor        | Data                | Adições | Deleções | Total de Linhas |\n")
            f.write(f"|-----------|--------------|---------------------|---------|----------|-----------------|\n")
            for commit in data['commits']:
                f.write(f"| {commit['sha']} | {commit['author']} | {commit['date']} | {commit['additions']} | {commit['deletions']} | {commit['total_lines']} |\n")
            f.write("\n")
    
    print("README.md atualizado com sucesso!")

if __name__ == "__main__":
    update_readme()
