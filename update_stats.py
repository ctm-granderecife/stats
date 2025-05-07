import os
import json
import requests
from dotenv import load_dotenv
from collections import Counter
from datetime import datetime, timedelta
import sys

# Carregar variáveis do .env
load_dotenv()

# Token do GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAME = "ctm-granderecife"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# Flag para usar dados de exemplo (quando não há token disponível)
USE_SAMPLE_DATA = GITHUB_TOKEN is None

# Arquivo JSON para armazenar os dados
DATA_FILE = "stats_data.json"

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

# Função para gerar dados de exemplo quando não há token disponível
def get_sample_data():
    # Dados de exemplo para top usuários
    top_users = [
        {'name': 'Luan Araújo', 'commits': 18},
        {'name': 'peregrinno', 'commits': 17},
        {'name': 'Grande Recife - CTM', 'commits': 6},
        {'name': 'felipeserpa01', 'commits': 5},
        {'name': 'rafaeldlcs', 'commits': 5},
        {'name': 'danilodct', 'commits': 4},
        {'name': 'Danilo Torres', 'commits': 4},
        {'name': 'Adelson', 'commits': 4},
        {'name': 'NataliaBento', 'commits': 2}
    ]
    
    # Dados de exemplo para repositórios
    repositories = {
        'sim-ui': {
            'commits': [
                {'sha': 'a4d4725', 'author': 'Luan Araújo', 'date': '2025-04-01T17:38:51Z', 'additions': 2718, 'deletions': 2757, 'total_lines': 5475},
                {'sha': '5dbeead', 'author': 'Luan Araújo', 'date': '2025-04-01T17:38:20Z', 'additions': 2718, 'deletions': 2757, 'total_lines': 5475},
                {'sha': 'c7cb2b1', 'author': 'Luan Araújo', 'date': '2025-04-01T17:37:41Z', 'additions': 2718, 'deletions': 2757, 'total_lines': 5475},
                {'sha': '62e5113', 'author': 'peregrinno', 'date': '2025-04-01T17:36:17Z', 'additions': 9, 'deletions': 473, 'total_lines': 482},
                {'sha': 'a495fa8', 'author': 'peregrinno', 'date': '2025-04-01T17:33:03Z', 'additions': 54, 'deletions': 7, 'total_lines': 61}
            ],
            'total_additions': 8217,
            'total_deletions': 8751,
            'total_lines': 16968
        },
        'vem-diag': {
            'commits': [
                {'sha': '0d6f7bc', 'author': 'peregrinno', 'date': '2025-04-01T13:02:10Z', 'additions': 73, 'deletions': 99, 'total_lines': 172},
                {'sha': '61626d5', 'author': 'peregrinno', 'date': '2025-04-01T12:58:13Z', 'additions': 4, 'deletions': 1, 'total_lines': 5},
                {'sha': '03305c1', 'author': 'peregrinno', 'date': '2025-04-01T12:55:48Z', 'additions': 29318, 'deletions': 0, 'total_lines': 29318}
            ],
            'total_additions': 29395,
            'total_deletions': 100,
            'total_lines': 29495
        },
        'itinerarios': {
            'commits': [
                {'sha': '2c6114e', 'author': 'felipeserpa01', 'date': '2025-03-26T16:34:18Z', 'additions': 10, 'deletions': 7, 'total_lines': 17},
                {'sha': 'a44bbcf', 'author': 'felipeserpa01', 'date': '2025-03-26T16:12:28Z', 'additions': 2465, 'deletions': 2417, 'total_lines': 4882},
                {'sha': '70b4c11', 'author': 'felipeserpa01', 'date': '2025-03-19T19:36:14Z', 'additions': 30787, 'deletions': 65, 'total_lines': 30852},
                {'sha': 'd0d4942', 'author': 'felipeserpa01', 'date': '2025-02-03T18:04:48Z', 'additions': 545, 'deletions': 255, 'total_lines': 800},
                {'sha': '6b3e5e2', 'author': 'felipeserpa01', 'date': '2025-01-08T18:01:45Z', 'additions': 914, 'deletions': 15, 'total_lines': 929}
            ],
            'total_additions': 34721,
            'total_deletions': 2759,
            'total_lines': 37480
        }
    }
    
    return {
        'top_users': top_users,
        'repositories': repositories,
        'last_updated': datetime.now().isoformat()
    }

