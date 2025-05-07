import os
import json
import requests
from dotenv import load_dotenv
from collections import Counter
from datetime import datetime, timedelta, timezone
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
    
    try:
        response = requests.get(repos_url, headers=HEADERS)
        response.raise_for_status()
        repos = response.json()
        return [repo['name'] for repo in repos]
    except Exception as e:
        print(f"Erro ao obter repositórios: {str(e)}")
        return []

# Função para pegar commits de um repositório
def get_commits(repo):
    commits_url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/commits?per_page=5"  # Limitar aos 5 commits mais recentes
    
    try:
        response = requests.get(commits_url, headers=HEADERS)
        response.raise_for_status()
        commits = response.json()
        return commits
    except Exception as e:
        print(f"Erro ao obter commits para {repo}: {str(e)}")
        return []

# Função para pegar as estatísticas de um commit
def get_commit_stats(repo, sha):
    commit_url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/commits/{sha}"
    
    try:
        response = requests.get(commit_url, headers=HEADERS)
        response.raise_for_status()
        commit_data = response.json()
        
        # Extrair informações relevantes
        try:
            author = commit_data['commit']['author']['name']
        except:
            author = "Unknown"
            
        try:
            date = commit_data['commit']['author']['date']
        except:
            date = "Unknown"
        
        # Obter estatísticas de adições e deleções
        try:
            additions = commit_data['stats']['additions']
            deletions = commit_data['stats']['deletions']
            total_lines = additions + deletions
        except:
            additions = 0
            deletions = 0
            total_lines = 0
        
        return {
            'sha': sha[:7],  # Apenas os primeiros 7 caracteres do SHA
            'author': author,
            'date': date,
            'additions': additions,
            'deletions': deletions,
            'total_lines': total_lines
        }
    except Exception as e:
        print(f"Erro ao obter estatísticas para commit {sha[:7]}: {str(e)}")
        # Configura o fuso horário para UTC-3 (Brasília)
        fuso_horario_brasil = timezone(timedelta(hours=-3))
        data_hora_brasil = datetime.now(fuso_horario_brasil)
        
        return {
            'sha': sha[:7],
            'author': 'Unknown',
            'date': data_hora_brasil.isoformat(),
            'additions': 0,
            'deletions': 0,
            'total_lines': 0
        }

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
    
    # Configura o fuso horário para UTC-3 (Brasília)
    fuso_horario_brasil = timezone(timedelta(hours=-3))
    data_hora_brasil = datetime.now(fuso_horario_brasil)
    
    return {
        'top_users': top_users,
        'repositories': repositories,
        'last_updated': data_hora_brasil.isoformat()
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
                        commit_stats = get_commit_stats(repo, sha)
                        additions = commit_stats['additions']
                        deletions = commit_stats['deletions']
                        total_lines += commit_stats['total_lines']
                        
                        # Coleta os dados
                        commit_authors[author] += 1
                        repo_commit_data.append({
                            'sha': sha[:7],  # Primeiros 7 caracteres do SHA
                            'author': author,
                            'date': date,
                            'additions': additions,
                            'deletions': deletions,
                            'total_lines': commit_stats['total_lines']
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
        # Configura o fuso horário para UTC-3 (Brasília)
        fuso_horario_brasil = timezone(timedelta(hours=-3))
        data_hora_brasil = datetime.now(fuso_horario_brasil)
        
        stats_data = {
            'top_users': [{'name': user, 'commits': commits} for user, commits in top_10_users],
            'repositories': repo_data,
            'last_updated': data_hora_brasil.isoformat()
        }
    
    # Salva os dados em um arquivo JSON
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)
    
    return stats_data

# Comentário: O HTML agora é estático e carrega os dados do JSON dinamicamente
# Não é mais necessário gerar o HTML a cada execução

def update_stats():
    # Coleta os dados
    stats_data = collect_stats_data()
    
    # Salva apenas o JSON (o HTML carrega os dados dinamicamente)
    print(f"Os dados foram salvos em {DATA_FILE} para referência futura.")
    print("Estatísticas atualizadas com sucesso!")
    
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