# Função para coletar os dados estatísticos
def collect_stats_data():
    # Se não tiver token, usa dados de exemplo
    if USE_SAMPLE_DATA:
        print("Aviso: Token GitHub não encontrado. Usando dados de exemplo.")
        return get_sample_data()
    
    try:
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
    except Exception as e:
        print(f"Erro ao coletar dados: {e}")
        print("Usando dados de exemplo como fallback.")
        return get_sample_data()
        
    # Ordena o ranking dos usuários
    top_10_users = commit_authors.most_common(10)
    
    # Se estiver usando dados de exemplo
    if USE_SAMPLE_DATA:
        stats_data = get_sample_data()
    else:
        # Prepara os dados para salvar em JSON
        stats_data = {
            'top_users': [{'name': user, 'commits': commits} for user, commits in top_10_users],
            'repositories': repo_data,
            'last_updated': datetime.now().isoformat()
        }
    
    # Salva os dados em um arquivo JSON
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)
    
    return stats_data

# Função para gerar o HTML a partir dos dados
def generate_html(stats_data):
    top_users = stats_data['top_users']
    repositories = stats_data['repositories']
    last_updated = stats_data['last_updated']
    
    # Início do HTML
    html = f'''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estatísticas do Grande Recife</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo {{
            max-width: 600px;
            margin-bottom: 20px;
        }}
        h1 {{
            color: #0056b3;
            text-align: center;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #0056b3;
            border-bottom: 2px solid #0056b3;
            padding-bottom: 10px;
            margin-top: 40px;
        }}
        h3 {{
            color: #0077cc;
            margin-top: 30px;
        }}
        .stats-container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 30px;
        }}
        .user-list {{
            list-style-type: none;
            padding: 0;
        }}
        .user-list li {{
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .repo-stats {{
            margin-bottom: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 14px;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 14px;
            color: #666;
        }}
        .last-updated {{
            text-align: right;
            font-size: 12px;
            color: #666;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <header>
        <img src="https://raw.githubusercontent.com/ctm-granderecife/cdn-imgs/refs/heads/main/commons/logo_grande_recife.svg" alt="Logo do Grande Recife" class="logo">
    </header>

    <h1>Dados Estatísticos de Desenvolvimento do Grande Recife</h1>
    
    <div class="last-updated">Última atualização: {datetime.fromisoformat(last_updated).strftime('%d/%m/%Y %H:%M:%S')}</div>

    <div class="stats-container">
        <h2>Top 10 Usuários da Última Semana</h2>
        <ul class="user-list">
'''
    
    # Adiciona os top usuários
    for user in top_users:
        html += f'            <li>{user["name"]}: {user["commits"]} commits</li>\n'
    
    html += '''
        </ul>
    </div>
'''
    
    # Adiciona as estatísticas de cada repositório
    for repo_name, repo_data in repositories.items():
        html += f'''
    <div class="stats-container">
        <h3>{repo_name}</h3>
        <div class="repo-stats">
            <p><strong>Total de Linhas Alteradas</strong>: {repo_data['total_lines']} (Adições: {repo_data['total_additions']} | Deleções: {repo_data['total_deletions']})</p>
        </div>
        <table>
            <thead>
                <tr>
                    <th>SHA</th>
                    <th>Autor</th>
                    <th>Data</th>
                    <th>Adições</th>
                    <th>Deleções</th>
                    <th>Total de Linhas</th>
                </tr>
            </thead>
            <tbody>
'''
        
        # Adiciona os commits do repositório
        for commit in repo_data['commits']:
            html += f'''
                <tr>
                    <td>{commit['sha']}</td>
                    <td>{commit['author']}</td>
                    <td>{commit['date']}</td>
                    <td>{commit['additions']}</td>
                    <td>{commit['deletions']}</td>
                    <td>{commit['total_lines']}</td>
                </tr>
'''
        
        html += '''
            </tbody>
        </table>
    </div>
'''
    
    # Finaliza o HTML
    html += '''
    <div class="footer">
        <p>© Grande Recife - CTM</p>
    </div>
</body>
</html>
'''
    
    # Salva o HTML em um arquivo
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("index.html atualizado com sucesso!")

def update_stats():
    # Coleta os dados
    stats_data = collect_stats_data()
    
    # Gera o HTML
    generate_html(stats_data)
    
    print("Estatísticas atualizadas com sucesso!")
    print(f"O arquivo index.html foi atualizado.")
    print(f"Os dados também foram salvos em {DATA_FILE} para referência futura.")
    
    # Se estiver usando dados de exemplo, avisa o usuário
    if USE_SAMPLE_DATA:
        print("\nNota: Foram usados dados de exemplo pois o token do GitHub não foi encontrado.")
        print("Para usar dados reais, crie um arquivo .env com seu token do GitHub:")
        print("GITHUB_TOKEN=seu_token_aqui")

if __name__ == "__main__":
    try:
        update_stats()
    except Exception as e:
        print(f"Erro ao atualizar estatísticas: {e}")
        sys.exit(1)
